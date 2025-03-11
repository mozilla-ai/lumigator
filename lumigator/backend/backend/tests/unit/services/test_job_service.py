import json
from unittest.mock import patch

import loguru
import pytest
from lumigator_schemas.datasets import DatasetFormat
from lumigator_schemas.jobs import (
    JobCreate,
    JobInferenceConfig,
    JobType,
)
from lumigator_schemas.secrets import SecretUploadRequest
from ray.job_submission import JobSubmissionClient

from backend.ray_submit.submission import RayJobEntrypoint
from backend.services.exceptions.secret_exceptions import SecretNotFoundError
from backend.services.jobs import job_settings_map
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
            request, request.dataset, dataset_s3_path, job_service.storage_path
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
            request, request.dataset, dataset_s3_path, job_service.storage_path
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
        ("open-mistral-7b", "mistral", "https://api.mistral.ai/v1", settings.MISTRAL_API_URL),
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
        with pytest.raises(SecretNotFoundError):
            job_service.create_job(request)
