import json
import re
import urllib
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient

from backend.settings import settings


def load_json(path: Path) -> str:
    with Path.open(path) as file:
        return json.load(file)


def test_get_job_status(
    app_client: TestClient,
    job_repository,
    request_mock,
    json_ray_version,
    json_data_health_job_metadata_ray,
    dependency_overrides_fakes,
):
    created_job = job_repository.create(name="test", description="test desc")

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

    response = app_client.get(f"/jobs/{created_job.id}")

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
    app_client: TestClient,
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
    response = app_client.get(f"/jobs/{created_job.id}/result/download")
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    download_url = response_json["download_url"]
    match = re.search(r"lumigator-storage/.+?\.json", download_url)
    extracted_url_path = match.group(0) if match else None
    assert extracted_url_path == expected_url_path


def test_job_logs(
    app_client: TestClient,
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
    response = app_client.get(f"/jobs/{created_job.id}/logs")
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    assert json.loads(logs_content)["logs"] == json.loads(f'"{log}"')
