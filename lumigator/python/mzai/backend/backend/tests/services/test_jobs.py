import pytest
from backend.services import jobs
from schemas.jobs import (
    JobCreate,

)
from backend.services.datasets import DatasetService
from backend.records.jobs import  JobRecord

def test_get_infer_config_params(job_repository):

    request = JobCreate(name="test_run_hugging_face",description="Test run for Huggingface model",model="Test run for Huggingface model",dataset= "cced289c-f869-4af1-9195-1d58e32d1cc1" )
    record = JobRecord().id
    config_params = {"name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": "hf://facebook/bart-large-cnn",
        "dataset": "cced289c-f869-4af1-9195-1d58e32d1cc1",}
    filled_template = jobs.JobService().get_config_params(request,record,config_params,DatasetService,"str","hf://facebook/bart-large-cnn")
