
from lumigator_schemas.jobs import (
    JobInferenceCreate,
)

from backend.services.jobs import JobService


def test_set_null_inference_job_params(job_record,job_service ):
    request = JobInferenceCreate(name="test_run_hugging_face",
                                 description="Test run for Huggingface model",
                                    model="Test run for Huggingface model",
                                 dataset="cced289c-f869-4af1-9195-1d58e32d1cc1")
    params = job_service._get_job_params("INFERENCE", job_record,request)
    assert params["max_samples"] == -1

def test_set_explicit_inference_job_params(job_record,job_service ):
    request = JobInferenceCreate(name="test_run_hugging_face",
                                 description="Test run for Huggingface model",
                                 max_samples=10,
                                    model="Test run for Huggingface model",
                                 dataset="cced289c-f869-4af1-9195-1d58e32d1cc1")
    params = job_service._get_job_params("INFERENCE", job_record,request)
    assert params["max_samples"] == 10
