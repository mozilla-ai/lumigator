from fastapi.testclient import TestClient

from src.schemas.extras import HealthResponse


def test_health_check(client: TestClient):
    response = client.get("health")
    print(response.request)
    assert response.status_code == 200
    health = HealthResponse.model_validate(response.json())
    assert health.status == "OK"
