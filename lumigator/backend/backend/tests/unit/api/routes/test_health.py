import json
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient
from lumigator_schemas.extras import HealthResponse


def load_json(path: Path) -> str:
    with Path.open(path) as file:
        return json.load(file)


def test_health_check(test_client: TestClient):
    response = test_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    health = HealthResponse.model_validate(response.json())
    assert health.status == "OK"
