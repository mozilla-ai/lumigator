from time import sleep

import pytest
import requests
from fastapi.testclient import TestClient
from lumigator_schemas.datasets import DatasetFormat, DatasetResponse
from lumigator_schemas.jobs import JobCreate, InferenceJobConfig, DatasetConfig

from backend.main import app


@app.on_event("startup")
def test_health_ok(local_client: TestClient):
    response = local_client.get("/health/")
    assert response.status_code == 200


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


def test_upload_data_launch_job_alt(local_client: TestClient, dialog_dataset):
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




            job_params = {
                "job_id": record.id,
                "job_name": request.name,
                "model_path": request.model,
                "dataset_path": dataset_s3_path,
                "max_samples": request.max_samples,
                "storage_path": self.storage_path,
                "model_url": model_url,
                "system_prompt": request.system_prompt,
                "output_field": request.output_field,
                "max_tokens": request.max_tokens,
                "frequency_penalty": request.frequency_penalty,
                "temperature": request.temperature,
                "top_p": request.top_p,
            }


causal_infer_template = """{{
    "name": "{job_name}/{job_id}",
    "model": {{ "path": "{model_path}" }},
    "dataset": {{ "path": "{dataset_path}" }},
}}"""


oai_infer_template = """{{
    "name": "{job_name}/{job_id}",
    "dataset": {{ "path": "{dataset_path}" }},
    "job": {{
    }},
    "inference_server": {{
        "base_url": "{model_url}",
        "engine": "{model_path}",
        "system_prompt": "{system_prompt}",
        "max_retries": 3
    }},
    "params": {{
        "max_tokens": {max_tokens},
        "frequency_penalty": {frequency_penalty},
        "temperature": {temperature},
        "top_p": {top_p}
    }}
}}"""



    specific_payload = InferenceJobConfig(
        name="test_run_hugging_face" f"{job_name}/{job_id}"
        dataset=DatasetConfig(
            path=str(created_dataset.id) dataset_s3_path
        ),
        job=JobConfig(
            max_samples=10,
            output_field="prediction",
            enable_tqdm=True,
        ),
        inference_server=InferenceServerConfig(
            "model_url": "string",
            "model": "hf://facebook/bart-large-cnn",
            engine: str
            "system_prompt": "string",
            system_prompt: str | None
            max_retries=3
        ),
        params=SamplingParameters(
            max_tokens=1024,
            frequency_penalty=0.0,
            temperature=1.0,
            top_p=1.0,
        )
    )
    payload = JobCreate(
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
    )

    create_inference_job_response = local_client.post(
        "/jobs/inference/", headers=headers, json=payload.model_dump_json()
    )
    assert create_inference_job_response.status_code == 201


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