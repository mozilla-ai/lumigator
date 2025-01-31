"""Integration tests for the SDK. The lumigator backend needs to
be started prior to running these tests using
`make start-lumigator-build`.
"""

from time import sleep
from uuid import UUID

import requests
from loguru import logger
from lumigator_schemas.datasets import DatasetFormat
from lumigator_schemas.jobs import JobType
from lumigator_schemas.workflows import WorkflowDetailsResponse, WorkflowStatus
from lumigator_sdk.lumigator import LumigatorClient
from lumigator_sdk.strict_schemas import (
    DatasetDownloadResponse,
    ExperimentIdCreate,
    JobAnnotateCreate,
    JobEvalCreate,
    WorkflowCreateRequest,
)


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
    dataset_response = lumi_client_int.datasets.create_dataset(
        dataset=dialog_data, format=DatasetFormat.JOB
    )

    assert dataset_response is not None
    assert isinstance(dataset_response.id, UUID)

    def sum_ends_with(download_response: DatasetDownloadResponse, extension: str):
        return sum(
            1
            for u in download_response.download_urls
            if len(u.split("?")) == 2 and u.split("?")[0].endswith(extension)
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


def test_job_lifecycle_remote_ok(
    lumi_client_int: LumigatorClient, dialog_data, simple_eval_template
):
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

    job = JobEvalCreate(
        name="test-job-int-001",
        model="hf://hf-internal-testing/tiny-random-LlamaForCausalLM",
        dataset=dataset.id,
        config_template=simple_eval_template,
    )
    logger.info(job)
    job.description = "This is a test job"
    job.max_samples = 2
    job_creation_result = lumi_client_int.jobs.create_job(JobType.EVALUATION, job)
    assert job_creation_result is not None
    assert lumi_client_int.jobs.get_jobs() is not None

    job_status = lumi_client_int.jobs.wait_for_job(job_creation_result.id, retries=11, poll_wait=30)
    logger.info(job_status)

    download_info = lumi_client_int.jobs.get_job_download(job_creation_result.id)
    logger.info(f"getting result from {download_info.download_url}")
    requests.get(download_info.download_url, allow_redirects=True, timeout=10)


def test_annotate_dataset(lumi_client_int: LumigatorClient, dialog_data_unannotated):
    datasets = lumi_client_int.datasets.get_datasets()
    if datasets.total > 0:
        for removed_dataset in datasets.items:
            lumi_client_int.datasets.delete_dataset(removed_dataset.id)
    datasets = lumi_client_int.datasets.get_datasets()
    n_initial_datasets = datasets.total
    dataset = lumi_client_int.datasets.create_dataset(
        dataset=dialog_data_unannotated, format=DatasetFormat.JOB
    )
    datasets = lumi_client_int.datasets.get_datasets()
    n_current_datasets = datasets.total
    assert n_current_datasets - n_initial_datasets == 1

    job = JobAnnotateCreate(
        name="test_annotate",
        description="Test run for Huggingface model",
        dataset=str(dataset.id),
        max_samples=2,
        task="summarization",
    )
    logger.info(job)
    job_creation_result = lumi_client_int.jobs.create_job(JobType.ANNOTATION, job)
    assert job_creation_result is not None
    assert lumi_client_int.jobs.get_jobs() is not None

    job_status = lumi_client_int.jobs.wait_for_job(job_creation_result.id, retries=11, poll_wait=30)
    logger.info(job_status)

    download_info = lumi_client_int.jobs.get_job_download(job_creation_result.id)
    logger.info(f"getting result from {download_info.download_url}")
    results = requests.get(download_info.download_url, allow_redirects=True, timeout=10)
    logger.info(f"Annotated set has keys: {results.json().keys()}")
    assert "ground_truth" in results.json().keys()


def wait_for_workflow_complete(lumi_client_int: LumigatorClient, workflow_id: UUID):
    """Wait for a workflow to complete."""
    workflow_details = lumi_client_int.workflows.get_workflow(workflow_id)
    while workflow_details.status not in [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]:
        sleep(5)
        workflow_details = lumi_client_int.workflows.get_workflow(workflow_id)
    return workflow_details


def test_create_exp_workflow_check_results(lumi_client_int: LumigatorClient, dialog_data):
    """Test creating an experiment with associated workflows and checking results."""
    # Upload a dataset
    dataset_response = lumi_client_int.datasets.create_dataset(
        dataset=dialog_data, format=DatasetFormat.JOB
    )
    assert dataset_response is not None
    dataset_id = dataset_response.id

    # Create an experiment
    request = ExperimentIdCreate(
        name="test_create_exp_workflow_check_results",
        description="Test for an experiment with associated workflows",
    )
    experiment_response = lumi_client_int.experiments.create_experiment(request)
    assert experiment_response is not None
    experiment_id = experiment_response.id

    # Create a workflow for the experiment
    request = WorkflowCreateRequest(
        name="Workflow_1",
        description="Test workflow for inf and eval",
        model="hf://hf-internal-testing/tiny-random-LlamaForCausalLM",
        dataset=str(dataset_id),
        experiment_id=str(experiment_id),
        max_samples=1,
    )
    workflow_1_response = lumi_client_int.workflows.create_workflow(request)
    assert workflow_1_response is not None
    workflow_1_id = workflow_1_response.id

    # Wait till the workflow is done
    workflow_1_details = wait_for_workflow_complete(lumi_client_int, workflow_1_id)

    # Get the results of the experiment
    experiment_results = lumi_client_int.experiments.get_experiment(experiment_id)
    assert experiment_results is not None
    assert workflow_1_details.experiment_id == experiment_results.id
    assert len(experiment_results.workflows) == 1
    assert workflow_1_details.model_dump(
        exclude={"artifacts_download_url"}
    ) == experiment_results.workflows[0].model_dump(exclude={"artifacts_download_url"})

    # Add another workflow to the experiment
    request = WorkflowCreateRequest(
        name="Workflow_2",
        description="Test workflow for inf and eval",
        model="hf://hf-internal-testing/tiny-random-LlamaForCausalLM",
        dataset=str(dataset_id),
        experiment_id=str(experiment_id),
        max_samples=1,
    )

    workflow_2_response = lumi_client_int.workflows.create_workflow(request)
    assert workflow_2_response is not None
    workflow_2_id = workflow_2_response.id

    # Wait till the workflow is done
    workflow_2_details = wait_for_workflow_complete(lumi_client_int, workflow_2_id)

    # Get the results of the experiment
    experiment_results = lumi_client_int.experiments.get_experiment(experiment_id)
    assert experiment_results is not None
    assert len(experiment_results.workflows) == 2
    assert workflow_1_details.model_dump(exclude={"artifacts_download_url"}) in [
        w.model_dump(exclude={"artifacts_download_url"}) for w in experiment_results.workflows
    ]
    assert workflow_2_details.model_dump(exclude={"artifacts_download_url"}) in [
        w.model_dump(exclude={"artifacts_download_url"}) for w in experiment_results.workflows
    ]

    # Get the logs
    logs_response = lumi_client_int.workflows.get_workflow_logs(workflow_1_details.id)
    assert logs_response is not None
    assert logs_response.logs is not None
    assert "Inference results stored at" in logs_response.logs
    assert "Storing evaluation results into" in logs_response.logs
    assert logs_response.logs.index("Inference results stored at") < logs_response.logs.index(
        "Storing evaluation results into"
    )

    # Delete the experiment
    lumi_client_int.experiments.delete_experiment(experiment_id)
    #  shoudl throw exeption: lumi_client_int.experiments.get_experiment(experiment_id)
    try:
        lumi_client_int.experiments.get_experiment(experiment_id)
        raise Exception("Should have thrown an exception")
    except requests.exceptions.HTTPError:
        pass

    try:
        lumi_client_int.workflows.get_workflow(workflow_1_details.id)
        raise Exception("Should have thrown an exception")
    except requests.exceptions.HTTPError:
        pass

    try:
        lumi_client_int.workflows.get_workflow(workflow_2_details.id)
        raise Exception("Should have thrown an exception")
    except requests.exceptions.HTTPError:
        pass
