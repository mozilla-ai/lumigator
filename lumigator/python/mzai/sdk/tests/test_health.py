import importlib.resources
import json
from http import HTTPStatus
from pathlib import Path

from pytest import raises
from requests.exceptions import HTTPError

from mzai.backend.schemas.datasets import DatasetResponse, DatasetResponseList
from mzai.backend.schemas.deployments import (
    DeploymentEvent,
    DeploymentEventList,
    DeploymentStatus,
    DeploymentType,
)
from mzai.sdk.client import ApiClient

LUMI_HOST="localhost"

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
    return ApiClient()

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


def test_sdk_healthcheck_ok(mock_requests_response, mock_requests, api_client):
    deployment_type = "local"
    status = "ok"
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads(
        f'{{"deployment_type": "{deployment_type}", "status": "{status}"}}'
    )
    check = api_client.health.healthcheck()
    assert check.status == status
    assert check.deployment_type == deployment_type


def test_sdk_healthcheck_server_error(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 500
    mock_requests_response.json = lambda: None
    error = HTTPError(response=mock_requests_response)
    mock_requests.side_effect = error
    with raises(HTTPError):
        api_client.health.healthcheck()


def test_sdk_healthcheck_missing_deployment(mock_requests_response, mock_requests, api_client):
    status = "ok"
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads(f'{{"status": "{status}"}}')
    check = api_client.health.healthcheck()
    assert check.status == status
    assert check.deployment_type is None


def test_get_deployments_ok(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 200

    ref = importlib.resources.files("mzai.sdk.tests") / "data/deployments.json"
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data

    deployments_ret = api_client.health.get_deployments()
    assert deployments_ret is not None


def test_get_jobs_ok(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 200

    ref = importlib.resources.files("mzai.sdk.tests") / "data/jobs.json"
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data

    jobs = api_client.health.get_jobs()

    assert jobs is not None
    assert len(jobs) == 2
    assert jobs[0].message == "I am the message"
    assert jobs[1].message == "I am another message"


def test_get_jobs_none(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads("[]")

    jobs = api_client.health.get_jobs()
    assert jobs is not None
    assert jobs == []


def test_get_job_ok(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 200

    ref = importlib.resources.files("mzai.sdk.tests") / "data/job.json"
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data

    job_id = "6f6487ac-7170-4a11-af7a-0f6db1ec9a74"
    job = api_client.health.get_job(job_id)

    # Test some properties
    assert job is not None
    assert job.type == "SUBMISSION"
    assert job.submission_id == job_id


def test_get_job_id_does_not_exist(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = HTTPStatus.NOT_FOUND
    mock_requests_response.json = lambda: None
    error = HTTPError(response=mock_requests_response)
    mock_requests.side_effect = error

    # We expect the SDK to handle the 404 and return None.
    job = api_client.health.get_job("6f6487ac-7170-4a11-af7a-0f6db1ec9a74")
    assert job is None


def test_get_vendors_ok(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads('["openai", "mistral"]')

    vendors = api_client.get_vendors()

    assert vendors is not None
    assert len(vendors) == 2
    assert vendors[0] == "openai"
    assert vendors[1] == "mistral"


def test_get_vendors_none(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads("[]")

    vendors = api_client.get_vendors()
    assert vendors is not None
    assert vendors == []


def test_get_experiments_ok(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 200
    load_response(mock_requests_response, "data/experiments.json")
    experiments_ret = api_client.get_experiments()
    assert experiments_ret is not None


def test_get_experiment_ok(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 200
    load_response(mock_requests_response, "data/experiment.json")
    experiment_ret = api_client.get_experiment()
    assert experiment_ret is not None


def test_create_experiment_ok_simple(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 200
    load_response(mock_requests_response, "data/experiment-post-response.json")
    experiment_ret = api_client.create_experiment(load_request("data/experiment-post-simple.json"))
    assert experiment_ret is not None


def test_create_experiment_ok_all(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 200
    load_response(mock_requests_response, "data/experiment-post-response.json")
    experiment_ret = api_client.create_experiment(load_request("data/experiment-post-all.json"))
    assert experiment_ret is not None

