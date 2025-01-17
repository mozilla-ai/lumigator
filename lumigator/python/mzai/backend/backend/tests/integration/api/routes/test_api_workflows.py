import time
from time import sleep
from unittest.mock import patch

import pytest
import requests
from fastapi.testclient import TestClient
from loguru import logger
from lumigator_schemas.datasets import DatasetFormat, DatasetResponse
from lumigator_schemas.experiments import ExperimentResponse
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobLogsResponse,
    JobResponse,
    JobResultDownloadResponse,
    JobStatus,
)

from backend.main import app
from backend.tests.conftest import TEST_CAUSAL_MODEL, TEST_INFER_MODEL


@app.on_event("startup")
def test_health_ok(local_client: TestClient):
    response = local_client.get("/health/")
    assert response.status_code == 200


def test_upload_data_launch_job(
    local_client: TestClient,
    dialog_dataset,
    simple_eval_template,
    simple_infer_template,
    dependency_overrides_services,
):
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
    eval_payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": TEST_CAUSAL_MODEL,
        "dataset": str(created_dataset.id),
        "config_template": simple_eval_template,
        "max_samples": 10,
    }

    create_evaluation_job_response = local_client.post(
        "/jobs/evaluate/", headers=headers, json=eval_payload
    )
    assert create_evaluation_job_response.status_code == 201

    create_evaluation_job_response_model = JobResponse.model_validate(
        create_evaluation_job_response.json()
    )

    succeeded = False
    for _ in range(1, 200):
        get_job_response = local_client.get(f"/jobs/{create_evaluation_job_response_model.id}")
        assert get_job_response.status_code == 200
        get_job_response_model = JobResponse.model_validate(get_job_response.json())
        if get_job_response_model.status == JobStatus.SUCCEEDED.value:
            succeeded = True
            break
        if get_job_response_model.status == JobStatus.FAILED.value:
            succeeded = False
            break
        time.sleep(10)
    assert succeeded

    logs_evaluation_job_response = local_client.get(
        f"/jobs/{create_evaluation_job_response_model.id}/logs"
    )
    logs_evaluation_job_response_model = JobLogsResponse.model_validate(
        logs_evaluation_job_response.json()
    )
    logger.info(f"-- eval logs -- {create_evaluation_job_response_model.id}")
    logger.info(f"#{logs_evaluation_job_response_model.logs}#")

    infer_payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": TEST_INFER_MODEL,
        "dataset": str(created_dataset.id),
        "max_samples": 10,
    }
    create_inference_job_response = local_client.post(
        "/jobs/inference/", headers=headers, json=infer_payload
    )
    assert create_inference_job_response.status_code == 201

    create_inference_job_response_model = JobResponse.model_validate(
        create_inference_job_response.json()
    )

    succeeded = False
    for _ in range(1, 200):
        get_job_response = local_client.get(f"/jobs/{create_inference_job_response_model.id}")
        assert get_job_response.status_code == 200
        get_job_response_model = JobResponse.model_validate(get_job_response.json())
        logs_infer_job_response = local_client.get(
            f"/jobs/{create_inference_job_response_model.id}/logs"
        )
        logs_infer_job_response_model = JobLogsResponse.model_validate(
            logs_infer_job_response.json()
        )
        if get_job_response_model.status == JobStatus.SUCCEEDED.value:
            succeeded = True
            break
        if get_job_response_model.status == JobStatus.FAILED.value:
            succeeded = False
            break
        time.sleep(10)
    assert succeeded

    logs_infer_job_response = local_client.get(
        f"/jobs/{create_inference_job_response_model.id}/logs"
    )
    logs_infer_job_response_model = JobLogsResponse.model_validate(logs_infer_job_response.json())
    logger.info(f"-- infer logs -- {create_inference_job_response_model.id}")
    logger.info(f"#{logs_infer_job_response_model.logs}#")


