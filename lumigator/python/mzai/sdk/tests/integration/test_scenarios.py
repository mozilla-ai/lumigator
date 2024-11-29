"""Integration tests for the SDK. The lumigator backend needs to
be started prior to running these tests using
`make start-lumigator-build`.
"""

from pathlib import Path
from time import sleep

import requests
from loguru import logger
from lumigator_schemas.datasets import DatasetFormat
from lumigator_schemas.jobs import JobType
from lumigator_sdk.strict_schemas import JobEvalCreate


def test_sdk_healthcheck_ok(lumi_client):
    """Test the healthcheck endpoint."""
    healthy = False
    for i in range(10):
        try:
            lumi_client.health.healthcheck()
            healthy = True
            break
        except Exception as e:
            print(f"failed health check, retry {i} - due to {e}")
            sleep(1)
    assert healthy


def test_get_datasets_remote_ok(lumi_client):
    """Test the `get_datasets` endpoint."""
    datasets = lumi_client.datasets.get_datasets()
    assert datasets is not None


def test_dataset_lifecycle_remote_ok(lumi_client, dialog_data):
    """Test a complete dataset lifecycle test: add a new dataset,
    list datasets, remove the dataset
    """
    datasets = lumi_client.datasets.get_datasets()
    n_initial_datasets = datasets.total
    lumi_client.datasets.create_dataset(dataset=dialog_data, format=DatasetFormat.JOB)
    datasets = lumi_client.datasets.get_datasets()
    n_current_datasets = datasets.total
    created_dataset = lumi_client.datasets.get_dataset(datasets.items[0].id)
    assert created_dataset is not None
    lumi_client.datasets.delete_dataset(datasets.items[0].id)
    datasets = lumi_client.datasets.get_datasets()
    assert n_current_datasets - n_initial_datasets == 1


def test_job_lifecycle_remote_ok(lumi_client, dialog_data, simple_eval_template):
    """Test a complete job lifecycle test: add a new dataset,
    create a new job, run the job, get the results
    """
    logger.info("Starting jobs lifecycle")
    datasets = lumi_client.datasets.get_datasets()
    if datasets.total > 0:
        for removed_dataset in datasets.items:
            lumi_client.datasets.delete_dataset(removed_dataset.id)
    datasets = lumi_client.datasets.get_datasets()
    n_initial_datasets = datasets.total
    dataset = lumi_client.datasets.create_dataset(dataset=dialog_data, format=DatasetFormat.JOB)
    datasets = lumi_client.datasets.get_datasets()
    n_current_datasets = datasets.total
    assert n_current_datasets - n_initial_datasets == 1

    jobs = lumi_client.jobs.get_jobs()
    assert jobs is not None
    logger.info(lumi_client.datasets.get_dataset(dataset.id))

    job = JobEvalCreate(
        name="test-job-int-001",
        model="hf://trl-internal-testing/tiny-random-LlamaForCausalLM",
        dataset=dataset.id,
        config_template=simple_eval_template,
    )
    logger.info(job)
    job.description = "This is a test job"
    job.max_samples = 2
    job_creation_result = lumi_client.jobs.create_job(JobType.EVALUATION, job)
    assert job_creation_result is not None
    assert lumi_client.jobs.get_jobs() is not None

    job_status = lumi_client.jobs.wait_for_job(job_creation_result.id)
    logger.info(job_status)

    download_info = lumi_client.jobs.get_job_download(job_creation_result.id)
    logger.info(f"getting result from {download_info.download_url}")
    requests.get(download_info.download_url, allow_redirects=True)
