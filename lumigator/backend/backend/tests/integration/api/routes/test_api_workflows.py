import asyncio
import time
import uuid
from http import HTTPStatus
from uuid import UUID

import pytest
import requests
from fastapi.testclient import TestClient
from httpx import HTTPStatusError, RequestError
from inference.schemas import GenerationConfig, InferenceJobConfig, InferenceServerConfig
from loguru import logger
from lumigator_schemas.datasets import DatasetFormat, DatasetResponse
from lumigator_schemas.experiments import GetExperimentResponse
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobInferenceConfig,
    JobInferenceCreate,
    JobLogsResponse,
    JobResponse,
    JobResultDownloadResponse,
    JobResultObject,
    JobStatus,
    JobType,
)
from lumigator_schemas.secrets import SecretUploadRequest
from lumigator_schemas.tasks import TaskType
from lumigator_schemas.workflows import WorkflowDetailsResponse, WorkflowResponse, WorkflowStatus
from pydantic import PositiveInt, ValidationError

from backend.main import app
from backend.tests.conftest import (
    MAX_JOB_TIMEOUT_SECS,
    MAX_POLLS,
    POLL_WAIT_TIME,
    TEST_CAUSAL_MODEL,
    TEST_SEQ2SEQ_MODEL,
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
            "model": TEST_SEQ2SEQ_MODEL,
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
            "model": TEST_SEQ2SEQ_MODEL,
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
            "model": TEST_SEQ2SEQ_MODEL,
            "provider": "hf",
            "output_field": "ground_truth",
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


def upload_dataset(local_client: TestClient, dataset):
    """Upload a dataset."""
    create_response = local_client.post(
        "/datasets/",
        data={},
        files={"dataset": dataset, "format": (None, DatasetFormat.JOB.value)},
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


def create_experiment(
    local_client: TestClient,
    dataset_id: UUID,
    task_definition: dict,
    name: str = "test_create_exp_workflow_check_results",
    description: str = "Test for an experiment with associated workflows",
) -> str:
    """Create an experiment."""
    experiment = local_client.post(
        "/experiments/",
        headers=POST_HEADER,
        json={
            "name": name,
            "description": description,
            "task_definition": task_definition,
            "dataset": str(dataset_id),
            "max_samples": 1,
        },
    )
    assert experiment.status_code == 201
    json_response = experiment.json()
    assert "id" in json_response
    experiment_id = json_response["id"]
    assert isinstance(experiment_id, str)
    assert len(experiment_id.strip()) > 0

    return experiment_id


def run_workflow(
    local_client: TestClient,
    experiment_id: str,
    workflow_name: str,
    model: str,
    job_timeout_sec: PositiveInt | None = MAX_JOB_TIMEOUT_SECS,
    description: str = "Test workflow for inf and eval",
) -> WorkflowResponse:
    """Run a workflow for the experiment."""
    workflow_payload = {
        "name": workflow_name,
        "description": description,
        "model": model,
        "provider": "hf",
        "experiment_id": experiment_id,
        "job_timeout_sec": 1000,
        "metrics": ["rouge", "meteor"],
    }
    # The timeout cannot be 0
    if job_timeout_sec:
        workflow_payload["job_timeout_sec"] = job_timeout_sec
    workflow = WorkflowResponse.model_validate(
        local_client.post(
            "/workflows/",
            headers=POST_HEADER,
            json=workflow_payload,
        ).json()
    )
    return workflow


def validate_experiment_results(
    local_client: TestClient, experiment_id: str, workflow_details_list: list[WorkflowDetailsResponse]
):
    """Validate that the experiment results match the expected workflows.

    This function retrieves the experiment details via the API and verifies that:
    1. The experiment ID in the results matches the expected ID.
    2. The number of workflows in the experiment matches the number of expected workflows.
    3. Each workflow in the experiment:
       - Has the correct experiment ID.
       - Is marked as "SUCCEEDED".
       - Has a valid artifacts download URL.

    @param local_client: The test client used to make requests to the API.
    @param experiment_id: The ID of the experiment to validate.
    @param workflow_details_list: A list of expected workflow details to compare against the experiment results.
    """
    response = local_client.get(f"/experiments/{experiment_id}")
    response.raise_for_status()
    response_json = response.json()
    assert response_json
    experiment_results = GetExperimentResponse.model_validate(response_json)

    # Ensure all workflows have the correct experiment ID
    assert all(workflow.experiment_id == experiment_results.id for workflow in workflow_details_list)

    # Validate the number of workflows
    assert len(experiment_results.workflows) == len(workflow_details_list)

    # Validate that each workflow is successful and has a valid download URL
    for expected_details in workflow_details_list:
        actual_workflow = next(
            (workflow for workflow in experiment_results.workflows if workflow.id == expected_details.id), None
        )
        assert actual_workflow is not None
        assert actual_workflow.status == WorkflowStatus.SUCCEEDED
        assert actual_workflow.artifacts_download_url is not None
        # Compare properties of the workflow, excluding the download URL
        expected_workflow_data = expected_details.model_dump(exclude={"artifacts_download_url"})
        actual_workflow_data = actual_workflow.model_dump(exclude={"artifacts_download_url"})
        assert expected_workflow_data == actual_workflow_data


def retrieve_and_validate_workflow_logs(
    local_client: TestClient, workflow_details_list: list[WorkflowDetailsResponse]
) -> None:
    """Retrieve and validate workflow logs."""
    for workflow_details in workflow_details_list:
        logs_job_response = local_client.get(f"/workflows/{workflow_details.id}/logs")
        logs_job_response.raise_for_status()
        logs = JobLogsResponse.model_validate(logs_job_response.json())
        assert logs.logs is not None
        assert "Inference results stored at" in logs.logs
        assert "Storing evaluation results to" in logs.logs
        assert "Storing evaluation results for S3 to" in logs.logs
        assert logs.logs.index("Inference results stored at") < logs.logs.index("Storing evaluation results to")
        assert logs.logs.index("Inference results stored at") < logs.logs.index("Storing evaluation results for S3 to")


def delete_experiment_and_validate(
    local_client: TestClient, experiment_id: str, workflow_details_list: list[WorkflowDetailsResponse]
) -> None:
    """Delete the experiment and ensure associated workflows are also deleted."""
    local_client.delete(f"/experiments/{experiment_id}")
    response = local_client.get(f"/experiments/{experiment_id}")
    assert response.status_code == 404
    for workflow_details in workflow_details_list:
        response = local_client.get(f"/workflows/{workflow_details.id}")
        assert response.status_code == 404


def list_experiments(local_client: TestClient):
    response = local_client.get("/experiments/").json()
    ListingResponse[GetExperimentResponse].model_validate(response)


def check_artifacts_contain_times(artifacts_url: str):
    response = requests.get(artifacts_url, timeout=5)  # 5 second timeout
    response.raise_for_status()
    data = response.json()
    assert "artifacts" in data
    artifacts = data["artifacts"]
    assert "evaluation_time" in artifacts
    assert "inference_time" in artifacts


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dataset_name, task_definition, model",
    [
        (
            "dialog_dataset",
            {
                "task": "summarization",
            },
            TEST_SEQ2SEQ_MODEL,
        ),
        (
            "mock_translation_dataset",
            {
                "task": "translation",
                "source_language": "en",
                "target_language": "de",
            },
            TEST_CAUSAL_MODEL,
        ),
    ],
)
async def test_full_experiment_launch(
    local_client: TestClient,
    dataset_name: str,
    task_definition: dict,
    model: str,
    request,
    dependency_overrides_services,
):
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
    test_name = f"test_full_experiment_launch/{dataset_name}"

    logger.info(
        f"Running '{test_name}"
        f"dataset_name: {dataset_name}, "
        f"task_definition: {task_definition.get('task')}, "
        f"model: {model}",
    )

    # Load the fixture using the name in the 'parametrize' params
    dataset = request.getfixturevalue(dataset_name)

    # Health check
    check_backend_health_status(local_client)

    # Dataset upload
    initial_count = check_initial_dataset_count(local_client)
    dataset = upload_dataset(local_client, dataset)
    check_dataset_count_after_upload(local_client, initial_count)

    # Trigger experiment/workflows
    experiment_id = create_experiment(local_client, dataset.id, task_definition)
    workflow_names = ["Workflow_1", "Workflow_2"]
    workflows = [
        run_workflow(
            local_client=local_client,
            experiment_id=experiment_id,
            workflow_name=name,
            model=model,
            description=f"{test_name}: {name}",
        )
        for name in workflow_names
    ]
    workflow_details_responses = await asyncio.gather(
        *[wait_for_workflow_complete(local_client, workflow.id) for workflow in workflows]
    )

    for workflow_details in workflow_details_responses:
        assert workflow_details
        assert workflow_details.status == WorkflowStatus.SUCCEEDED
        assert workflow_details.artifacts_download_url
        check_artifacts_contain_times(workflow_details.artifacts_download_url)

    validate_experiment_results(local_client, experiment_id, workflow_details_responses)
    retrieve_and_validate_workflow_logs(local_client, workflow_details_responses)

    # Clean up ...
    delete_experiment_and_validate(local_client, experiment_id, workflow_details_responses)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_timedout_experiment(local_client: TestClient, dialog_dataset, dependency_overrides_services):
    """Test ensures that the timeout set on jobs causes the workflow to fail:
    * The backend health status
    * Uploading a dataset
    * Creating an experiment
    * Running a workflow for the experiment (max 1 sec timeout)
    * Check that the workflow is in failed state
    * Check that any jobs are in a stopped state
    """
    # Hardcoded values for summarization
    task_definition = {"task": "summarization"}

    check_backend_health_status(local_client)

    initial_count = check_initial_dataset_count(local_client)
    dataset = upload_dataset(local_client, dialog_dataset)
    check_dataset_count_after_upload(local_client, initial_count)

    experiment_id = create_experiment(local_client, dataset.id, task_definition)
    workflow = run_workflow(
        local_client=local_client,
        experiment_id=experiment_id,
        workflow_name="timed_out_workflow",
        model=TEST_SEQ2SEQ_MODEL,
        job_timeout_sec=1,  # 1 second timeout to fail the workflow quickly
        description="This workflow should fail",
    )
    workflow_details = await wait_for_workflow_complete(local_client, workflow.id)
    assert workflow_details is not None
    assert workflow_details.status == WorkflowStatus.FAILED
    ensure_job_status(local_client, workflow_details, JobStatus.STOPPED)


def ensure_job_status(local_client: TestClient, workflow_details: WorkflowDetailsResponse, expected_status: JobStatus):
    """Helper function to check that all jobs in a workflow have the expected status."""
    for job in workflow_details.jobs:
        ray_job_id = next((param["value"] for param in job.parameters if param.get("name") == "ray_job_id"), None)
        assert ray_job_id, f"'ray_job_id' missing for job {job.id}"
        response = local_client.get(f"/jobs/{ray_job_id}")
        response.raise_for_status()
        job_response = JobResponse.model_validate(response.json())
        # Assert that the job status matches the expected status
        assert job_response.status == expected_status, (
            f"Job {job.id}, status: {job_response.status}, expected {expected_status}"
        )


def test_experiment_non_existing(local_client: TestClient, dependency_overrides_services):
    non_existing_id = "d34dbeef-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/experiments/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Experiment with ID {non_existing_id} not found"


def test_job_non_existing(local_client: TestClient, dependency_overrides_services):
    non_existing_id = "d34dbeef-4bea-4d19-ad06-214202165812"
    response = local_client.get(f"/jobs/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Job with ID {non_existing_id} not found"


async def wait_for_workflow_complete(local_client: TestClient, workflow_id: UUID) -> WorkflowDetailsResponse | None:
    """Wait for the workflow to complete, including post-completion processing for successful
    workflows to create compiled results.

    Makes a total of ``MAX_POLLS`` (as configured in the ``conftest.py``).
    Sleeps for ``POLL_WAIT_TIME`` seconds between each poll (as configured in the ``conftest.py``).

    :param local_client: The test client.
    :param workflow_id: The workflow ID of the workflow to wait for.
    :return: The workflow details, or ``None`` if the workflow did not reach the required completed state
                within the maximum number of polls.
    """
    attempt = 0
    max_attempts = MAX_POLLS
    wait_duration = POLL_WAIT_TIME

    while attempt < max_attempts:
        # Allow the waiting interval if we're coming around again.
        if attempt > 0:
            await asyncio.sleep(wait_duration)

        attempt += 1
        try:
            response = local_client.get(f"/workflows/{workflow_id}")
            response.raise_for_status()
            # Validation failure will raise an exception (``ValidationError``) which is fine
            # as if we're getting a response we expect it to be valid.
            workflow = WorkflowDetailsResponse.model_validate(response.json())
        except (RequestError, HTTPStatusError) as e:
            # Log the error but allow us to retry the request until we've maxed out our attempts.
            logger.warning(f"Workflow: {workflow_id}, request: ({attempt}/{max_attempts}) failed: {e}")
            continue

        # Check if the workflow is not in a terminal state.
        if workflow.status not in {WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED}:
            logger.info(
                f"Workflow: {workflow_id}, "
                f"request: ({attempt}/{max_attempts}), "
                f"status: {workflow.status}, "
                f"not in terminal state"
            )
            continue

        # If the workflow failed, we can stop checking.
        if workflow.status == WorkflowStatus.FAILED:
            return workflow

        # The workflow was successful, but we need the artifacts download url to be populated.
        if not workflow.artifacts_download_url:
            logger.info(
                f"Workflow: {workflow_id}, "
                f"request: ({attempt}/{max_attempts}), "
                f"status: {workflow.status}, "
                f"artifacts not ready"
            )
            continue

        logger.info(
            f"Workflow: {workflow_id},"
            f"request: ({attempt}/{max_attempts}), "
            f"status: {workflow.status}, "
            f"succeeded and processed)"
        )
        return workflow

    # Couldn't get the workflow details within the maximum number of polls.
    return None


def _test_launch_job_with_secret(
    local_client: TestClient,
    dialog_dataset,
    dependency_overrides_services,
):
    logger.info("Running test...")
    ko_secret = SecretUploadRequest(value="<WRONG SECRET HERE>", description="Mistral API key")
    secret_name = "MISTRAL_API_KEY"  # pragma: allowlist secret
    response = local_client.put(f"/settings/secrets/{secret_name}", json=ko_secret.model_dump())
    logger.info(f"Uploading KO key {secret_name}: {response}")
    assert response.status_code == HTTPStatus.CREATED or response.status_code == HTTPStatus.NO_CONTENT

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

    infer_model = JobInferenceCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        dataset=str(created_dataset.id),
        max_samples=2,
        job_config=JobInferenceConfig(
            model="ministral-8b-latest",
            provider="mistral",
        ),
    )
    infer_payload = infer_model.model_dump(mode="json")
    create_inference_job_response = local_client.post("/jobs/inference/", headers=POST_HEADER, json=infer_payload)
    if create_inference_job_response.status_code >= 400:
        logger.error(f"error: {create_inference_job_response.text}")
    assert create_inference_job_response.status_code == 201
    create_inference_job_response_model = JobResponse.model_validate(create_inference_job_response.json())
    assert not wait_for_job(local_client, create_inference_job_response_model.id)

    ok_secret = SecretUploadRequest(value="<CORRECT SECRET HERE>", description="Mistral API key")
    response = local_client.put(f"/settings/secrets/{secret_name}", json=ok_secret.model_dump())
    assert response.status_code == HTTPStatus.NO_CONTENT

    infer_model = JobInferenceCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        dataset=str(created_dataset.id),
        max_samples=2,
        api_keys=[secret_name],
        job_config=JobInferenceConfig(
            model="ministral-8b-latest",
            provider="mistral",
        ),
    )
    infer_payload = infer_model.model_dump(mode="json")
    create_inference_job_response = local_client.post("/jobs/inference/", headers=POST_HEADER, json=infer_payload)
    assert create_inference_job_response.status_code == 201
    create_inference_job_response_model = JobResponse.model_validate(create_inference_job_response.json())
    assert wait_for_job(local_client, create_inference_job_response_model.id)
