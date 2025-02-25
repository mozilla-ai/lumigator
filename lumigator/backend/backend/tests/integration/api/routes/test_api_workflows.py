import time
from uuid import UUID

import pytest
import requests
from fastapi.testclient import TestClient
from loguru import logger
from lumigator_schemas.datasets import DatasetFormat, DatasetResponse
from lumigator_schemas.experiments import GetExperimentResponse
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobLogsResponse,
    JobResponse,
    JobResultDownloadResponse,
    JobResultObject,
    JobStatus,
    JobType,
)
from lumigator_schemas.workflows import WorkflowDetailsResponse, WorkflowResponse, WorkflowStatus

from backend.main import app
from backend.tests.conftest import (
    TEST_CAUSAL_MODEL,
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
    dependency_overrides_services,
):
    response = local_client.get("/health")
    assert response.status_code == 200

    logger.info("Running test...")
    # store how many ds are in the db before we start
    get_ds_response = local_client.get("/datasets/")
    assert get_ds_response.status_code == 200
    get_ds = ListingResponse[DatasetResponse].model_validate(get_ds_response.json())

    create_response = local_client.post(
        "/datasets/",
        data={},
        files={"dataset": dialog_dataset, "format": (None, DatasetFormat.JOB.value)},
    )

    assert create_response.status_code == 201

    created_dataset = DatasetResponse.model_validate(create_response.json())

    get_ds_before_response = local_client.get("/datasets/")
    assert get_ds_before_response.status_code == 200
    get_ds_before = ListingResponse[DatasetResponse].model_validate(get_ds_before_response.json())
    assert get_ds_before.total == get_ds.total + 1

    infer_payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "dataset": str(created_dataset.id),
        "max_samples": 10,
        "job_config": {
            "job_type": JobType.INFERENCE,
            "model": TEST_CAUSAL_MODEL,
            "provider": "hf",
            "output_field": "predictions",
            "store_to_dataset": True,
        },
    }
    create_inference_job_response = local_client.post("/jobs/inference/", headers=POST_HEADER, json=infer_payload)
    assert create_inference_job_response.status_code == 201

    create_inference_job_response_model = JobResponse.model_validate(create_inference_job_response.json())

    assert wait_for_job(local_client, create_inference_job_response_model.id)

    logs_infer_job_response = local_client.get(f"/jobs/{create_inference_job_response_model.id}/logs")
    logs_infer_job_response_model = JobLogsResponse.model_validate(logs_infer_job_response.json())
    logger.info(f"-- infer logs -- {create_inference_job_response_model.id}")
    logger.info(f"#{logs_infer_job_response_model.logs}#")

    # retrieve the DS for the infer job...
    output_infer_job_response = local_client.get(f"/jobs/{create_inference_job_response_model.id}/dataset")
    assert output_infer_job_response is not None
    assert output_infer_job_response.status_code == 200

    output_infer_job_response_model = DatasetResponse.model_validate(output_infer_job_response.json())
    assert output_infer_job_response_model is not None

    eval_payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "dataset": str(output_infer_job_response_model.id),
        "max_samples": 10,
        "job_config": {
            "job_type": JobType.EVALUATION,
            "metrics": ["rouge", "meteor"],
            "model": TEST_CAUSAL_MODEL,
            "provider": "hf",
        },
    }

    create_evaluation_job_response = local_client.post("/jobs/evaluator/", headers=POST_HEADER, json=eval_payload)
    assert create_evaluation_job_response.status_code == 201

    create_evaluation_job_response_model = JobResponse.model_validate(create_evaluation_job_response.json())

    assert wait_for_job(local_client, create_evaluation_job_response_model.id)

    logs_evaluation_job_response = local_client.get(f"/jobs/{create_evaluation_job_response_model.id}/logs")
    logs_evaluation_job_response_model = JobLogsResponse.model_validate(logs_evaluation_job_response.json())
    logger.info(f"-- eval logs -- {create_evaluation_job_response_model.id}")
    logger.info(f"#{logs_evaluation_job_response_model.logs}#")

    # FIXME Either remove the store_to_dataset option, or
    # restore it to the jobs service
    get_ds_after_response = local_client.get("/datasets/")
    assert get_ds_after_response.status_code == 200
    get_ds_after = ListingResponse[DatasetResponse].model_validate(get_ds_after_response.json())
    assert get_ds_after.total == get_ds_before.total + 1

    get_all_jobs = local_client.get("/jobs")
    assert (ListingResponse[JobResponse].model_validate(get_all_jobs.json())).total == 2
    get_jobs_infer = local_client.get("/jobs?job_types=inference")
    assert (ListingResponse[JobResponse].model_validate(get_jobs_infer.json())).total == 1
    get_jobs_eval = local_client.get("/jobs?job_types=evaluator")
    assert (ListingResponse[JobResponse].model_validate(get_jobs_eval.json())).total == 1


