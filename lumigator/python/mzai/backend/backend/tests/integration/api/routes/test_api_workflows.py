from time import sleep

import pytest
import requests
from fastapi.testclient import TestClient
from lumigator_schemas.datasets import DatasetFormat, DatasetResponse
from lumigator_schemas.experiments import ExperimentResponse
from lumigator_schemas.extras import ListingResponse

from backend.main import app


@app.on_event("startup")
def test_health_ok(local_client: TestClient):
    response = local_client.get("/health/")
    assert response.status_code == 200


# int test (ray, localstack)
def test_upload_data_launch_job(local_client: TestClient, dialog_dataset):
    response = local_client.get("/health")
    assert response.status_code == 200

    create_response = local_client.post(
        "/datasets/",
        data={},
        files={"dataset": dialog_dataset, "format": (None, DatasetFormat.JOB.value)},
    )

    assert create_response.status_code == 201

    created_dataset = DatasetResponse.model_validate(create_response.json())
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": "hf://facebook/bart-large-cnn",
        "dataset": str(created_dataset.id),
        "max_samples": 10,
        "model_url": "string",
        "system_prompt": "string",
        "config_template": "string",
    }

    create_evaluation_job_response = local_client.post(
        "/jobs/evaluate/", headers=headers, json=payload
    )
    assert create_evaluation_job_response.status_code == 201

    create_inference_job_response = local_client.post(
        "/jobs/inference/", headers=headers, json=payload
    )
    assert create_inference_job_response.status_code == 201


# int test (ray, localstack)
def test_full_experiment_launch(local_client: TestClient, dialog_dataset):
    response = local_client.get("/health")
    assert response.status_code == 200
    create_response = local_client.post(
        "/datasets/",
        data={},
        files={"dataset": dialog_dataset, "format": (None, DatasetFormat.JOB.value)},
    )
    assert create_response.status_code == 201
    created_dataset = DatasetResponse.model_validate(create_response.json())
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": "hf://facebook/bart-large-cnn",
        "dataset": str(created_dataset.id),
        "max_samples": 2,
    }

    create_experiments_response = local_client.post("/experiments/", headers=headers, json=payload)
    assert create_experiments_response.status_code == 201

    get_experiments_response = local_client.get("/experiments/")
    get_experiments = ListingResponse[ExperimentResponse].model_validate(
        get_experiments_response.json()
    )
    assert get_experiments.total > 0

    get_experiment_response = local_client.get(f"/experiments/{get_experiments.items[0].id}")
    assert get_experiment_response.status_code == 200


# int test (ray)
def test_experiment_non_existing(local_client: TestClient):
    non_existing_id = "71aaf905-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/experiments/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Job {non_existing_id} not found."


# int test (ray)
def test_job_non_existing(local_client: TestClient):
    non_existing_id = "71aaf905-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/jobs/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Job {non_existing_id} not found."
