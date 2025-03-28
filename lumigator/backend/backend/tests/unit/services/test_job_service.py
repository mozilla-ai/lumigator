import json
from unittest.mock import MagicMock, patch
from uuid import UUID

import loguru
import pytest
import requests_mock
from lumigator_schemas.datasets import DatasetFormat
from lumigator_schemas.jobs import (
    JobCreate,
    JobInferenceConfig,
    JobType,
)
from lumigator_schemas.secrets import SecretUploadRequest
from ray.dashboard.modules.job.common import JobStatus
from ray.job_submission import JobSubmissionClient

from backend.ray_submit.submission import RayJobEntrypoint
from backend.services.exceptions.job_exceptions import JobNotFoundError, JobUpstreamError, JobValidationError
from backend.services.exceptions.secret_exceptions import SecretNotFoundError
from backend.services.jobs import JobService, job_settings_map
from backend.settings import settings
from backend.tests.conftest import TEST_SEQ2SEQ_MODEL


def test_set_null_inference_job_params(job_record, job_service):
    request = JobCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        job_config=JobInferenceConfig(job_type=JobType.INFERENCE, model=TEST_SEQ2SEQ_MODEL, provider="hf"),
        dataset="cced289c-f869-4af1-9195-1d58e32d1cc1",
    )

    # Patch the response we'd get from the dataset service since we don't actually have a dataset
    with patch(
        "backend.services.datasets.DatasetService.get_dataset_s3_path",
        return_value="s3://bucket/path/to/dataset",
    ):
        dataset_s3_path = job_service._dataset_service.get_dataset_s3_path(request.dataset)
        job_config = job_settings_map[JobType.INFERENCE].generate_config(
            request, request.dataset, dataset_s3_path, "s3://lumigator-storage/path/to/results.json"
        )
        assert job_config.job.max_samples == -1


def test_set_explicit_inference_job_params(job_record, job_service):
    request = JobCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        max_samples=10,
        job_config=JobInferenceConfig(job_type=JobType.INFERENCE, model=TEST_SEQ2SEQ_MODEL, provider="hf"),
        dataset="cced289c-f869-4af1-9195-1d58e32d1cc1",
    )

    # Patch the response we'd get from the dataset service since we don't actually have a dataset
    with patch(
        "backend.services.datasets.DatasetService.get_dataset_s3_path",
        return_value="s3://bucket/path/to/dataset",
    ):
        dataset_s3_path = job_service._dataset_service.get_dataset_s3_path(request.dataset)
        job_config = job_settings_map[JobType.INFERENCE].generate_config(
            request, request.dataset, dataset_s3_path, "s3://lumigator-storage/path/to/results.json"
        )
        assert job_config.job.max_samples == 10


@pytest.mark.parametrize(
    ["model", "provider", "input_base_url", "returned_base_url"],
    [
        # generic HF model loaded locally
        ("facebook/bart-large-cnn", "hf", None, None),
        # vLLM served model (with HF model name specified to be passed as "model")
        (
            "mistralai/Mistral-7B-Instruct-v0.3",
            "hf",
            "http://localhost:8000/v1/chat/completions",
            "http://localhost:8000/v1/chat/completions",
        ),
        # llamafile served model (with custom model name)
        (
            "mistralai/Mistral-7B-Instruct-v0.2",
            "openai",
            "http://localhost:8000/v1/chat/completions",
            "http://localhost:8000/v1/chat/completions",
        ),
        # openai model (from API)
        ("gpt-4-turbo", "openai", "https://api.openai.com/v1", settings.OAI_API_URL),
        # mistral model (from API)
        ("ministral-8b-latest", "mistral", "https://api.mistral.ai/v1", settings.MISTRAL_API_URL),
        # deepseek model (from API)
        ("deepseek-chat", "deepseek", "https://api.deepseek.com/v1", settings.DEEPSEEK_API_URL),
    ],
)
def test_set_model(job_service, model, provider, input_base_url, returned_base_url):
    request = JobCreate(
        name="test_run",
        description="Test run to verify how model URL is set",
        job_config=JobInferenceConfig(
            job_type=JobType.INFERENCE,
            model=model,
            provider=provider,
            base_url=input_base_url,
        ),
        dataset="d34dd34d-d34d-d34d-d34d-d34dd34dd34d",
    )
    base_url = request.job_config.base_url
    assert base_url == returned_base_url


def test_check_api_key_not_in_job_creation_config(
    job_service, secret_service, dataset_service, valid_upload_file, dependency_overrides_fakes
):
    key_name = "MISTRAL_KEY"
    key_value = "12345"

    def submit_ray_job_fixture_side_effect(_: JobSubmissionClient, entrypoint: RayJobEntrypoint):
        parsed_args = json.loads(entrypoint.config.args["--config"])
        if parsed_args.get("api_key") == key_value:
            raise Exception(f"Passed API key <{parsed_args['api_key']}> in config")

    test_dataset = dataset_service.upload_dataset(valid_upload_file, DatasetFormat.JOB)
    secret_service.upload_secret(key_name, SecretUploadRequest(value=key_value, description="Mistral key"))
    request = JobCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        job_config=JobInferenceConfig(
            job_type=JobType.INFERENCE, model=TEST_SEQ2SEQ_MODEL, provider="hf", secret_key_name=key_name
        ),
        dataset=str(test_dataset.id),
    )
    with patch(
        "backend.services.jobs.submit_ray_job",
        side_effect=submit_ray_job_fixture_side_effect,
    ):
        job_service.create_job(request)


def test_missing_api_key_in_job_creation(
    job_service, secret_service, dataset_service, valid_upload_file, dependency_overrides_fakes
):
    key_name = "MISTRAL_KEY"

    test_dataset = dataset_service.upload_dataset(valid_upload_file, DatasetFormat.JOB)
    request = JobCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        job_config=JobInferenceConfig(
            job_type=JobType.INFERENCE, model=TEST_SEQ2SEQ_MODEL, provider="hf", secret_key_name=key_name
        ),
        dataset=str(test_dataset.id),
    )
    with patch(
        "backend.services.jobs.submit_ray_job",
        return_value=None,
    ):
        with pytest.raises(JobValidationError):
            job_service.create_job(request)


def test_get_upstream_job_status_success(job_service: JobService, valid_job_id: UUID):
    # Mock the Ray client's get_job_status method to return a mock response
    mock_job_status = MagicMock()
    mock_job_status.value = "SUCCEEDED"
    job_service._ray_client.get_job_status = MagicMock(return_value=mock_job_status)
    status = job_service.get_upstream_job_status(valid_job_id)
    assert status == "succeeded"


def test_get_upstream_job_status_job_not_found(job_service: JobService, valid_job_id: UUID):
    """Test for job not found error (404)."""
    # This is the current response from the Ray client when a job is not found.
    job_service._ray_client.get_job_status.side_effect = RuntimeError(
        "Request failed with status code 404: Job not found."
    )

    with pytest.raises(JobNotFoundError):
        job_service.get_upstream_job_status(valid_job_id)


def test_get_upstream_job_status_other_error(job_service: JobService, valid_job_id: UUID):
    """Test for any other error."""
    job_service._ray_client.get_job_status.side_effect = RuntimeError("Some other error occurred")

    with pytest.raises(JobUpstreamError):
        job_service.get_upstream_job_status(valid_job_id)
