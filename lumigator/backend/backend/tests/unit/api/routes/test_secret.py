import json
from pathlib import Path

import loguru
from fastapi import status
from fastapi.testclient import TestClient
from lumigator_schemas.secrets import SecretUploadRequest

from backend.repositories.secrets import SecretRepository
from backend.services.secrets import SecretService


def test_put_secret(
    app_client: TestClient,
    secret_service: SecretService,
    secret_repository: SecretRepository,
    dependency_overrides_fakes,
):
    new_secret = SecretUploadRequest(value="123456", description="test secret")
    new_secret_name = "TEST_AI_CLIENT_KEY"  # pragma: allowlist secret
    assert secret_repository.list() == []
    response = app_client.put(f"/settings/secrets/{new_secret_name}", json=new_secret.model_dump())
    assert response.status_code == status.HTTP_201_CREATED
    assert secret_repository.list() != []
    assert len(secret_repository.list()) == 1
    db_secret = secret_repository.list()[0]
    assert db_secret.name == new_secret_name.lower()
    assert db_secret.value != new_secret.value
    assert secret_service._decrypt(db_secret.value) == new_secret.value
    assert db_secret.description == new_secret.description

    # Repeat now that it already exists to ensure we get the right status code response.
    new_secret.description = "test secret 2"
    new_secret.value = "secret2"
    response = app_client.put(f"/settings/secrets/{new_secret_name}", json=new_secret.model_dump())
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert secret_repository.list() != []
    assert len(secret_repository.list()) == 1
    db_secret = secret_repository.list()[0]
    assert db_secret.name == new_secret_name.lower()
    assert db_secret.value != new_secret.value
    assert secret_service._decrypt(db_secret.value) == new_secret.value
    assert db_secret.description == new_secret.description
