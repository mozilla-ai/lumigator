import unittest.mock as mock

import pytest

from sdk.lumigator import LumigatorClient

LUMI_HOST = "localhost"


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
    return LumigatorClient(LUMI_HOST)
