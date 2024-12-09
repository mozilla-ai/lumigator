import json
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
