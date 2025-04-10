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
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_INTERVAL_SECONDS,
    MAX_JOB_TIMEOUT_SECS,
    TEST_CAUSAL_MODEL,
    TEST_SEQ2SEQ_MODEL,
    wait_for_job,
)

POST_HEADER = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


@app.on_event("startup")
def test_health_ok(test_client: TestClient):
    response = test_client.get("/health/")
    assert response.status_code == 200


def test_upload_data_launch_job(
    test_client_without_background_tasks: TestClient,
    dialog_dataset,
    dependency_overrides_services,
):
    logger.info("Running test: 'test_upload_data_launch_job'")
    client = test_client_without_background_tasks

    response = client.get("/health")
    assert response.status_code == 200

    # store how many ds are in the db before we start
    get_ds_response = client.get("/datasets/")
    assert get_ds_response.status_code == 200
    get_ds = ListingResponse[DatasetResponse].model_validate(get_ds_response.json())

    create_response = client.post(
        "/datasets/",
        data={},
        files={"dataset": dialog_dataset, "format": (None, DatasetFormat.JOB.value)},
    )

    assert create_response.status_code == 201

    created_dataset = DatasetResponse.model_validate(create_response.json())

    get_ds_before_response = client.get("/datasets/")
    assert get_ds_before_response.status_code == 200
    get_ds_before = ListingResponse[DatasetResponse].model_validate(get_ds_before_response.json())
    assert get_ds_before.total == get_ds.total + 1

    infer_payload = {
        "name": "test_upload_data_launch_job-inference",
        "description": "Huggingface model inference",
        "dataset": str(created_dataset.id),
        "max_samples": 10,
        "job_config": {
            "job_type": JobType.INFERENCE,
            "model": TEST_SEQ2SEQ_MODEL,
            "provider": "hf",
            "output_field": "predictions",
            "store_to_dataset": False,
        },
    }
    create_inference_job_response = client.post("/jobs/inference/", headers=POST_HEADER, json=infer_payload)
    assert create_inference_job_response.status_code == 201


