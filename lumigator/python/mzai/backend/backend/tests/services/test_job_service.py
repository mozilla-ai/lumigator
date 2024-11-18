
from lumigator_schemas.jobs import (
    JobInferenceCreate,
)

from backend.services.jobs import JobService


def test_set_null_inference_job_params(job_record,job_service ):
    request = JobInferenceCreate(name="test_run_hugging_face",
                                 description="Test run for Huggingface model",
                                 model="hf://facebook/bart-large-cnn",
                                 dataset="cced289c-f869-4af1-9195-1d58e32d1cc1")
    params = job_service._get_job_params("INFERENCE", job_record,request)
    assert params["max_samples"] == -1

def test_set_explicit_inference_job_params(job_record,job_service ):
    request = JobInferenceCreate(name="test_run_hugging_face",
                                 description="Test run for Huggingface model",
                                 max_samples=10,
                                 model="hf://facebook/bart-large-cnn",
                                 dataset="cced289c-f869-4af1-9195-1d58e32d1cc1")
    params = job_service._get_job_params("INFERENCE", job_record,request)
    assert params["max_samples"] == 10


def test_set_model_hf(job_record,job_service):
    request = JobInferenceCreate(name="test_run_hugging_face",
                                 description="Test run for Huggingface model",
                                 max_samples=10,
                                 model="hf://facebook/bart-large-cnn",
                                 model_url="hf://facebook/bart-large-cnn",
                                 dataset="cced289c-f869-4af1-9195-1d58e32d1cc1")
    model_url = job_service._set_model_type(request)
    assert model_url == "hf://facebook/bart-large-cnn"

def test_set_model_openai(job_record,job_service):
    request = JobInferenceCreate(name="test_run_openai",
                                 description="Test run for OpenAI server",
                                 max_samples=10,
                                 model="oai://gpt-4-turbo",
                                 dataset="cced289c-f869-4af1-9195-1d58e32d1cc1")

    model_url = job_service._set_model_type(request)
    assert model_url == "https://api.openai.com/v1"

def test_set_model_mistral(job_record,job_service):
    request = JobInferenceCreate(name="test_run_mistral",
                                 description="Test run for Mistral server",
                                 max_samples=10,
                                 model="mistral://open-mistral-7b",
                                 dataset="cced289c-f869-4af1-9195-1d58e32d1cc1")

    model_url = job_service._set_model_type(request)
    assert model_url == "https://api.mistral.ai/v1"
