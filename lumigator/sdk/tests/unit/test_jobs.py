import json
from http import HTTPStatus
from pathlib import Path

from lumigator_schemas.jobs import JobType
from lumigator_sdk.health import Health
from lumigator_sdk.jobs import Jobs
from lumigator_sdk.strict_schemas import (
    DatasetDownloadResponse,
    JobAnnotateConfig,
    JobCreate,
    JobEvalConfig,
    JobInferenceConfig,
)
from pydantic import ValidationError
from pytest import raises
from requests import Response
from requests.exceptions import HTTPError
from tests.helpers import load_json


def test_create_job_ok_all(lumi_client, json_data_job_response, json_data_job_all, request_mock):
    job_json = load_json(json_data_job_all)
    path = job_json["job_config"]["job_type"]

    request_mock.post(
        url=lumi_client.client._api_url + f"/{Jobs.JOBS_ROUTE}/{path}/",
        status_code=HTTPStatus.OK,
        json=load_json(json_data_job_response),
    )

    job_ret = lumi_client.jobs.create_job(JobCreate.model_validate(job_json))
    assert job_ret is not None
    assert str(job_ret.id) == "daab39ac-be9f-4de9-87c0-c4c94b297a97"
    assert job_ret.name == "test-job-001"
    assert job_ret.status == "created"


def test_create_job_ok_minimal(lumi_client, json_data_job_response, json_data_job_minimal, request_mock):
    job_json = load_json(json_data_job_minimal)
    path = job_json["job_config"]["job_type"]

    request_mock.post(
        url=lumi_client.client._api_url + f"/{Jobs.JOBS_ROUTE}/{path}/",
        status_code=HTTPStatus.OK,
        json=load_json(json_data_job_response),
    )

    job_ret = lumi_client.jobs.create_job(JobCreate.model_validate(job_json))
    assert job_ret is not None
    assert str(job_ret.id) == "daab39ac-be9f-4de9-87c0-c4c94b297a97"
    assert job_ret.name == "test-job-001"
    assert job_ret.status == "created"


def test_create_job_ok_extra(lumi_client, json_data_job_response, json_data_job_extra, request_mock):
    job_json = load_json(json_data_job_extra)
    path = job_json["job_config"]["job_type"]

    request_mock.post(
        url=lumi_client.client._api_url + f"/{Jobs.JOBS_ROUTE}/{path}/",
        status_code=HTTPStatus.OK,
        json=load_json(json_data_job_response),
    )

    with raises(ValidationError):
        lumi_client.jobs.create_job(JobCreate.model_validate(job_json))


def test_get_jobs_ok(lumi_client, json_data_jobs, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Jobs.JOBS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=load_json(json_data_jobs),
    )

    jobs = lumi_client.jobs.get_jobs()
    assert jobs is not None
    assert len(jobs.items) == jobs.total


def test_get_jobs_none(lumi_client, request_mock):
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Jobs.JOBS_ROUTE}",
        status_code=HTTPStatus.OK,
        json={"total": 0, "items": []},
    )

    jobs = lumi_client.jobs.get_jobs()
    assert jobs is not None
    assert jobs.items == []


def test_get_job_ok(lumi_client, json_data_job, request_mock):
    job_id = "6f6487ac-7170-4a11-af7a-0f6db1ec9a74"
    request_mock.get(
        url=lumi_client.client._api_url + f"/{Jobs.JOBS_ROUTE}/{job_id}",
        status_code=HTTPStatus.OK,
        json=load_json(json_data_job),
    )

    job = lumi_client.jobs.get_job(job_id)

    assert job is not None
    assert job.type == "SUBMISSION"
    assert job.status == "pending"
    assert job.submission_id == job_id


def test_get_job_id_does_not_exist(lumi_client, request_mock):
    job_id = "00000000-0000-0000-0000-000000000000"
    response = Response()
    response.status_code = HTTPStatus.NOT_FOUND
    response._content = b"Content not found"
    error = HTTPError(response=response)
    request_mock.get(url=lumi_client.client._api_url + f"/{Jobs.JOBS_ROUTE}/{job_id}", exc=error)

    # We expect the SDK to handle the 404 and return None.
    with raises(HTTPError) as exc_info:
        lumi_client.jobs.get_job(job_id)
    assert exc_info.value.response.text == response.text
