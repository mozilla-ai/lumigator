import json
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient
from lumigator_schemas.keys import Key

from backend.repositories.keys import KeyRepository
from backend.services.keys import KeyService


def test_put_key(
    app_client: TestClient, key_service: KeyService, key_repository: KeyRepository, dependency_overrides_fakes
):
    new_key = Key(key_value="123456", description="test key")
    new_key_name = "TEST_AI_CLIENT_KEY"
    assert key_repository.list() == []
    response = app_client.put(f"/keys/{new_key_name}", json=new_key.model_dump())
    assert response.status_code == status.HTTP_200_OK
    assert key_repository.list() != []
    db_key = key_repository.list()[0]
    assert db_key.key_name == new_key_name
    assert db_key.key_value == new_key.key_value
    assert db_key.description == new_key.description
