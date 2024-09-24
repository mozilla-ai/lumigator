import pytest

import requests

import unittest.mock as mock

from mzai.sdk.core import LumigatorClient

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
    def json(self):
        return self.json_data

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
def lumi_client() -> LumigatorClient :
    return LumigatorClient("localhost")

def test_sdk_healthcheck(mock_requests_response, lumi_client):
    mock_requests_response.return_value = requests.Response
    check = lumi_client.healthcheck()