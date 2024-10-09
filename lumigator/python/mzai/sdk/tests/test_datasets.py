from pathlib import Path

import json
import io
from schemas.datasets import DatasetFormat
from http import HTTPMethod

from tests.helpers import load_json, check_method


def test_get_datasets_ok(mock_requests_response, mock_requests, lumi_client, json_data_datasets):
    mock_requests_response.status_code = 200
    data = load_json(json_data_datasets)
    mock_requests_response.json = lambda: data

    datasets = lumi_client.datasets.get_datasets()
    assert datasets is not None


def test_get_datasets_none(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads("[]")

    datasets = lumi_client.datasets.get_datasets()
    assert datasets is not None
    assert datasets == []


def test_get_dataset_ok(mock_requests_response, mock_requests, lumi_client, json_data_dataset):
    mock_requests_response.status_code = 200
    data = load_json(json_data_dataset)
    mock_requests_response.json = lambda: data

    dataset = lumi_client.datasets.get_dataset(data["id"])
    assert dataset is not None


def test_delete_dataset_ok(mock_requests_response, mock_requests, lumi_client, json_data_dataset):
    mock_requests_response.status_code = 204
    data = load_json(json_data_dataset)
    mock_requests_response.json = lambda: None
    mock_requests.side_effect = lambda **kwargs: check_method(str(HTTPMethod.DELETE), **kwargs)

    lumi_client.datasets.delete_dataset(data["id"])


def test_delete_dataset_not_found(
    mock_requests_response, mock_requests, lumi_client, json_data_dataset
):
    mock_requests_response.status_code = 404
    data = load_json(json_data_dataset)
    mock_requests_response.json = lambda: None
    mock_requests.side_effect = lambda **kwargs: check_method(str(HTTPMethod.DELETE), **kwargs)

    lumi_client.datasets.delete_dataset(data["id"])


def test_create_dataset_ok(mock_requests_response, mock_requests, lumi_client, json_data_dataset):
    mock_requests_response.status_code = 201
    data = load_json(json_data_dataset)
    mock_requests_response.json = lambda: data
    mock_requests.side_effect = lambda **kwargs: check_method(str(HTTPMethod.POST), **kwargs)

    content = io.BytesIO(bytearray(b"0" * 20))
    dataset = lumi_client.datasets.create_dataset(
        dataset=(data["filename"], content), format=DatasetFormat.EXPERIMENT
    )
    assert dataset is not None
