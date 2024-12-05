from time import sleep

import pytest
import requests
import time
from fastapi.testclient import TestClient
from lumigator_schemas.datasets import DatasetFormat, DatasetResponse
from lumigator_schemas.experiments import ExperimentResponse
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import JobResponse, JobStatus

from backend.main import app


@app.on_event("startup")
def test_health_ok(local_client: TestClient):
    response = local_client.get("/health/")
    assert response.status_code == 200


def test_upload_data_launch_job(local_client: TestClient, dialog_dataset, simple_eval_template, simple_infer_template, dependency_overrides_services):
    response = local_client.get("/health")
    assert response.status_code == 200

    create_response = local_client.post(
        "/datasets/",
        data={},
        files={"dataset": dialog_dataset, "format": (None, DatasetFormat.JOB.value)},
    )

    print(f'response: {create_response.text}')
    assert create_response.status_code == 201

    created_dataset = DatasetResponse.model_validate(create_response.json())

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    eval_payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": "hf://trl-internal-testing/tiny-random-LlamaForCausalLM",
        "dataset": str(created_dataset.id),
        "config_template": simple_eval_template,
        "max_samples": 10,
        # Investigate!
        # "model_url": "string",
        # "system_prompt": "string",
        # "config_template": "string",
    }

    create_evaluation_job_response = local_client.post(
        "/jobs/evaluate/", headers=headers, json=eval_payload
    )
    assert create_evaluation_job_response.status_code == 201

    create_evaluation_job_response_model = JobResponse.model_validate(create_evaluation_job_response.json())

    succeeded = False
    for i in range (1, 200):
        get_job_response = local_client.get(f'/jobs/{create_evaluation_job_response_model.id}')
        assert get_job_response.status_code == 200
        get_job_response_model = JobResponse.model_validate(get_job_response.json())
        print(f'--> try {i}: {get_job_response_model}')
        if get_job_response_model.status == JobStatus.SUCCEEDED.value:
            succeeded = True
            break
        if get_job_response_model.status == JobStatus.FAILED.value:
            succeeded = False
            break
        time.sleep(1)
    assert succeeded

    infer_payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": "hf://trl-internal-testing/tiny-random-LlamaForCausalLM",
        "dataset": str(created_dataset.id),
        "config_template": simple_infer_template,
        "max_samples": 10,
        # Investigate!
        # "model_url": "string",
        # "system_prompt": "string",
        # "config_template": "string",
    }

    create_inference_job_response = local_client.post(
        "/jobs/inference/", headers=headers, json=infer_payload
    )
    assert create_inference_job_response.status_code == 201

    create_inference_job_response_model = JobResponse.model_validate(create_inference_job_response.json())

    succeeded = False
    for i in range (1, 200):
        get_job_response = local_client.get(f'/jobs/{create_inference_job_response_model.id}')
        assert get_job_response.status_code == 200
        get_job_response_model = JobResponse.model_validate(get_job_response.json())
        print(f'--> try {i}: {get_job_response_model}')
        if get_job_response_model.status == JobStatus.SUCCEEDED.value:
            succeeded = True
            break
        if get_job_response_model.status == JobStatus.FAILED.value:
            succeeded = False
            break
        time.sleep(1)
    assert succeeded


def test_full_experiment_launch(local_client: TestClient, dialog_dataset, dependency_overrides_services):
    response = local_client.get("/health")
    assert response.status_code == 200
    create_response = local_client.post(
        "/datasets/",
        data={},
        files={"dataset": dialog_dataset, "format": (None, DatasetFormat.JOB.value)},
    )
    print(f'response: {create_response.text}')
    assert create_response.status_code == 201
    created_dataset = DatasetResponse.model_validate(create_response.json())
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": "hf://trl-internal-testing/tiny-random-LlamaForCausalLM",
        "dataset": str(created_dataset.id),
        "max_samples": 2,
    }

    create_experiments_response = local_client.post("/experiments/", headers=headers, json=payload)
    assert create_experiments_response.status_code == 201

    get_experiments_response = local_client.get("/experiments/")
    get_experiments = ListingResponse[ExperimentResponse].model_validate(
        get_experiments_response.json()
    )
    print(get_experiments)
    assert get_experiments.total > 0

    get_experiment_response = local_client.get(f"/experiments/{get_experiments.items[0].id}")
    assert get_experiment_response.status_code == 200

    succeeded = False
    for i in range (1, 200):
        get_job_response = local_client.get(f'/jobs/{get_experiments.items[0].id}')
        assert get_job_response.status_code == 200
        get_job_response_model = JobResponse.model_validate(get_job_response.json())
        print(f'--> try {i}: {get_job_response_model}')
        if get_job_response_model.status == JobStatus.SUCCEEDED.value:
            succeeded = True
            break
        if get_job_response_model.status == JobStatus.FAILED.value:
            succeeded = False
            break
        time.sleep(1)
    assert succeeded


def test_experiment_non_existing(local_client: TestClient, dependency_overrides_services):
    non_existing_id = "71aaf905-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/experiments/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Job {non_existing_id} not found."


def test_job_non_existing(local_client: TestClient, dependency_overrides_services):
    non_existing_id = "71aaf905-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/jobs/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Job {non_existing_id} not found."
