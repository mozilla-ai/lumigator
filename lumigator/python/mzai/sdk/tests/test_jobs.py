import json
from http import HTTPStatus
from pathlib import Path

from lumigator_sdk.strict_schemas import JobEvalCreate
from lumigator_schemas.jobs import JobType
from pytest import raises
from requests.exceptions import HTTPError

from tests.helpers import load_json


def test_create_job_ok_all(
    mock_requests_response, mock_requests, lumi_client, json_data_job_response, json_data_job_all
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_job_response)
    mock_requests_response.json = lambda: data

    job_json = load_json(json_data_job_all)
    job_ret = lumi_client.jobs.create_job(
        JobType.EVALUATION, JobEvalCreate.model_validate(job_json)
    )
    assert job_ret is not None
    assert str(job_ret.id) == "daab39ac-be9f-4de9-87c0-c4c94b297a97"
    assert job_ret.name == "test-job-001"
    assert job_ret.status == "created"


def test_create_job_ok_minimal(
    mock_requests_response,
    mock_requests,
    lumi_client,
    json_data_job_response,
    json_data_job_minimal,
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_job_response)
    mock_requests_response.json = lambda: data

    job_json = load_json(json_data_job_minimal)
    job_ret = lumi_client.jobs.create_job(JobType.INFERENCE, JobEvalCreate.model_validate(job_json))
    assert job_ret is not None
    assert str(job_ret.id) == "daab39ac-be9f-4de9-87c0-c4c94b297a97"
    assert job_ret.name == "test-job-001"
    assert job_ret.status == "created"


def test_create_job_ok_extra(
    mock_requests_response,
    mock_requests,
    lumi_client,
    json_data_job_response,
    json_data_job_extra,
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_job_response)
    mock_requests_response.json = lambda: data

    job_json = load_json(json_data_job_extra)
    with raises(BaseException):
        job_ret = lumi_client.jobs.create_job(JobType.INFERENCE, JobEvalCreate.model_validate(job_json))


def test_get_jobs_ok(mock_requests_response, mock_requests, lumi_client, json_data_jobs):
    mock_requests_response.status_code = 200
    data = load_json(json_data_jobs)
    mock_requests_response.json = lambda: data

    jobs = lumi_client.jobs.get_jobs()
    assert jobs is not None
    assert len(jobs.items) == jobs.total


def test_get_jobs_none(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    mock_requests_response.json = lambda: json.loads('{"total":0,"items":[]}')

    jobs = lumi_client.jobs.get_jobs()
    assert jobs is not None
    assert jobs.items == []


def test_get_job_ok(mock_requests_response, mock_requests, lumi_client, json_data_job):
    mock_requests_response.status_code = 200
    data = load_json(json_data_job)
    mock_requests_response.json = lambda: data

    job_id = "6f6487ac-7170-4a11-af7a-0f6db1ec9a74"
    job = lumi_client.health.get_job(job_id)

    assert job is not None
    assert job.type == "SUBMISSION"
    assert job.status == "PENDING"
    assert job.submission_id == job_id


def test_get_job_id_does_not_exist(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = HTTPStatus.NOT_FOUND
    mock_requests_response.json = lambda: None
    error = HTTPError(response=mock_requests_response)
    mock_requests.side_effect = error

    # We expect the SDK to handle the 404 and return None.
    job = lumi_client.health.get_job("00000000-0000-0000-0000-000000000000")
    assert job is None