@pytest.mark.parametrize("unnanotated_dataset", ["dialog_empty_gt_dataset", "dialog_no_gt_dataset"])
def test_upload_data_no_gt_launch_annotation(
    request: pytest.FixtureRequest,
    local_client: TestClient,
    unnanotated_dataset,
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
        "job_config": {
            "job_type": JobType.ANNOTATION,
            "task": "summarization",
        },
    }
    create_annotation_job_response = local_client.post("/jobs/annotate/", headers=POST_HEADER, json=annotation_payload)
    assert create_annotation_job_response.status_code == 201

    create_annotation_job_response_model = JobResponse.model_validate(create_annotation_job_response.json())

    assert wait_for_job(local_client, create_annotation_job_response_model.id)

    logs_annotation_job_response = local_client.get(f"/jobs/{create_annotation_job_response_model.id}/logs")
    logger.info(logs_annotation_job_response)
    logs_annotation_job_response_model = JobLogsResponse.model_validate(logs_annotation_job_response.json())
    logger.info(f"-- infer logs -- {create_annotation_job_response_model.id}")
    logger.info(f"#{logs_annotation_job_response_model.logs}#")

    logs_annotation_job_results = local_client.get(f"/jobs/{create_annotation_job_response_model.id}/result/download")
    logs_annotation_job_results_model = JobResultDownloadResponse.model_validate(logs_annotation_job_results.json())
    logger.info(f"Download url: {logs_annotation_job_results_model.download_url}")
    annotation_job_results_url = requests.get(
        logs_annotation_job_results_model.download_url,
        timeout=5,  # 5 seconds
    )
    logs_annotation_job_output = JobResultObject.model_validate(annotation_job_results_url.json())
    assert logs_annotation_job_output.artifacts["predictions"] is None
    assert logs_annotation_job_output.artifacts["ground_truth"] is not None
    logger.info(f"Created results: {logs_annotation_job_output}")


def check_backend_health_status(local_client: TestClient):
    """Check the backend health status."""
    response = local_client.get("/health")
    assert response.status_code == 200


def check_initial_dataset_count(local_client: TestClient):
    """Check the initial dataset count."""
    get_ds_response = local_client.get("/datasets/")
    assert get_ds_response.status_code == 200
    return ListingResponse[DatasetResponse].model_validate(get_ds_response.json())


def upload_dataset(local_client: TestClient, dialog_dataset):
    """Upload a dataset."""
    create_response = local_client.post(
        "/datasets/",
        data={},
        files={"dataset": dialog_dataset, "format": (None, DatasetFormat.JOB.value)},
    )
    assert create_response.status_code == 201
    return DatasetResponse.model_validate(create_response.json())


def check_dataset_count_after_upload(local_client: TestClient, initial_count):
    """Check the dataset count after uploading a dataset."""
    get_ds_after_response = local_client.get("/datasets/")
    assert get_ds_after_response.status_code == 200
    get_ds_after = ListingResponse[DatasetResponse].model_validate(get_ds_after_response.json())
    assert get_ds_after.total == initial_count.total + 1
    return get_ds_after


def create_experiment(local_client: TestClient, dataset_id: UUID):
    """Create an experiment."""
    experiment = local_client.post(
        "/experiments/",
        headers=POST_HEADER,
        json={
            "name": "test_create_exp_workflow_check_results",
            "description": "Test for an experiment with associated workflows",
            "task_definition": {"task": "summarization"},
            "dataset": str(dataset_id),
            "max_samples": 1,
        },
    )
    assert experiment.status_code == 201
    return experiment.json()["id"]


def run_workflow(local_client: TestClient, dataset_id, experiment_id, workflow_name):
    """Run a workflow for the experiment."""
    workflow = WorkflowResponse.model_validate(
        local_client.post(
            "/workflows/",
            headers=POST_HEADER,
            json={
                "name": workflow_name,
                "description": "Test workflow for inf and eval",
                "task_definitions": {"task": "summarization"},
                "model": TEST_CAUSAL_MODEL,
                "provider": "hf",
                "dataset": str(dataset_id),
                "experiment_id": experiment_id,
                "max_samples": 1,
            },
        ).json()
    )
    return workflow


def validate_experiment_results(local_client: TestClient, experiment_id, workflow_details):
    """Validate experiment results."""
    experiment_results = GetExperimentResponse.model_validate(local_client.get(f"/experiments/{experiment_id}").json())
    assert workflow_details.experiment_id == experiment_results.id
    assert len(experiment_results.workflows) == 1
    assert workflow_details.model_dump(exclude={"artifacts_download_url"}) == experiment_results.workflows[
        0
    ].model_dump(exclude={"artifacts_download_url"})


