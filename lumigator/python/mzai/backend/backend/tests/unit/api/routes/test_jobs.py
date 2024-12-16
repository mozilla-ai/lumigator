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
):
    created_job = job_repository.create(name="test", description="")

    # The Ray client will call the Ray API to get the version before gettting the job status
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


def test_get_job_results(
    app_client: TestClient,
    job_repository,
    request_mock,
    json_ray_version,
    json_data_health_job_metadata_ray,
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

    
def test_annotate_job(
    app_client: TestClient,
):
    payload = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "dataset": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "max_samples": 2,
        "task": "summarization",
    }

    post_response = app_client.post(
        "/jobs/annotate/",
        json=payload,
    )

    assert post_response.status_code == 201

    job_id = post_response.json()["id"]
    response = app_client.get(f"/jobs/{job_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"].lower() == "pending"
