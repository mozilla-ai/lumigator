import pytest

import requests

import unittest.mock as mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

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
def lumi_client() -> LumigatorClient :
    return LumigatorClient("localhost")

def test_sdk_healthcheck(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 500
    mock_requests_response.json = lambda: "{}"
    check = lumi_client.healthcheck()
    print(check)