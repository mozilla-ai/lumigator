from fastapi import status
from fastapi.testclient import TestClient

from src.schemas.extras import HealthResponse


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    health = HealthResponse.model_validate(response.json())
    assert health.status == "OK"
