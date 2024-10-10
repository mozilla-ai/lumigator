import importlib.resources
import unittest.mock as mock

import pytest
import json

from importlib.resources.abc import Traversable
from lumigator import LumigatorClient

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
        yield req_mock


@pytest.fixture(scope="session")
def lumi_client() -> LumigatorClient:
    lumi_c = None
    with mock.patch("requests.request") as req_mock:
        with mock.patch("requests.Response") as resp_mock:
            resp_mock.status_code = 200
            resp_mock.json = lambda: json.loads('["openai", "mistral"]')
            req_mock.return_value = resp_mock
            lumi_c = LumigatorClient(LUMI_HOST)
    return lumi_c


@pytest.fixture(scope="session")
def mock_vendor_data() -> str:
    return '["openai", "mistral"]'


def json_data_path() -> Traversable:
    return importlib.resources.files("sdk.tests") / "data"


@pytest.fixture(scope="session")
def json_data_deployments() -> Traversable:
    return json_data_path() / "deployments.json"


@pytest.fixture(scope="session")
def json_data_jobs() -> Traversable:
    return json_data_path() / "jobs.json"


@pytest.fixture(scope="session")
def json_data_job() -> Traversable:
    return json_data_path() / "job.json"


@pytest.fixture(scope="session")
def json_data_experiments() -> Traversable:
    return json_data_path() / "experiments.json"


@pytest.fixture(scope="session")
def json_data_experiment() -> Traversable:
    return json_data_path() / "experiment.json"


@pytest.fixture(scope="session")
def json_data_experiment_post_response() -> Traversable:
    return json_data_path() / "experiment-post-response.json"


@pytest.fixture(scope="session")
def json_data_experiment_post_simple() -> Traversable:
    return json_data_path() / "experiment-post-simple.json"


@pytest.fixture(scope="session")
def json_data_experiment_post_all() -> Traversable:
    return json_data_path() / "experiment-post-all.json"
