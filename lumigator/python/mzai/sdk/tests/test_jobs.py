import importlib.resources
import json
from http import HTTPStatus
from pathlib import Path

from requests.exceptions import HTTPError


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