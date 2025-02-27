from unittest.mock import patch
from uuid import UUID

import pytest
from lumigator_schemas.jobs import (
    JobCreate,
    JobInferenceConfig,
    JobType,
)
from lumigator_schemas.tasks import TaskType
from pydantic import ValidationError

from backend.services.exceptions.job_exceptions import JobValidationError
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


def test_invalid_text_generation(job_service, job_definition_fixture):
    with pytest.raises(ValueError) as excinfo:
        # Create invalid request without system_prompt
        job_create_request = JobCreate(
            name="test_text_generation_run",
            description="Test missing system prompt for text generation",
            job_config=JobInferenceConfig(
                job_type=JobType.INFERENCE,
                model="microsoft/Phi-3-mini-instruct",
                provider="hf",
                task_definition={"task": TaskType.TEXT_GENERATION},
                # system_prompt left out intentionally
            ),
            dataset="d34dd34d-d34d-d34d-d34d-d34dd34dd34d",
        )

        job_definition_fixture.generate_config(
            job_create_request,
            record_id=UUID("d34dd34d-d34d-d34d-d34d-d34dd34dd34d"),
            dataset_path="s3://lumigator-storage/datasets/d34dd34d-d34d-d34d-d34d-d34dd34dd34d/test.csv",
            storage_path="s3://lumigator-storage/jobs/results/",
        )

    # Verify exact error message
    assert "system_prompt required for task=`text-generation`" in str(excinfo.value)
    assert "Received: None" in str(excinfo.value)