@pytest.mark.parametrize("unnanotated_dataset", ["dialog_empty_gt_dataset", "dialog_no_gt_dataset"])
def test_upload_data_no_gt_launch_annotation(
    request: pytest.FixtureRequest,
    local_client: TestClient,
    unnanotated_dataset,
    simple_eval_template,
    simple_infer_template,
    dependency_overrides_services,
):
    dataset = request.getfixturevalue(unnanotated_dataset)
    create_response = local_client.post(
        "/datasets/",
        data={},
        files={"dataset": dataset, "format": (None, DatasetFormat.JOB.value)},
    )

    assert create_response.status_code == 201

    created_dataset = DatasetResponse.model_validate(create_response.json())

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    annotation_payload = {
        "name": "test_annotate",
        "description": "Test run for Huggingface model",
        "dataset": str(created_dataset.id),
        "max_samples": 2,
        "task": "summarization",
    }
    create_annotation_job_response = local_client.post(
        "/jobs/annotate/", headers=headers, json=annotation_payload
    )
    assert create_annotation_job_response.status_code == 201

    create_annotation_job_response_model = JobResponse.model_validate(
        create_annotation_job_response.json()
    )

    succeeded = False
    for _ in range(1, 200):
        get_job_response = local_client.get(f"/jobs/{create_annotation_job_response_model.id}")
        assert get_job_response.status_code == 200
        get_job_response_model = JobResponse.model_validate(get_job_response.json())
        if get_job_response_model.status == JobStatus.SUCCEEDED.value:
            succeeded = True
            break
        if get_job_response_model.status == JobStatus.FAILED.value:
            succeeded = False
            break
        time.sleep(10)
    assert succeeded

    logs_annotation_job_response = local_client.get(
        f"/jobs/{create_annotation_job_response_model.id}/logs"
    )
    logger.info(logs_annotation_job_response)
    logs_annotation_job_response_model = JobLogsResponse.model_validate(
        logs_annotation_job_response.json()
    )
    logger.info(f"-- infer logs -- {create_annotation_job_response_model.id}")
    logger.info(f"#{logs_annotation_job_response_model.logs}#")

    logs_annotation_job_results = local_client.get(
        f"/jobs/{create_annotation_job_response_model.id}/result/download"
    )
    logs_annotation_job_results_model = JobResultDownloadResponse.model_validate(
        logs_annotation_job_results.json()
    )
    logger.info(f"Download url: {logs_annotation_job_results_model.download_url}")
    logs_annotation_job_results_url = requests.get(logs_annotation_job_results_model.download_url)
    logs_annotation_job_results_json = logs_annotation_job_results_url.json()
    assert "predictions" not in logs_annotation_job_results_json.keys()
    assert "ground_truth" in logs_annotation_job_results_json.keys()
    logger.info(f"Created results: {logs_annotation_job_results_json}")


def test_full_experiment_launch(
    local_client: TestClient, dialog_dataset, dependency_overrides_services
):
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
        "model": TEST_CAUSAL_MODEL,
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

    succeeded = False
    for _ in range(1, 200):
        get_job_response = local_client.get(f"/jobs/{get_experiments.items[0].id}")
        assert get_job_response.status_code == 200
        get_job_response_model = JobResponse.model_validate(get_job_response.json())
        if get_job_response_model.status == JobStatus.SUCCEEDED.value:
            succeeded = True
            break
        if get_job_response_model.status == JobStatus.FAILED.value:
            succeeded = False
            break
        time.sleep(10)
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


def test_annotation_job(local_client: TestClient, dependency_overrides_services):
    payload = {
        "name": "test_annotate",
        "description": "Test run for Huggingface model",
        "dataset": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "max_samples": 2,
        "task": "summarization",
    }

    post_response = local_client.post(
        "/jobs/annotate/",
        json=payload,
    )

    assert post_response.status_code == 201

    job_id = post_response.json()["id"]
    response = local_client.get(f"/jobs/{job_id}")

    assert response.status_code == 200
