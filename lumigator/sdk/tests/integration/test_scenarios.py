"""Integration tests for the SDK. The lumigator backend needs to
be started prior to running these tests using
`make start-lumigator-build`.
"""

from time import sleep
from uuid import UUID

import pytest
import requests
from loguru import logger
from lumigator_schemas.datasets import DatasetFormat
from lumigator_schemas.jobs import JobType
from lumigator_schemas.tasks import TaskType
from lumigator_schemas.workflows import WorkflowDetailsResponse, WorkflowStatus
from lumigator_sdk.lumigator import LumigatorClient
from lumigator_sdk.strict_schemas import (
    DatasetDownloadResponse,
    ExperimentCreate,
    JobAnnotateConfig,
    JobCreate,
    JobEvalConfig,
    JobInferenceConfig,
    WorkflowCreateRequest,
)

TEST_SEQ2SEQ_MODEL = "hf-internal-testing/tiny-random-BARTForConditionalGeneration"
TEST_CAUSAL_MODEL = "hf-internal-testing/tiny-random-LlamaForCausalLM"


def test_sdk_healthcheck_ok(lumi_client_int: LumigatorClient):
    """Test the healthcheck endpoint."""
    healthy = False
    for i in range(10):
        try:
            lumi_client_int.health.healthcheck()
            healthy = True
            break
        except Exception as e:
            print(f"failed health check, retry {i} - due to {e}")
            sleep(1)
    assert healthy


def test_get_datasets_remote_ok(lumi_client_int: LumigatorClient):
    """Test the `get_datasets` endpoint."""
    datasets = lumi_client_int.datasets.get_datasets()
    assert datasets is not None


def test_get_datasets_download(lumi_client_int: LumigatorClient, dialog_data):
    """Test the download datasets endpoint."""
    dataset_response = lumi_client_int.datasets.create_dataset(dataset=dialog_data, format=DatasetFormat.JOB)

    assert dataset_response is not None
    assert isinstance(dataset_response.id, UUID)

    def sum_ends_with(download_response: DatasetDownloadResponse, extension: str):
        return sum(
            1 for u in download_response.download_urls if len(u.split("?")) == 2 and u.split("?")[0].endswith(extension)
        )

    ds_id = dataset_response.id
    download_response = lumi_client_int.datasets.get_dataset_link(ds_id)
    assert download_response is not None
    assert download_response.id == ds_id
    assert len(download_response.download_urls) == 4
    # Check we also only have a single CSV file.
    assert sum_ends_with(download_response, ".csv") == 1

    # Filter for just the CSV
    download_response = lumi_client_int.datasets.get_dataset_link(ds_id, "csv")
    assert download_response is not None
    assert download_response.id == ds_id
    assert len(download_response.download_urls) == 1
    assert sum_ends_with(download_response, ".csv") == 1


def test_dataset_lifecycle_remote_ok(lumi_client_int: LumigatorClient, dialog_data):
    """Test a complete dataset lifecycle test: add a new dataset,
    list datasets, remove the dataset
    """
    datasets = lumi_client_int.datasets.get_datasets()
    n_initial_datasets = datasets.total

    # Create a dataset
    lumi_client_int.datasets.create_dataset(dataset=dialog_data, format=DatasetFormat.JOB)
    datasets = lumi_client_int.datasets.get_datasets()
    n_current_datasets = datasets.total
    assert n_current_datasets - n_initial_datasets == 1

    # Delete one dataset (check it first)
    dataset_id = datasets.items[0].id
    created_dataset = lumi_client_int.datasets.get_dataset(dataset_id)
    assert created_dataset is not None
    lumi_client_int.datasets.delete_dataset(dataset_id)

    # Re-check the total number of datasets
    datasets = lumi_client_int.datasets.get_datasets()
    n_current_datasets = datasets.total
    assert n_current_datasets - n_initial_datasets == 0


