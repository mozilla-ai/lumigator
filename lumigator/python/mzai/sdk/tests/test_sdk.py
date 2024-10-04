import importlib.resources
import json
import unittest.mock as mock
from http import HTTPStatus
from pathlib import Path

import pytest
from pytest import fail, raises
from requests.exceptions import HTTPError

from mzai.backend.schemas.datasets import DatasetResponse, DatasetResponseList
from mzai.backend.schemas.deployments import (
    DeploymentEvent,
    DeploymentEventList,
    DeploymentStatus,
    DeploymentType,
)
from mzai.sdk.core import LumigatorClient


@pytest.fixture(scope="function")
def mock_requests_response():
    """Mocks calls to `requests.Response`."""
    with mock.patch("requests.Response") as resp_mock:
        yield resp_mock


@pytest.fixture(scope="function")
def mock_requests(mock_requests_response):
    """Mocks calls to `requests.request`."""
    with mock.patch("requests.request") as req_mock:
        req_mock.return_value = mock_requests_response
        # TODO write a side effect to check the url
        yield req_mock


@pytest.fixture(scope="session")
def lumi_client() -> LumigatorClient:
    return LumigatorClient("localhost")


def check_url(check_url, **kwargs):
    print(f'the url used is {check_url} vs {kwargs["url"]}')
    return mock.DEFAULT


def test_sdk_healthcheck_ok(mock_requests_response, mock_requests, lumi_client):
    deployment_type = "local"
    status = "ok"
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads(
        f'{{"deployment_type": "{deployment_type}", "status": "{status}"}}'
    )
    mock_requests.side_effect = lambda **kwargs: check_url("/health", **kwargs)
    check = lumi_client.healthcheck()
    assert check.status == status
    assert check.deployment_type == deployment_type


def test_sdk_healthcheck_server_error(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 500
    mock_requests_response.json = lambda: None
    error = HTTPError(response=mock_requests_response)
    mock_requests.side_effect = error
    with raises(HTTPError):
        lumi_client.healthcheck()


def test_sdk_healthcheck_missing_deployment(mock_requests_response, mock_requests, lumi_client):
    status = "ok"
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads(f'{{"status": "{status}"}}')
    check = lumi_client.healthcheck()
    assert check.status == status
    assert check.deployment_type is None


def test_get_datasets_ok(mock_requests_response, mock_requests, lumi_client):
    datasets = [
        DatasetResponse(
            id="daab39ac-be9f-4de9-87c0-c4c94b297a97",
            filename="ds1.hf",
            format="experiment",
            size=16,
            created_at="2024-09-26T11:52:05",
        ),
        DatasetResponse(
            id="e3be6e4b-dd1e-43b7-a97b-0d47dcc49a4f",
            filename="ds2.hf",
            format="experiment",
            size=16,
            created_at="2024-09-26T11:52:05",
        ),
        DatasetResponse(
            id="1e23ed9f-b193-444e-8427-e2119a08b0d8",
            filename="ds3.hf",
            format="experiment",
            size=16,
            created_at="2024-09-26T11:52:05",
        ),
    ]
    datasets_list_json = DatasetResponseList(datasets).model_dump_json()
    print(f"datasets: {datasets_list_json}")
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads(datasets_list_json)
    datasets_ret = lumi_client.get_datasets()
    assert datasets_ret is not None


def test_get_deployments_ok(mock_requests_response, mock_requests, lumi_client):
    deployments = [
        DeploymentEvent(
            deployment_id="daab39ac-be9f-4de9-87c0-c4c94b297a97",
            deployment_type=DeploymentType.GROUNDTRUTH,
            status=DeploymentStatus.CREATED,
            detail="some details",
        ),
        DeploymentEvent(
            deployment_id="e3be6e4b-dd1e-43b7-a97b-0d47dcc49a4f",
            deployment_type=DeploymentType.GROUNDTRUTH,
            status=DeploymentStatus.RUNNING,
        ),
        DeploymentEvent(
            deployment_id="1e23ed9f-b193-444e-8427-e2119a08b0d8",
            deployment_type=DeploymentType.GROUNDTRUTH,
            status=DeploymentStatus.SUCCEEDED,
        ),
    ]
    deployments_list_json = DeploymentEventList(deployments).model_dump_json()
    print(f"datasets: {deployments_list_json}")
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads(deployments_list_json)
    deployments_ret = lumi_client.get_deployments()
    assert deployments_ret is not None


def test_get_jobs_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200

    ref = importlib.resources.files("mzai.sdk.tests") / "data/jobs.json"
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data

    jobs = lumi_client.get_jobs()

    assert jobs is not None
    assert len(jobs) == 2
    assert jobs[0].message == "I am the message"
    assert jobs[1].message == "I am another message"


def test_get_jobs_none(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads("[]")

    jobs = lumi_client.get_jobs()
    assert jobs is not None
    assert jobs == []


def test_get_job_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200

    ref = importlib.resources.files("mzai.sdk.tests") / "data/job.json"
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data

    job_id = "6f6487ac-7170-4a11-af7a-0f6db1ec9a74"
    job = lumi_client.get_job(job_id)

    # Test some properties
    assert job is not None
    assert job.type == "SUBMISSION"
    assert job.submission_id == job_id


def test_get_job_id_does_not_exist(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = HTTPStatus.NOT_FOUND
    mock_requests_response.json = lambda: None
    error = HTTPError(response=mock_requests_response)
    mock_requests.side_effect = error

    # We expect the SDK to handle the 404 and return None.
    job = lumi_client.get_job("6f6487ac-7170-4a11-af7a-0f6db1ec9a74")
    assert job is None


def test_get_vendors_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads('["openai", "mistral"]')

    vendors = lumi_client.get_vendors()

    assert vendors is not None
    assert len(vendors) == 2
    assert vendors[0] == "openai"
    assert vendors[1] == "mistral"


def test_get_vendors_none(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads("[]")

    vendors = lumi_client.get_vendors()
    assert vendors is not None
    assert vendors == []
