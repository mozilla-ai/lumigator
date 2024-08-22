from fastapi.testclient import TestClient
from fastapi import status
from mzai.backend.main import app


# We invoke the app directly since the main route is outside the router
client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Hello": "Lumigator!🐊"}
