from pathlib import Path

import json

from tests.helpers import load_request


def test_get_datasets_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    data = load_request("data/datasets.json")
    mock_requests_response.json = lambda: data

    datasets = lumi_client.datasets.get_datasets()
    assert datasets is not None


def test_get_datasets_none(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads("[]")

    datasets = lumi_client.datasets.get_datasets()
    assert datasets is not None
    assert datasets == []


def test_get_dataset_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    data = load_request("data/dataset.json")
    mock_requests_response.json = lambda: data

    dataset = lumi_client.datasets.get_dataset(data["id"])
    assert dataset is not None


bytearray([1] * 100)
