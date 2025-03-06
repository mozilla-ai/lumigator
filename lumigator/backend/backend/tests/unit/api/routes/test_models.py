import json
from pathlib import Path

import yaml
from fastapi.testclient import TestClient
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.models import ModelsResponse

from backend.api.routes.models import _get_supported_tasks

MODELS_PATH = Path(__file__).resolve().parents[4] / "models.yaml"


def test_get_suggested_models_summarization_ok(app_client: TestClient):
    response = app_client.get("/models/summarization")
    assert response.status_code == 200
    models = ListingResponse[ModelsResponse].model_validate(response.json())

    with Path(MODELS_PATH).open() as file:
        data = yaml.safe_load(file)

    assert models.total == len(data)


def test_get_suggested_models_invalid_task(app_client: TestClient):
    response = app_client.get("/models/invalid_task")
    assert response.status_code == 400

    with Path(MODELS_PATH).open() as file:
        data = yaml.safe_load(file)

    supported_tasks = _get_supported_tasks(data)

    assert response.json() == {"detail": f"Unsupported task. Choose from: {supported_tasks}"}
