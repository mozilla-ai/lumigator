from unittest.mock import patch

import pytest
from lumigator_schemas.jobs import (
    JobCreate,
    JobInferenceConfig,
    JobType,
)
from lumigator_schemas.tasks import TaskType
from pydantic import ValidationError

from backend.services.exceptions.job_exceptions import JobValidationError
from backend.settings import settings


def test_set_null_inference_job_params(job_record, job_service):
    request = JobCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        job_config=JobInferenceConfig(job_type=JobType.INFERENCE, model="facebook/bart-large-cnn", provider="hf"),
        dataset="cced289c-f869-4af1-9195-1d58e32d1cc1",
    )

    # Patch the response we'd get from the dataset service since we don't actually have a dataset
    with patch(
        "backend.services.datasets.DatasetService.get_dataset_s3_path",
        return_value="s3://bucket/path/to/dataset",
    ):
        dataset_s3_path = job_service._dataset_service.get_dataset_s3_path(request.dataset)
        job_config = job_service.job_settings[JobType.INFERENCE].generate_config(
            request, request.dataset, dataset_s3_path, job_service.storage_path
        )
        assert job_config.job.max_samples == -1


def test_set_explicit_inference_job_params(job_record, job_service):
    request = JobCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        max_samples=10,
        job_config=JobInferenceConfig(job_type=JobType.INFERENCE, model="facebook/bart-large-cnn", provider="hf"),
        dataset="cced289c-f869-4af1-9195-1d58e32d1cc1",
    )

    # Patch the response we'd get from the dataset service since we don't actually have a dataset
    with patch(
        "backend.services.datasets.DatasetService.get_dataset_s3_path",
        return_value="s3://bucket/path/to/dataset",
    ):
        dataset_s3_path = job_service._dataset_service.get_dataset_s3_path(request.dataset)
        job_config = job_service.job_settings[JobType.INFERENCE].generate_config(
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


def test_invalid_text_generation(job_service):
    with pytest.raises(ValidationError) as excinfo:
        JobCreate(
            name="test_text_generation_run",
            description="Test missing system prompt for text generation",
            job_config=JobInferenceConfig(
                job_type=JobType.INFERENCE,
                model="microsoft/Phi-3-mini-instruct",
                provider="hf",
                task_definition={
                    "task": TaskType.TEXT_GENERATION
                    # Intentionally missing system_prompt
                },
            ),
            dataset="d34dd34d-d34d-d34d-d34d-d34dd34dd34d",
        )

    # Verify the exact error structure from Pydantic
    assert "Field required" in str(excinfo.value)
    assert "system_prompt" in str(excinfo.value)


@pytest.mark.parametrize(
    "task, source_language, target_language, should_pass, error_msg",
    [
        # Valid summarization case - no language fields
        (TaskType.SUMMARIZATION, None, None, True, None),
        # Invalid summarization cases - language fields in task definition
        (
            TaskType.SUMMARIZATION,
            "en",
            None,
            False,
            "Extra inputs are not permitted",
        ),
        (
            TaskType.SUMMARIZATION,
            None,
            "fr",
            False,
            "Extra inputs are not permitted",
        ),
        # Valid translation case - both languages provided
        (TaskType.TRANSLATION, "en", "fr", True, None),
        # Invalid translation cases - missing language fields
        (
            TaskType.TRANSLATION,
            None,
            None,
            False,
            "Field required",
        ),
        (
            TaskType.TRANSLATION,
            "en",
            None,
            False,
            "Field required",
        ),
        (
            TaskType.TRANSLATION,
            None,
            "fr",
            False,
            "Field required",
        ),
    ],
)
def test_inference_config_task_language_pair(task, source_language, target_language, should_pass, error_msg):
    # Base config structure
    config = {
        "job_type": JobType.INFERENCE,
        "model": "gpt-4-turbo",
        "provider": "openai",
        "task_definition": {"task": task},
    }

    # Add language fields to task_definition if provided
    task_def = config["task_definition"]
    if source_language is not None:
        task_def["source_language"] = source_language
    if target_language is not None:
        task_def["target_language"] = target_language

    # Test naming
    name = f"test_{task.value}_{'valid' if should_pass else 'invalid'}"
    description = (
        f"Testing {task.value} task with "
        f"source_lang={source_language or 'None'} "
        f"target_lang={target_language or 'None'}"
    )

    if should_pass:
        # Valid case should create successfully
        JobCreate(
            name=name,
            description=description,
            job_config=JobInferenceConfig(**config),
            dataset="d34dd34d-d34d-d34d-d34d-d34dd34dd34d",
        )
    else:
        # Invalid case should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            JobCreate(
                name=name,
                description=description,
                job_config=JobInferenceConfig(**config),
                dataset="d34dd34d-d34d-d34d-d34d-d34dd34dd34d",
            )
        # Verify expected error message
        assert error_msg in str(exc_info.value)
