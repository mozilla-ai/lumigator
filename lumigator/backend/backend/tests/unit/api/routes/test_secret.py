import json
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient
from lumigator_schemas.secrets import Secret

from backend.repositories.secrets import SecretRepository
from backend.services.secrets import SecretService


def test_put_secret(
    app_client: TestClient, secret_service: SecretService, secret_repository: SecretRepository, dependency_overrides_fakes
):
    new_secret = Secret(secret_value="123456", description="test secret")
    new_secret_name = "TEST_AI_CLIENT_KEY"
    assert secret_repository.list() == []
    response = app_client.put(f"/secrets/{new_secret_name}", json=new_secret.model_dump())
    assert response.status_code == status.HTTP_200_OK
    assert secret_repository.list() != []
    db_secret = secret_repository.list()[0]
    assert db_secret.secret_name == new_secret_name
    assert db_secret.secret_value == new_secret.secret_value
    assert db_secret.description == new_secret.description
