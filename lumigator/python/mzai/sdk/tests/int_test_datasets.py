import asyncio
from pathlib import Path
from time import sleep

from loguru import logger
from schemas.datasets import DatasetFormat
from schemas.jobs import JobCreate, JobType

import requests

def test_sdk_healthcheck_ok(lumi_client):
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
    datasets = lumi_client.datasets.get_datasets()
    assert datasets is not None


def test_dataset_lifecycle_remote_ok(lumi_client, dialog_data):
    with Path.open(dialog_data) as file:
        datasets = lumi_client.datasets.get_datasets()
        before = datasets.total
        dataset = lumi_client.datasets.create_dataset(dataset=file, format=DatasetFormat.JOB)
        datasets = lumi_client.datasets.get_datasets()
        after = datasets.total
        dataset = lumi_client.datasets.get_dataset(datasets.items[0].id)
        assert dataset is not None
        lumi_client.datasets.delete_dataset(datasets.items[0].id)
        datasets = lumi_client.datasets.get_datasets()
        assert after - before == 1


def test_job_lifecycle_remote_ok(lumi_client, dialog_data):
    logger.info('Starting jobs lifecycle')
    with Path.open(dialog_data) as file:
        datasets = lumi_client.datasets.get_datasets()
        if datasets.total > 0:
            for remove_ds in datasets.items:
                logger.info(f"Removing dataset {remove_ds.id}")
                lumi_client.datasets.delete_dataset(remove_ds.id)
        datasets = lumi_client.datasets.get_datasets()
        before = datasets.total
        dataset = lumi_client.datasets.create_dataset(dataset=file, format=DatasetFormat.JOB)
        datasets = lumi_client.datasets.get_datasets()
        after = datasets.total
        assert after - before == 1

        jobs = lumi_client.jobs.get_jobs()
        assert jobs is not None
        logger.info(lumi_client.datasets.get_dataset(dataset.id))
        # job_create = JobCreate(name="test-job-int-001", model="hf://distilbert/distilbert-base-uncased", dataset=dataset.id)
        job_create = JobCreate(name="test-job-int-001", model="hf://distilgpt2", dataset=dataset.id)
        job_create.description = "This is a test job"
        job_create.max_samples = 0
        job_ret = lumi_client.jobs.create_job(JobType.EVALUATION, job_create)
        assert job_ret is not None
        jobs = lumi_client.jobs.get_jobs()
        assert jobs is not None
        assert len(jobs.items) == jobs.total

        job_status = asyncio.run(lumi_client.jobs.wait_for_job(job_ret.id))
        logger.info(job_status)

        download_info = lumi_client.jobs.get_job_download(job_ret.id)
        logger.info(f'getting result from {download_info.download_url}')
        results = requests.get(download_info.download_url, allow_redirects=True)
        logger.info(f'first 30 chars: {results.content[:30]}...')
