from pathlib import Path

from schemas.datasets import DatasetFormat
from loguru import logger

from tests.helpers import load_json, check_method


def test_get_datasets_remote_ok(lumi_client):
    datasets = lumi_client.datasets.get_datasets()
    assert datasets is not None


def test_dataset_lifecycle_remote_ok(lumi_client, hf_data):
    with Path.open(hf_data) as file:
        dataset = lumi_client.datasets.create_dataset(dataset=file, format=DatasetFormat.EXPERIMENT)
        datasets = lumi_client.datasets.get_datasets()
        assert datasets.total is not 0
        dataset = lumi_client.datasets.get_dataset(datasets.items[0].id)
        assert dataset is not None
        lumi_client.datasets.delete_dataset(datasets.items[0].id)
