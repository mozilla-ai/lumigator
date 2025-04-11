from unittest.mock import patch

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from lumigator_schemas.secrets import SecretGetRequest, SecretUploadRequest

from backend.repositories.secrets import SecretRepository
from backend.services.secrets import SecretService


def test_put_secret(
    test_client: TestClient,
    secret_service: SecretService,
    secret_repository: SecretRepository,
    dependency_overrides_fakes,
):
    new_secret = SecretUploadRequest(value="123456", description="test secret")
    new_secret_name = "TEST_AI_CLIENT_KEY"  # pragma: allowlist secret
    assert secret_repository.list() == []
    response = test_client.put(f"/settings/secrets/{new_secret_name}", json=new_secret.model_dump())
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
    response = test_client.put(f"/settings/secrets/{new_secret_name}", json=new_secret.model_dump())
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert secret_repository.list() != []
    assert len(secret_repository.list()) == 1
    db_secret = secret_repository.list()[0]
    assert db_secret.name == new_secret_name.lower()
    assert db_secret.value != new_secret.value
    assert secret_service._decrypt(db_secret.value) == new_secret.value
    assert db_secret.description == new_secret.description


@pytest.mark.parametrize(
    "mock_return_value",
    [
        [],
        [SecretGetRequest(name="secret_api_key", description="test desc")],
        [
            SecretGetRequest(name="secret_1_api_key", description="test desc 1"),
            SecretGetRequest(name="secret_2_api_key", description="test desc 2"),
        ],
    ],
)
def test_api_list_secrets(
    app: FastAPI,
    test_client: TestClient,
    mock_return_value,
):
    expected_pairs = {(secret.name.lower(), secret.description) for secret in mock_return_value}

    with patch.object(SecretService, "list_secrets", return_value=mock_return_value):
        response = test_client.get("/settings/secrets")
        assert response.status_code == status.HTTP_200_OK

        json_response = response.json()
        assert isinstance(json_response, list)
        assert len(json_response) == len(expected_pairs)

        actual_pairs = {(secret.get("name", "").lower(), secret.get("description", "")) for secret in json_response}

        assert actual_pairs == expected_pairs
