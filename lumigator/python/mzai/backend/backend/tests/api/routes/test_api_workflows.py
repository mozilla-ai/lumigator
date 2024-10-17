import requests
from fastapi import status
from fastapi.testclient import TestClient
from schemas.datasets import DatasetFormat, DatasetResponse


def test_upload_data_launch_experiement(dialog_dataset):
    
    BASE_URL = "http://localhost/api/v1/"
    
    response = requests.get(BASE_URL + "health/")
    assert response.status_code == status.HTTP_200_OK
    
    assert BASE_URL + "health/" == "http://localhost/api/v1/health/"
    create_response = requests.post(
            url=BASE_URL + "datasets/",
            data={},
            files={"dataset": dialog_dataset, "format": (None, DatasetFormat.EXPERIMENT.value)},
        )
    assert BASE_URL + "datasets/" == "http://localhost/api/v1/datasets/"
    assert create_response.status_code == status.HTTP_201_CREATED

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

    create_experiment_response = requests.post(
        BASE_URL + "experiments/", headers=headers, json=payload
    )
    assert BASE_URL + "experiments/" == "http://localhost/api/v1/experiments/"
    assert create_experiment_response.status_code == status.HTTP_201_CREATED