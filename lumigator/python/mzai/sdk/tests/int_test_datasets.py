from pathlib import Path
from time import sleep

from schemas.datasets import DatasetFormat
from loguru import logger

from tests.helpers import load_json, check_method


def test_sdk_healthcheck_ok(lumi_client):
    healthy = False
    for i in range(10):
        try:
            lumi_client.health.healthcheck()
            healthy = True
            break
        except Exception as e:
            print(f'failed health check, retry {i} - due to {e}')
            sleep(1)
    assert healthy


def test_get_datasets_remote_ok(lumi_client):
    datasets = lumi_client.datasets.get_datasets()
    assert datasets is not None


def test_dataset_lifecycle_remote_ok(lumi_client, dialog_data):
    with Path.open(dialog_data) as file:
        datasets = lumi_client.datasets.get_datasets()
        assert datasets.total is 0
        dataset = lumi_client.datasets.create_dataset(dataset=file, format=DatasetFormat.EXPERIMENT)
        datasets = lumi_client.datasets.get_datasets()
        assert datasets.total is 1
        dataset = lumi_client.datasets.get_dataset(datasets.items[0].id)
        assert dataset is not None
        lumi_client.datasets.delete_dataset(datasets.items[0].id)
        datasets = lumi_client.datasets.get_datasets()
        assert datasets.total is 0
