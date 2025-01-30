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
from lumigator_schemas.experiments import ExperimentResponse, GetExperimentResponse
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    Job,
    JobLogsResponse,
    JobResponse,
    JobResultDownloadResponse,
    JobStatus,
)
from lumigator_schemas.workflows import WorkflowDetailsResponse, WorkflowResponse

from backend.main import app
from backend.tests.conftest import (
    TEST_CAUSAL_MODEL,
    wait_for_experiment,
    wait_for_job,
)

POST_HEADER = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


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
        "/jobs/inference/", headers=POST_HEADER, json=infer_payload
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

    eval_payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": TEST_CAUSAL_MODEL,
        "dataset": str(output_infer_job_response_model.id),
        "config_template": simple_eval_template,
        "max_samples": 10,
    }

    create_evaluation_job_response = local_client.post(
        "/jobs/eval_lite/", headers=POST_HEADER, json=eval_payload
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

    annotation_payload = {
        "name": "test_annotate",
        "description": "Test run for Huggingface model",
        "dataset": str(created_dataset.id),
        "max_samples": 2,
        "task": "summarization",
    }
    create_annotation_job_response = local_client.post(
        "/jobs/annotate/", headers=POST_HEADER, json=annotation_payload
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
    payload = {
        "name": "test_experiment",
        "description": "Test experiment for Huggingface models",
    }

    get_ds_response = local_client.get("/datasets/")
    assert get_ds_response.status_code == 200
    get_ds = ListingResponse[DatasetResponse].model_validate(get_ds_response.json())

    create_experiments_id_response = local_client.post(
        "/experiments/new/", headers=POST_HEADER, json=payload
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
    create_workflow_response = local_client.post("/workflows/", headers=POST_HEADER, json=payload)
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


def wait_for_workflow_complete(local_client: TestClient, workflow_id: UUID):
    workflow_status = JobStatus.PENDING
    while workflow_status not in [JobStatus.SUCCEEDED, JobStatus.FAILED]:
        time.sleep(1)
        workflow_details = WorkflowDetailsResponse.model_validate(
            local_client.get(f"/workflows/{workflow_id}").json()
        )
        workflow_status = workflow_details.status
        logger.info(f"Workflow status: {workflow_status}")
    return workflow_details


def test_create_exp_workflow_check_results(
    local_client: TestClient, dialog_dataset, dependency_overrides_services
):
    """Here's how it will work
    * Create a dataset
    * Create an experiment, get back an ID and validate it
    * Create a workflow for that experiment
    * Poll the status of the workflow until it's done
    * Get the results of the workflow
    """
    # Make sure backend is healthy
    response = local_client.get("/health")
    assert response.status_code == 200

    # Upload a dataset
    create_response = local_client.post(
        "/datasets/",
        data={},
        files={"dataset": dialog_dataset, "format": (None, DatasetFormat.JOB.value)},
    )
    assert create_response.status_code == 201

    dataset = DatasetResponse.model_validate(create_response.json())

    experiment = local_client.post(
        "/experiments/new/",
        headers=POST_HEADER,
        json={
            "name": "test_create_exp_workflow_check_results",
            "description": "Test for an experiment with associated workflows",
        },
    )
    assert experiment.status_code == 201
    experiment_id = experiment.json()["id"]

    # run a workflow for that experiment
    workflow_1 = WorkflowResponse.model_validate(
        local_client.post(
            "/workflows/",
            headers=POST_HEADER,
            json={
                "name": "Workflow_1",
                "description": "Test workflow for inf and eval",
                "model": TEST_CAUSAL_MODEL,
                "dataset": str(dataset.id),
                "experiment_id": experiment_id,
                "max_samples": 1,
            },
        ).json()
    )

    # Wait till the workflow is done
    workflow_1_details = wait_for_workflow_complete(local_client, workflow_1.id)

    experiment_results = GetExperimentResponse.model_validate(
        local_client.get(f"/experiments/new/{experiment_id}").json()
    )

    assert workflow_1_details.experiment_id == experiment_results.id
    assert len(experiment_results.workflows) == 1
    # the presigned url can be different but everything else should be the same
    assert workflow_1_details.model_dump(
        exclude={"artifacts_download_url"}
    ) == experiment_results.workflows[0].model_dump(exclude={"artifacts_download_url"})

    # add another workflow to the experiment
    workflow_2 = WorkflowResponse.model_validate(
        local_client.post(
            "/workflows/",
            headers=POST_HEADER,
            json={
                "name": "Workflow_2",
                "description": "Test workflow for inf and eval",
                "model": TEST_CAUSAL_MODEL,
                "dataset": str(dataset.id),
                "experiment_id": experiment_id,
                "max_samples": 1,
            },
        ).json()
    )

    # Wait till the workflow is done
    workflow_2_details = wait_for_workflow_complete(local_client, workflow_2.id)

    # now get the results of the experiment
    experiment_results = GetExperimentResponse.model_validate(
        local_client.get(f"/experiments/new/{experiment_id}").json()
    )
    # make sure it has the info for both workflows
    assert len(experiment_results.workflows) == 2
    # make sure both workflows are in the experiment, excluding that presigned url again
    assert workflow_1_details.model_dump(exclude={"artifacts_download_url"}) in [
        w.model_dump(exclude={"artifacts_download_url"}) for w in experiment_results.workflows
    ]
    assert workflow_2_details.model_dump(exclude={"artifacts_download_url"}) in [
        w.model_dump(exclude={"artifacts_download_url"}) for w in experiment_results.workflows
    ]

    # delete the experiment
    local_client.delete(f"/experiments/new/{experiment_id}")
    response = local_client.get(f"/experiments/new/{experiment_id}")
    assert response.status_code == 404
    # make sure the workflow results also were deleted
    response = local_client.get(f"/workflows/{workflow_1_details.id}")
    assert response.status_code == 404
    response = local_client.get(f"/workflows/{workflow_2_details.id}")
    assert response.status_code == 404
