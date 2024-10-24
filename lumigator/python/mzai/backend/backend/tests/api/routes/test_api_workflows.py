from time import sleep

import pytest
import requests
from fastapi.testclient import TestClient
from schemas.datasets import DatasetFormat, DatasetResponse

from backend.main import app


@app.on_event("startup")
def test_health_ok(local_client: TestClient):
        response = local_client.get("/health/")
        assert response.status_code == 200

def test_upload_data_launch_job(local_client: TestClient, dialog_dataset):
    response = local_client.get("/health")
    assert response.status_code == 200

    create_response = local_client.post("/datasets",
            data={},
            files={"dataset": dialog_dataset, "format": (None, DatasetFormat.EXPERIMENT.value)},
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

    create_experiment_response = local_client.post("/jobs/evaluate", headers=headers, json=payload
    )
    assert create_experiment_response.status_code == 201


def test_experiment_non_existing(local_client: TestClient):
    non_existing_id = "71aaf905-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/experiments/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Job {non_existing_id} not found."


def test_job_non_existing(local_client: TestClient):
    non_existing_id = "71aaf905-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/jobs/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Job {non_existing_id} not found."