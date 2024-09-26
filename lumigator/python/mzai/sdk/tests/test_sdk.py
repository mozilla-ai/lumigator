import pytest

from pytest import raises

import json
import unittest.mock as mock

from requests.exceptions import HTTPError

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
