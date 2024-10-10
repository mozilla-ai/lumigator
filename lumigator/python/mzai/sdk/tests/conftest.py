from pathlib import Path
import unittest.mock as mock

import pytest
import json

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
    with mock.patch("requests.request") as req_mock:
        with mock.patch("requests.Response") as resp_mock:
            resp_mock.status_code = 200
            resp_mock.json = lambda: json.loads('["openai", "mistral"]')
            req_mock.return_value = resp_mock
            return LumigatorClient(LUMI_HOST)


@pytest.fixture(scope="session")
def mock_vendor_data() -> str:
    return '["openai", "mistral"]'


def resources_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def json_data_deployments() -> Path:
    return resources_dir() / "deployments.json"


@pytest.fixture(scope="session")
def json_data_jobs() -> Path:
    return resources_dir() / "jobs.json"


@pytest.fixture(scope="session")
def json_data_job() -> Path:
    return resources_dir() / "job.json"


@pytest.fixture(scope="session")
def json_data_experiments() -> Path:
    return resources_dir() / "experiments.json"


@pytest.fixture(scope="session")
def json_data_experiment() -> Path:
    return resources_dir() / "experiment.json"


@pytest.fixture(scope="session")
def json_data_experiment_missing() -> Path:
    return resources_dir() / "experiment-missing.json"


@pytest.fixture(scope="session")
def json_data_experiment_post_response() -> Path:
    return resources_dir() / "experiment-post-response.json"


@pytest.fixture(scope="session")
def json_data_experiment_post_simple() -> Path:
    return resources_dir() / "experiment-post-simple.json"


@pytest.fixture(scope="session")
def json_data_experiment_post_all() -> Path:
    return resources_dir() / "experiment-post-all.json"


@pytest.fixture(scope="session")
def json_data_experiment_result() -> Path:
    return resources_dir() / "experiment-result.json"


@pytest.fixture(scope="session")
def json_data_experiment_result_missing() -> Path:
    return resources_dir() / "experiment-result-no-experiment.json"


@pytest.fixture(scope="session")
def json_data_experiment_result_download() -> Path:
    return resources_dir() / "experiment-download.json"


@pytest.fixture(scope="session")
def json_data_experiment_result_download_missing() -> Path:
    return resources_dir() / "experiment-download-no-experiment.json"
