import io
import json
from http import HTTPMethod, HTTPStatus
from pathlib import Path
from uuid import UUID

from lumigator_schemas.datasets import DatasetFormat
from lumigator_sdk.lm_datasets import Datasets
from pytest import raises
from requests.exceptions import HTTPError
from tests.helpers import load_json


def test_get_datasets_ok(lumi_client, json_data_datasets, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Datasets.DATASETS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=load_json(json_data_datasets),
    )

    datasets = lumi_client.datasets.get_datasets()
    assert datasets is not None


def test_get_datasets_none(lumi_client, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Datasets.DATASETS_ROUTE}",
        status_code=HTTPStatus.OK,
        json={"total": 0, "items": []},
    )

    datasets = lumi_client.datasets.get_datasets()
    assert datasets is not None
    assert datasets.total == 0
    assert datasets.items == []


def test_get_dataset_ok(lumi_client, json_data_dataset, request_mock):
    data = load_json(json_data_dataset)
    request_mock.get(
        url=lumi_client.client._api_url + f'/{Datasets.DATASETS_ROUTE}/{data["id"]}',
        status_code=HTTPStatus.OK,
        json=data,
    )

    dataset = lumi_client.datasets.get_dataset(UUID(data["id"]))
    assert dataset is not None


def test_delete_dataset_ok(lumi_client, json_data_dataset, request_mock):
    data = load_json(json_data_dataset)
    request_mock.delete(
        url=lumi_client.client._api_url + f'/{Datasets.DATASETS_ROUTE}/{data["id"]}',
        status_code=HTTPStatus.OK,
        json=data,
    )

    lumi_client.datasets.delete_dataset(UUID(data["id"]))


def test_delete_dataset_not_found(lumi_client, json_data_dataset, request_mock):
    data = load_json(json_data_dataset)
    request_mock.delete(
        url=lumi_client.client._api_url + f'/{Datasets.DATASETS_ROUTE}/{data["id"]}',
        status_code=HTTPStatus.NOT_FOUND,
        json=data,
    )

    with raises(HTTPError):
        lumi_client.datasets.delete_dataset(UUID(data["id"]))


def test_create_dataset_ok(lumi_client, json_data_dataset, request_mock):
    data = load_json(json_data_dataset)
    request_mock.post(
        url=lumi_client.client._api_url + f"/{Datasets.DATASETS_ROUTE}",
        status_code=HTTPStatus.CREATED,
        json=load_json(json_data_dataset),
    )

    content = io.BytesIO(bytearray(b"0" * 20))
    dataset = lumi_client.datasets.create_dataset(
        dataset=(data["filename"], content), format=DatasetFormat.JOB
    )
    assert dataset is not None
