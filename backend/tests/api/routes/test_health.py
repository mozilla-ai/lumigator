from fastapi.testclient import TestClient

from src.settings import settings


def test_health_check(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == "OK"