@pytest.mark.skip(reason="Identical test exists as an e2e test, this test should be refactored or removed.")
def test_job_lifecycle_remote_ok(lumi_client_int: LumigatorClient, dialog_data, simple_eval_template):
    """Test a complete job lifecycle test: add a new dataset,
    create a new job, run the job, get the results
    """
    logger.info("Starting jobs lifecycle")
    datasets = lumi_client_int.datasets.get_datasets()
    if datasets.total > 0:
        for removed_dataset in datasets.items:
            lumi_client_int.datasets.delete_dataset(removed_dataset.id)
    datasets = lumi_client_int.datasets.get_datasets()
    n_initial_datasets = datasets.total
    dataset = lumi_client_int.datasets.create_dataset(dataset=dialog_data, format=DatasetFormat.JOB)
    datasets = lumi_client_int.datasets.get_datasets()
    n_current_datasets = datasets.total
    assert n_current_datasets - n_initial_datasets == 1

    jobs = lumi_client_int.jobs.get_jobs()
    assert jobs is not None
    logger.info(lumi_client_int.datasets.get_dataset(dataset.id))

    datasets = lumi_client_int.datasets.get_datasets()
    n_before_jobs_datasets = datasets.total

    infer_jobs_before = lumi_client_int.jobs.get_jobs_per_type(JobType.INFERENCE)
    assert infer_jobs_before is not None

    eval_jobs_before = lumi_client_int.jobs.get_jobs_per_type(JobType.EVALUATION)
    assert eval_jobs_before is not None

    infer_job_config = JobInferenceConfig(
        # FIXME make a const
        model=TEST_SEQ2SEQ_MODEL,
        provider="hf",
        output_field="predictions",
        store_to_dataset=True,
    )
    infer_job = JobCreate(
        name="test-job-int-001",
        description="This is a test job",
        dataset=dataset.id,
        max_samples=2,
        job_config=infer_job_config,
    )
    logger.info(infer_job)

    job_infer_creation_result = lumi_client_int.jobs.create_job(infer_job)
    assert job_infer_creation_result is not None
    assert lumi_client_int.jobs.get_jobs() is not None

    eval_jobs_after = lumi_client_int.jobs.get_jobs_per_type(JobType.EVALUATION)
    assert eval_jobs_after is not None
    assert eval_jobs_after.total - eval_jobs_before.total == 0

    infer_job_status = lumi_client_int.jobs.wait_for_job(job_infer_creation_result.id, retries=11, poll_wait=30)
    logger.info(infer_job_status)

    download_info = lumi_client_int.jobs.get_job_download(job_infer_creation_result.id)
    logger.info(f"getting result from {download_info.download_url}")
    requests.get(download_info.download_url, allow_redirects=True, timeout=10)

    infer_dataset = lumi_client_int.jobs.get_job_dataset(job_infer_creation_result.id)

    assert infer_dataset is not None

    eval_job_config = JobEvalConfig(
        metrics=["rouge", "meteor"],
    )
    eval_job = JobCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        dataset=str(infer_dataset.id),
        max_samples=10,
        job_config=eval_job_config,
    )
    logger.info(eval_job)

    job_eval_creation_result = lumi_client_int.jobs.create_job(eval_job)
    assert job_eval_creation_result is not None
    assert lumi_client_int.jobs.get_jobs() is not None

    eval_job_status = lumi_client_int.jobs.wait_for_job(job_eval_creation_result.id, retries=11, poll_wait=30)
    logger.info(eval_job_status)

    datasets = lumi_client_int.datasets.get_datasets()
    n_after_jobs_datasets = datasets.total
    assert n_after_jobs_datasets - n_before_jobs_datasets == 1

    infer_jobs_after = lumi_client_int.jobs.get_jobs_per_type(JobType.INFERENCE)
    assert infer_jobs_after is not None
    assert infer_jobs_after.total - infer_jobs_before.total == 1


