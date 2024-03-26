from fastapi.testclient import TestClient

from src.settings import settings


def test_health_check(test_client: TestClient):
    response = test_client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == "OK"
