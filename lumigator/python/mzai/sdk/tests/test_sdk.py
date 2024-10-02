import importlib.resources
import json
import unittest.mock as mock
from pathlib import Path

import pytest
from pytest import fail, raises
from requests.exceptions import HTTPError

from mzai.schemas.datasets import DatasetResponse
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
        yield req_mock

@pytest.fixture(scope="session")
def lumi_client() -> LumigatorClient:
    return LumigatorClient("localhost")

def test_sdk_healthcheck_ok(mock_requests_response, mock_requests, lumi_client):
    deployment_type = "local"
    status = "ok"
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads(f'{{"deployment_type": "{deployment_type}", "status": "{status}"}}')
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
    assert check.deployment_type == None

def test_get_datasets_ok(mock_requests_response, mock_requests, lumi_client):
    datasets = [
        DatasetResponse(id="daab39ac-be9f-4de9-87c0-c4c94b297a97",filename="ds1.hf",format="experiment",size=16,created_at="2024-09-26T11:52:05"),
        DatasetResponse(id="e3be6e4b-dd1e-43b7-a97b-0d47dcc49a4f",filename="ds2.hf",format="experiment",size=16,created_at="2024-09-26T11:52:05"),
        DatasetResponse(id="1e23ed9f-b193-444e-8427-e2119a08b0d8",filename="ds3.hf",format="experiment",size=16,created_at="2024-09-26T11:52:05")
    ]
    datasets_json = json.dumps(datasets)
    print(datasets_json)
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: datasets_json
    check = lumi_client.healthcheck()
    fail

def test_get_jobs_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200

    ref = importlib.resources.files('mzai.sdk.tests') / 'data/jobs.json'
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data

    jobs = lumi_client.get_jobs()

    assert jobs is not None
    assert len(jobs) == 2
    assert jobs[0].message == "I am the message"
    assert jobs[1].message == "I am another message"

def test_get_job_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200

    ref = importlib.resources.files('mzai.sdk.tests') / 'data/job.json'
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data

    job = lumi_client.get_job("123")

    # Test some properties
    assert job is not None
    assert job.type == "SUBMISSION"
    assert job.submission_id == "6f6487ac-7170-4a11-af7a-0f6db1ec9a74"
