from time import sleep

import pytest
import requests
from fastapi.testclient import TestClient
from schemas.datasets import DatasetFormat, DatasetResponse


# First test waits and polls up to 10 times for the real backend to be up.
def test_health_ok(local_client: TestClient):
    attempt = 0
    while attempt < 10:
        response = local_client.get("/health/")
        
        if response.status_code == 200:
            assert True
            return
        attempt += 1
        sleep(1)
    pytest.fail("API did not respond with 200 OK within 10 attempts")

def test_upload_data_launch_experiement(local_client: TestClient, dialog_dataset):
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

    create_experiment_response = local_client.post("/experiments", headers=headers, json=payload
    )
    assert create_experiment_response.status_code == 201