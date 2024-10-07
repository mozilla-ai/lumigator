import unittest.mock as mock
import importlib.resources
import json

import pytest

from client import ApiClient
from pathlib import Path

LUMI_HOST="localhost"

def load_response(mock_requests_response: mock.Mock, path: str):
    ref = importlib.resources.files("mzai.sdk.tests") / path
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data

def load_request(path: str) -> str:
    ref = importlib.resources.files("mzai.sdk.tests") / path
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            return(json.load(file))

def check_url(check_url, **kwargs):
    print(f'the url used is {check_url} vs {kwargs["url"]}')
    assert check_url == kwargs["url"]
    return mock.DEFAULT

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
def api_client() -> ApiClient:
    return ApiClient(LUMI_HOST)