@pytest.mark.parametrize("unnanotated_dataset", ["dialog_empty_gt_dataset", "dialog_no_gt_dataset"])
def test_upload_data_no_gt_launch_annotation(
    request: pytest.FixtureRequest,
    test_client_without_background_tasks: TestClient,
    unnanotated_dataset,
    dependency_overrides_services,
):
    dataset = request.getfixturevalue(unnanotated_dataset)
    client = test_client_without_background_tasks

    create_response = client.post(
        "/datasets/",
        data={},
        files={"dataset": dataset, "format": (None, DatasetFormat.JOB.value)},
    )

    assert create_response.status_code == 201

    created_dataset = DatasetResponse.model_validate(create_response.json())

    annotation_payload = {
        "name": "test_annotate",
        "description": "Annotation job to add ground truth",
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

    create_annotation_job_response = client.post("/jobs/annotate/", headers=POST_HEADER, json=annotation_payload)
    assert create_annotation_job_response.status_code == 201

    create_annotation_job_response_model = JobResponse.model_validate(create_annotation_job_response.json())

    logs_annotation_job_response = client.get(f"/jobs/{create_annotation_job_response_model.id}/logs")
    logger.info(logs_annotation_job_response)
    logs_annotation_job_response_model = JobLogsResponse.model_validate(logs_annotation_job_response.json())
    logger.info(f"-- infer logs -- {create_annotation_job_response_model.id}")
    logger.info(f"#{logs_annotation_job_response_model.logs}#")


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
    hf_model: str,
    job_timeout_sec: PositiveInt | None = MAX_JOB_TIMEOUT_SECS,
    description: str = "Test workflow for inf and eval",
) -> WorkflowResponse:
    """Run a new workflow under the specified experiment.

    :param local_client: The test client used to make requests to the API.
    :param experiment_id: The ID of the experiment to which the workflow belongs.
    :param workflow_name: The name of the workflow.
    :param hf_model: The Hugging Face model to use for the workflow.
    :param job_timeout_sec: The timeout for any job in the workflow, in seconds.
    :param description: A description for the workflow.
    :return: The created workflow response.
    """
    workflow_payload = {
        "name": workflow_name,
        "description": description,
        "model": hf_model,
        "provider": "hf",
        "experiment_id": experiment_id,
        "job_timeout_sec": job_timeout_sec,
        "metrics": ["rouge", "meteor"],
    }

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
    test_client_without_background_tasks: TestClient,
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
    """
    client = test_client_without_background_tasks
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
    check_backend_health_status(client)

    # Dataset upload
    initial_count = check_initial_dataset_count(client)
    dataset = upload_dataset(client, dataset)
    check_dataset_count_after_upload(client, initial_count)

    # Trigger experiment/workflows
    experiment_id = create_experiment(client, dataset.id, task_definition)
    workflow_names = ["Backend_Workflow_1", "Backend_Workflow_2"]
    for name in workflow_names:
        run_workflow(
            local_client=client,
            experiment_id=experiment_id,
            workflow_name=name,
            hf_model=model,
            description=f"{test_name}: {name}",
        )


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


def test_experiment_non_existing(test_client: TestClient, dependency_overrides_services):
    non_existing_id = "d34dbeef-4bea-4d19-ad06-214202165812"
    response = test_client.get(f"/experiments/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Experiment with ID {non_existing_id} not found"


def test_job_non_existing(test_client: TestClient, dependency_overrides_services):
    non_existing_id = "d34dbeef-4bea-4d19-ad06-214202165812"
    response = test_client.get(f"/jobs/{non_existing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Job with ID {non_existing_id} not found"


async def wait_for_workflow_complete(
    local_client: TestClient,
    workflow_id: UUID,
    max_retries: PositiveInt = DEFAULT_MAX_RETRIES,
    retry_interval: PositiveInt = DEFAULT_RETRY_INTERVAL_SECONDS,
) -> WorkflowDetailsResponse | None:
    """Wait for the workflow to complete, including post-completion processing for successful
    workflows to create compiled results.

    Makes a total of ``max_retries`` requests, sleeping for ``retry_interval`` seconds between each poll.

    :param local_client: The test client.
    :param workflow_id: The workflow ID of the workflow to wait for.
    :param max_retries: The maximum number of retries to check the workflow status.
    :param retry_interval: The interval in seconds to wait between retries.
    :return: The workflow details, or ``None`` if the workflow did not reach the required completed state
                within the maximum number of polls.
    """
    attempt = 0
    while attempt < max_retries:
        # Allow the waiting interval if we're coming around again.
        if attempt > 0:
            await asyncio.sleep(retry_interval)

        attempt += 1
        try:
            response = local_client.get(f"/workflows/{workflow_id}")
            response.raise_for_status()
            # Validation failure will raise an exception (``ValidationError``) which is fine
            # as if we're getting a response we expect it to be valid.
            workflow = WorkflowDetailsResponse.model_validate(response.json())
        except (RequestError, HTTPStatusError) as e:
            # Log the error but allow us to retry the request until we've maxed out our attempts.
            logger.warning(f"Workflow: {workflow_id}, request: ({attempt}/{max_retries}) failed: {e}")
            continue

        # Check if the workflow is not in a terminal state.
        if workflow.status not in {WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED}:
            logger.info(
                f"Workflow: {workflow_id}, "
                f"request: ({attempt}/{max_retries}), "
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
                f"request: ({attempt}/{max_retries}), "
                f"status: {workflow.status}, "
                f"artifacts not ready"
            )
            continue

        logger.info(
            f"Workflow: {workflow_id},"
            f"request: ({attempt}/{max_retries}), "
            f"status: {workflow.status}, "
            f"succeeded and processed)"
        )
        return workflow

    # Couldn't get the workflow details within the maximum number of polls.
    return None


def test_launch_job_with_secret(
    test_client: TestClient,
    dialog_dataset,
    dependency_overrides_services,  # Required even if not used directly in the test
):
    logger.info("Running test: 'test_launch_job_with_secret'")
    secret_name = "MISTRAL_API_KEY"  # pragma: allowlist secret

    # Upload the Mistral API key as a secret with an incorrect value.
    ko_secret = SecretUploadRequest(value="<WRONG SECRET HERE>", description="Mistral API key")
    response = test_client.put(f"/settings/secrets/{secret_name}", json=ko_secret.model_dump())
    logger.info(f"Uploaded KO key {secret_name}: {response}")
    assert response.status_code == HTTPStatus.CREATED or response.status_code == HTTPStatus.NO_CONTENT

    # Upload a dataset
    create_response = test_client.post(
        "/datasets/",
        data={},
        files={"dataset": dialog_dataset, "format": (None, DatasetFormat.JOB.value)},
    )
    assert create_response.status_code == 201
    created_dataset = DatasetResponse.model_validate(create_response.json())

    # Create an inference job but don't use the secret.
    infer_create = JobInferenceCreate(
        name="test_launch_job_with_no_secret",
        description="Mistral model with no API key",
        dataset=str(created_dataset.id),
        max_samples=2,
        job_config=JobInferenceConfig(
            model="ministral-8b-latest",
            provider="mistral",
            secret_key_name=secret_name,
        ),
    )
    create_inference_job_response = test_client.post(
        url="/jobs/inference/", headers=POST_HEADER, json=infer_create.model_dump(mode="json")
    )
    create_inference_job_response.raise_for_status()
    assert create_inference_job_response.status_code == 201
    job_response = JobResponse.model_validate(create_inference_job_response.json())
    # We expect the job to fail because it needs a VALID API key for Mistral.
    assert not wait_for_job(test_client, job_response.id, max_retries=60, retry_interval=5)
