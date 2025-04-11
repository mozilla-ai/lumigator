import json
import re
import urllib
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

import loguru
from fastapi import status
from fastapi.testclient import TestClient
from lumigator_schemas.jobs import JobInferenceConfig, JobInferenceCreate, JobType

from backend.services.exceptions.secret_exceptions import SecretNotFoundError
from backend.settings import settings

POST_HEADER = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


def load_json(path: Path) -> str:
    with Path.open(path) as file:
        return json.load(file)


def test_get_job_status(
    test_client: TestClient,
    job_repository,
    request_mock,
    json_ray_version,
    json_data_health_job_metadata_ray,
    dependency_overrides_fakes,
):
    created_job = job_repository.create(name="test", description="test desc", job_type=JobType.INFERENCE)

    # The Ray client will call the Ray API to get the version before getting the job status
    # Mock the Ray version API
    request_mock.get(
        url=settings.RAY_VERSION_URL,
        status_code=status.HTTP_200_OK,
        text=json.dumps(load_json(json_ray_version)),
    )

    request_mock.get(
        url=urllib.parse.urljoin(f"{settings.RAY_JOBS_URL}", f"{created_job.id}"),
        status_code=status.HTTP_200_OK,
        text=json.dumps(load_json(json_data_health_job_metadata_ray)),
    )

    response = test_client.get(f"/jobs/{created_job.id}")

    assert response is not None
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"].lower() == "running"
    assert data["name"] == "test"
    assert data["description"] == "test desc"
    assert data["type"] == "SUBMISSION"
    assert data["id"] == str(created_job.id)
    assert data["driver_agent_http_address"] == "http://172.18.0.3:52365"


def test_get_job_results(
    test_client: TestClient,
    job_repository,
    request_mock,
    json_ray_version,
    json_data_health_job_metadata_ray,
    dependency_overrides_fakes,
):
    created_job = job_repository.create(name="test", description="")
    expected_url_path = f"lumigator-storage/jobs/results/test/{created_job.id}/results.json"
    # The Ray client will call the Ray API to get the version during initialization
    request_mock.get(
        url=settings.RAY_VERSION_URL,
        status_code=status.HTTP_200_OK,
        text=json.dumps(load_json(json_ray_version)),
    )
    response = test_client.get(f"/jobs/{created_job.id}/result/download")
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    download_url = response_json["download_url"]
    match = re.search(r"lumigator-storage/.+?\.json", download_url)
    extracted_url_path = match.group(0) if match else None
    assert extracted_url_path == expected_url_path


def test_job_logs(
    test_client: TestClient,
    job_repository,
    request_mock,
    json_ray_version,
    dependency_overrides_fakes,
):
    created_job = job_repository.create(name="test", description="")
    log = "2024-11-13 02:00:08,889\\tINFO job_manager.py:530 -- Runtime env is setting up.\\n"
    logs_content = f'{{"logs": "{log}"}}'

    request_mock.get(
        url=urllib.parse.urljoin(f"{settings.RAY_JOBS_URL}", f"{created_job.id}/logs"),
        status_code=status.HTTP_200_OK,
        text=logs_content,
    )
    request_mock.get(
        url=settings.RAY_VERSION_URL,
        status_code=status.HTTP_200_OK,
        text=json.dumps(load_json(json_ray_version)),
    )
    response = test_client.get(f"/jobs/{created_job.id}/logs")
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    assert json.loads(logs_content)["logs"] == json.loads(f'"{log}"')


def test_missing_api_key_in_job_creation(
    job_service, test_client, dependency_overrides_fakes, job_service_dependency_override
):
    key_name = "MISTRAL_KEY"
    infer_model = JobInferenceCreate(
        name="test_run_hugging_face",
        description="Test run for Huggingface model",
        dataset=UUID("00000000000000000000000000000000"),
        max_samples=2,
        api_keys=key_name,
        job_config=JobInferenceConfig(
            model="ministral-8b-latest",
            provider="mistral",
        ),
    )
    infer_payload = infer_model.model_dump(mode="json")

    with patch("backend.api.deps.JobSubmissionClient"):
        with patch.object(job_service, "create_job", side_effect=SecretNotFoundError("test error msg")):
            response = test_client.post("/jobs/inference/", headers=POST_HEADER, json=infer_payload)
            assert response is not None
            assert response.status_code == status.HTTP_400_BAD_REQUEST