def validate_updated_experiment_results(
    local_client: TestClient, experiment_id, workflow_1_details, workflow_2_details
):
    """Validate updated experiment results."""
    experiment_results = GetExperimentResponse.model_validate(local_client.get(f"/experiments/{experiment_id}").json())
    assert len(experiment_results.workflows) == 2
    assert workflow_1_details.model_dump(exclude={"artifacts_download_url"}) in [
        w.model_dump(exclude={"artifacts_download_url"}) for w in experiment_results.workflows
    ]
    assert workflow_2_details.model_dump(exclude={"artifacts_download_url"}) in [
        w.model_dump(exclude={"artifacts_download_url"}) for w in experiment_results.workflows
    ]


def retrieve_and_validate_workflow_logs(local_client: TestClient, workflow_id):
    """Retrieve and validate workflow logs."""
    logs_job_response = local_client.get(f"/workflows/{workflow_id}/logs")
    logs = JobLogsResponse.model_validate(logs_job_response.json())
    assert logs.logs is not None
    assert "Inference results stored at" in logs.logs
    assert "Storing evaluation results into" in logs.logs
    assert logs.logs.index("Inference results stored at") < logs.logs.index("Storing evaluation results into")


def delete_experiment_and_validate(local_client: TestClient, experiment_id):
    """Delete the experiment and ensure associated workflows are also deleted."""
    local_client.delete(f"/experiments/{experiment_id}")
    response = local_client.get(f"/experiments/{experiment_id}")
    assert response.status_code == 404


def list_experiments(local_client: TestClient):
    response = local_client.get("/experiments/").json()
    ListingResponse[GetExperimentResponse].model_validate(response)


def check_artifacts_times(artifacts_url):
    artifacts = requests.get(
        artifacts_url,
        timeout=5,  # 5 seconds
    ).json()
    logger.critical(artifacts)
    assert "evaluation_time" in artifacts["artifacts"]
    assert "inference_time" in artifacts["artifacts"]


@pytest.mark.integration
def test_full_experiment_launch(local_client: TestClient, dialog_dataset, dependency_overrides_services):
    """This is the main integration test: it checks:
    * The backend health status
    * Uploading a dataset
    * Creating an experiment
    * Running workflows for the experiment
    * Waiting for workflows to complete
    * Validating experiment results
    * Adding additional workflows to the experiment
    * Validating updated experiment results
    * Retrieving and validating workflow logs
    * Deleting the experiment and ensuring associated workflows are also deleted
    """
    check_backend_health_status(local_client)
    initial_count = check_initial_dataset_count(local_client)
    dataset = upload_dataset(local_client, dialog_dataset)
    check_dataset_count_after_upload(local_client, initial_count)
    experiment_id = create_experiment(local_client, dataset.id)
    workflow_1 = run_workflow(local_client, dataset.id, experiment_id, "Workflow_1")
    workflow_1_details = wait_for_workflow_complete(local_client, workflow_1.id)
    check_artifacts_times(workflow_1_details.artifacts_download_url)
    validate_experiment_results(local_client, experiment_id, workflow_1_details)
    workflow_2 = run_workflow(local_client, dataset.id, experiment_id, "Workflow_2")
    workflow_2_details = wait_for_workflow_complete(local_client, workflow_2.id)
    check_artifacts_times(workflow_2_details.artifacts_download_url)
    list_experiments(local_client)
    validate_updated_experiment_results(local_client, experiment_id, workflow_1_details, workflow_2_details)
    retrieve_and_validate_workflow_logs(local_client, workflow_1_details.id)
    delete_experiment_and_validate(local_client, experiment_id)


def test_experiment_non_existing(local_client: TestClient, dependency_overrides_services):
    non_existing_id = "71aaf905-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/experiments/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Experiment with ID {non_existing_id} not found"


def test_job_non_existing(local_client: TestClient, dependency_overrides_services):
    non_existing_id = "71aaf905-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/jobs/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Job with ID {non_existing_id} not found"


def wait_for_workflow_complete(local_client: TestClient, workflow_id: UUID):
    for _ in range(1, 300):
        time.sleep(1)
        workflow_details = WorkflowDetailsResponse.model_validate(local_client.get(f"/workflows/{workflow_id}").json())
        workflow_status = workflow_details.status
        if workflow_status in [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]:
            logger.info(f"Workflow status: {workflow_status}")
            break
    if workflow_status not in [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]:
        raise Exception(f"Stopped, job remains in {workflow_status} status")

    return workflow_details