@pytest.mark.parametrize(
    "dataset_name, dataset_fixture",
    [
        ("dialog", "dialog_data_unannotated"),
        ("mock_long_sequences", "long_sequences_data_unannotated"),
    ],
)
def test_jobs_annotate_create(lumi_client_int: LumigatorClient, dataset_name: str, dataset_fixture: str, request):
    # Clear existing datasets
    datasets = lumi_client_int.datasets.get_datasets()
    if datasets.total > 0:
        for removed_dataset in datasets.items:
            lumi_client_int.datasets.delete_dataset(removed_dataset.id)

    datasets = lumi_client_int.datasets.get_datasets()
    n_initial_datasets = datasets.total

    # Get the dataset from the fixture
    dataset = request.getfixturevalue(dataset_fixture)
    created_dataset = lumi_client_int.datasets.create_dataset(dataset=dataset, format=DatasetFormat.JOB)

    # Verify dataset creation
    datasets = lumi_client_int.datasets.get_datasets()
    n_current_datasets = datasets.total
    assert n_current_datasets - n_initial_datasets == 1

    annotate_job_config = JobAnnotateConfig(task_definition={"task": "summarization"}, model=TEST_SEQ2SEQ_MODEL)
    annotate_job = JobCreate(
        name="test_annotate",
        description="Test run for Huggingface model",
        dataset=str(created_dataset.id),
        max_samples=2,
        job_config=annotate_job_config,
    )

    logger.info(annotate_job)
    annotate_job_creation_result = lumi_client_int.jobs.create_job(annotate_job)
    assert annotate_job_creation_result is not None
    assert lumi_client_int.jobs.get_job(annotate_job_creation_result.id) is not None


@pytest.mark.parametrize(
    "dataset_name, task_definition, model",
    [
        ("dialog_data", {"task": "summarization"}, TEST_SEQ2SEQ_MODEL),
        (
            "mock_translation_data",
            {"task": "translation", "source_language": "en", "target_language": "de"},
            TEST_CAUSAL_MODEL,
        ),
    ],
)
def test_experiment_and_workflows_create(
    lumi_client_int: LumigatorClient, dataset_name: str, task_definition: dict, model: str, request
):
    """Test creating an experiment with associated workflows and checking results."""
    # Upload a dataset
    dataset = request.getfixturevalue(dataset_name)
    dataset_response = lumi_client_int.datasets.create_dataset(dataset=dataset, format=DatasetFormat.JOB)
    assert dataset_response is not None
    dataset_id = dataset_response.id

    # Create an experiment
    request = ExperimentCreate(
        name="test_experiment_and_workflows_create",
        description="Test for an experiment with associated workflows",
        task_definition=task_definition,
        dataset=dataset_id,
    )
    experiment_response = lumi_client_int.experiments.create_experiment(request)
    assert experiment_response is not None
    experiment_id = experiment_response.id

    # Create a workflow for the experiment
    request = WorkflowCreateRequest(
        name="SDK_Workflow_1",
        description="Test workflow for inf and eval",
        model=model,
        provider="hf",
        experiment_id=str(experiment_id),
    )

    # Get the results of the workflow & the experiment
    workflow_1_response = lumi_client_int.workflows.create_workflow(request)
    workflow_1_id = workflow_1_response.id
    workflow_1_details = lumi_client_int.workflows.get_workflow(workflow_1_id)
    experiment_results = lumi_client_int.experiments.get_experiment(experiment_id)

    assert workflow_1_response is not None
    assert workflow_1_details is not None
    assert experiment_results is not None
    logger.info(f"Workflow 1 details: {workflow_1_details}")
    logger.info(f"Experiment results: {experiment_results}")

    # Add another workflow to the experiment
    request = WorkflowCreateRequest(
        name="SDK_Workflow_2",
        description="Test workflow for inf and eval",
        model=model,
        provider="hf",
        experiment_id=str(experiment_id),
    )

    # Get the results of the workflow & the experiment
    workflow_2_response = lumi_client_int.workflows.create_workflow(request)
    workflow_2_id = workflow_2_response.id
    workflow_2_details = lumi_client_int.workflows.get_workflow(workflow_2_id)
    experiment_results = lumi_client_int.experiments.get_experiment(experiment_id)

    assert workflow_2_response is not None
    assert workflow_2_details is not None
    assert experiment_results is not None
    assert len(experiment_results.workflows) == 2
    logger.info(f"Workflow 2 details: {workflow_2_details}")
    logger.info(f"Experiment results: {experiment_results}")

    # Check the workflow ids in the experiment
    expected_workflow_ids = {workflow_1_id, workflow_2_id}
    experiment_workflow_ids = {w.id for w in experiment_results.workflows}
    assert experiment_workflow_ids == expected_workflow_ids

    # Get the logs
    logs_response = lumi_client_int.workflows.get_workflow_logs(workflow_1_details.id)
    assert logs_response is not None
    assert logs_response.logs is not None
