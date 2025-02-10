from unittest.mock import patch

import pytest
from lumigator_schemas.jobs import (
    JobCreate,
    JobInferenceConfig,
    JobType,
)

from backend.services.jobs import JobService
from backend.settings import settings


def test_set_null_inference_job_params(job_record, job_service):
    request = JobCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        job_config=JobInferenceConfig(
            job_type=JobType.INFERENCE, model="hf://facebook/bart-large-cnn"
        ),
        dataset="cced289c-f869-4af1-9195-1d58e32d1cc1",
    )

    # Patch the response we'd get from the dataset service since we don't actually have a dataset
    with patch(
        "backend.services.datasets.DatasetService.get_dataset_s3_path",
        return_value="s3://bucket/path/to/dataset",
    ):
        dataset_s3_path = job_service._dataset_service.get_dataset_s3_path(request.dataset)
        job_config = job_service.generate_inference_job_config(
            request, request.dataset, dataset_s3_path, job_service.storage_path
        )
        assert job_config.job.max_samples == -1


def test_set_explicit_inference_job_params(job_record, job_service):
    request = JobCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        max_samples=10,
        job_config=JobInferenceConfig(
            job_type=JobType.INFERENCE, model="hf://facebook/bart-large-cnn"
        ),
        dataset="cced289c-f869-4af1-9195-1d58e32d1cc1",
    )

    # Patch the response we'd get from the dataset service since we don't actually have a dataset
    with patch(
        "backend.services.datasets.DatasetService.get_dataset_s3_path",
        return_value="s3://bucket/path/to/dataset",
    ):
        dataset_s3_path = job_service._dataset_service.get_dataset_s3_path(request.dataset)
        job_config = job_service.generate_inference_job_config(
            request, request.dataset, dataset_s3_path, job_service.storage_path
        )
        assert job_config.job.max_samples == 10


@pytest.mark.parametrize(
    ["model", "input_model_url", "returned_model_url"],
    [
        # generic HF model loaded locally
        ("hf://facebook/bart-large-cnn", None, None),
        # vLLM served model (with HF model name specified to be passed as "engine")
        (
            "hf://mistralai/Mistral-7B-Instruct-v0.3",
            "http://localhost:8000/v1/chat/completions",
            "http://localhost:8000/v1/chat/completions",
        ),
        # llamafile served model (with custom model name)
        (
            "llamafile://mistralai/Mistral-7B-Instruct-v0.2",
            "http://localhost:8000/v1/chat/completions",
            "http://localhost:8000/v1/chat/completions",
        ),
    ],
)
def test_set_model(job_service, model, input_model_url, returned_model_url):
    request = JobCreate(
        name="test_run",
        description="Test run to verify how model URL is set",
        job_config=JobInferenceConfig(
            job_type=JobType.INFERENCE,
            model=model,
            model_url=input_model_url,
        ),
        dataset="d34dd34d-d34d-d34d-d34d-d34dd34dd34d",
    )
    model_url = request.model_url
    assert model_url == returned_model_url
