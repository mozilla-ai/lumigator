import json
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient
from lumigator_schemas.extras import HealthResponse

from backend.settings import settings


def load_json(path: Path) -> str:
    with Path.open(path) as file:
        return json.load(file)

def test_health_check(app_client: TestClient):
    response = app_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    health = HealthResponse.model_validate(response.json())
    assert health.status == "OK"

def test_get_job_metadata_not_found(app_client: TestClient, request_mock,):
    job_id = "42e146e3-10eb-4a55-8018-218829c4752d"
    request_mock.get(
        url=f"{settings.RAY_DASHBOARD_URL}/api/jobs/{job_id}",
        status_code=status.HTTP_404_NOT_FOUND,
        text="Not Found",
    )
    response = app_client.get(f"/health/jobs/{job_id}")
    assert response is not None
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == f"Job metadata for ID: {job_id} not found"

def test_get_job_metadata_not_ok(app_client: TestClient, request_mock,):
    job_id = "22e146e3-10eb-4a55-8018-218829c4752a"
    request_mock.get(
        url=f"{settings.RAY_DASHBOARD_URL}/api/jobs/{job_id}",
        status_code=status.HTTP_409_CONFLICT,
    )
    response = app_client.get(f"/health/jobs/{job_id}")
    assert response is not None
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert data["detail"] == f"Unexpected error getting job metadata for ID: {job_id}"

def test_get_job_metadata_ok(app_client: TestClient,
                             request_mock,
                             json_data_health_job_metadata_ray,
                             json_data_health_job_metadata_ok):
    job_id = "e899341d-bada-4f3c-ae32-b87bf730f897"
    request_mock.get(
        url=f"{settings.RAY_DASHBOARD_URL}/api/jobs/{job_id}",
        status_code=status.HTTP_200_OK,
        text = json.dumps(load_json(json_data_health_job_metadata_ray))
    )
    response = app_client.get(f"/health/jobs/{job_id}")
    assert response is not None
    assert response.status_code == status.HTTP_200_OK

    actual = json.loads(response.text)
    expected = load_json(json_data_health_job_metadata_ok)
    assert expected == actual
