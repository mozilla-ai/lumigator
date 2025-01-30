import json
import logging
import time
from uuid import UUID

import pytest
import requests
from fastapi.testclient import TestClient
from inference.schemas import InferenceJobOutput
from loguru import logger
from lumigator_schemas.datasets import DatasetFormat, DatasetResponse
from lumigator_schemas.experiments import ExperimentResponse
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    Job,
    JobLogsResponse,
    JobResponse,
    JobResultDownloadResponse,
    JobStatus,
)

from backend.main import app
from backend.tests.conftest import (
    TEST_CAUSAL_MODEL,
    wait_for_experiment,
    wait_for_job,
)


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

    logger.info("Running test...")

    create_response = local_client.post(
        "/datasets/",
        data={},
        files={"dataset": dialog_dataset, "format": (None, DatasetFormat.JOB.value)},
    )

    assert create_response.status_code == 201

    created_dataset = DatasetResponse.model_validate(create_response.json())

    get_ds_response = local_client.get("/datasets/")
    assert get_ds_response.status_code == 200
    get_ds = ListingResponse[DatasetResponse].model_validate(get_ds_response.json())

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    infer_payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": TEST_CAUSAL_MODEL,
        "dataset": str(created_dataset.id),
        "max_samples": 10,
        "config_template": simple_infer_template,
        "output_field": "predictions",
        "store_to_dataset": True,
    }
    create_inference_job_response = local_client.post(
        "/jobs/inference/", headers=headers, json=infer_payload
    )
    assert create_inference_job_response.status_code == 201

    create_inference_job_response_model = JobResponse.model_validate(
        create_inference_job_response.json()
    )

    wait_for_job(local_client, create_inference_job_response_model.id)

    logs_infer_job_response = local_client.get(
        f"/jobs/{create_inference_job_response_model.id}/logs"
    )
    logs_infer_job_response_model = JobLogsResponse.model_validate(logs_infer_job_response.json())
    logger.info(f"-- infer logs -- {create_inference_job_response_model.id}")
    logger.info(f"#{logs_infer_job_response_model.logs}#")

    # retrieve the DS for the infer job...
    output_infer_job_response = local_client.get(
        f"/jobs/{create_inference_job_response_model.id}/dataset"
    )
    output_infer_job_response_model = DatasetResponse.model_validate(
        output_infer_job_response.json()
    )
    assert output_infer_job_response_model is not None

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    eval_payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": TEST_CAUSAL_MODEL,
        "dataset": str(output_infer_job_response_model.id),
        "config_template": simple_eval_template,
        "max_samples": 10,
    }

    create_evaluation_job_response = local_client.post(
        "/jobs/eval_lite/", headers=headers, json=eval_payload
    )
    assert create_evaluation_job_response.status_code == 201

    create_evaluation_job_response_model = JobResponse.model_validate(
        create_evaluation_job_response.json()
    )

    assert wait_for_job(local_client, create_evaluation_job_response_model.id)

    logs_evaluation_job_response = local_client.get(
        f"/jobs/{create_evaluation_job_response_model.id}/logs"
    )
    logs_evaluation_job_response_model = JobLogsResponse.model_validate(
        logs_evaluation_job_response.json()
    )
    logger.info(f"-- eval logs -- {create_evaluation_job_response_model.id}")
    logger.info(f"#{logs_evaluation_job_response_model.logs}#")

    get_ds_after_response = local_client.get("/datasets/")
    assert get_ds_after_response.status_code == 200
    get_ds_after = ListingResponse[DatasetResponse].model_validate(get_ds_after_response.json())
    assert get_ds_after.total == get_ds.total + 1


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

    assert wait_for_job(local_client, create_annotation_job_response_model.id)

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
    logs_annotation_job_output = InferenceJobOutput.model_validate(
        logs_annotation_job_results_url.json()
    )
    assert logs_annotation_job_output.predictions is None
    assert logs_annotation_job_output.ground_truth is not None
    logger.info(f"Created results: {logs_annotation_job_output}")


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
        "name": "test_experiment",
        "description": "Test experiment for Huggingface models",
    }

    get_ds_response = local_client.get("/datasets/")
    assert get_ds_response.status_code == 200
    get_ds = ListingResponse[DatasetResponse].model_validate(get_ds_response.json())

    create_experiments_id_response = local_client.post(
        "/experiments/new/", headers=headers, json=payload
    )
    assert create_experiments_id_response.status_code == 201
    experiment_id = create_experiments_id_response.json()["id"]

    # run a workflow for that experiment
    payload = {
        "name": "test_run_hugging_face",
        "description": "Test workflow for Huggingface model",
        "model": TEST_CAUSAL_MODEL,
        "dataset": str(created_dataset.id),
        "experiment_id": experiment_id,
        "max_samples": 2,
    }
    create_workflow_response = local_client.post("/workflows/", headers=headers, json=payload)
    assert create_workflow_response.status_code == 201

    get_experiments_response = local_client.get("/experiments/new/all")
    assert get_experiments_response.status_code == 200
    get_experiments = ListingResponse[ExperimentResponse].model_validate(
        get_experiments_response.json()
    )
    assert experiment_id in [str(exp.id) for exp in get_experiments.items]
    experiment_id = get_experiments.items[0].id

    get_experiment_response = local_client.get(f"/experiments/new/{experiment_id}")
    logger.info(f"--> {get_experiment_response.text}")
    assert get_experiment_response.status_code == 200
    # response
    get_jobs_per_experiment_response = local_client.get(f"/workflows/{experiment_id}/jobs")

    experiment_jobs = ListingResponse[JobResponse].model_validate(
        get_jobs_per_experiment_response.json()
    )

    for job in experiment_jobs.items:
        logs_job_response = local_client.get(f"/jobs/{job}/logs")
        logs_job_response_model = JobLogsResponse.model_validate(logs_job_response.json())
        logger.info(f"Logs for job {job}: ------")
        logger.info(f"{logs_job_response_model}")
        logger.info("------")

    get_ds_after_response = local_client.get("/datasets/")
    assert get_ds_after_response.status_code == 200
    get_ds_after = ListingResponse[DatasetResponse].model_validate(get_ds_after_response.json())
    assert get_ds_after.total == get_ds.total + 1


def test_experiment_non_existing(local_client: TestClient, dependency_overrides_services):
    non_existing_id = "71aaf905-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/experiments/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Job with ID {non_existing_id} not found"


def test_job_non_existing(local_client: TestClient, dependency_overrides_services):
    non_existing_id = "71aaf905-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/jobs/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Job with ID {non_existing_id} not found"
