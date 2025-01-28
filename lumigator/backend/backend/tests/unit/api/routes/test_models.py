import json
from pathlib import Path

from fastapi.testclient import TestClient
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.models import ModelsResponse

from backend.api.routes.models import _get_supported_tasks


def test_get_suggested_models_summarization_ok(app_client: TestClient, json_data_models: Path):
    response = app_client.get("/models/summarization")
    assert response.status_code == 200
    models = ListingResponse[ModelsResponse].model_validate(response.json())

    with Path(json_data_models).open() as file:
        data = json.load(file)

    assert models.total == data["total"]


def test_get_suggested_models_invalid_task(app_client: TestClient, json_data_models: Path):
    response = app_client.get("/models/invalid_task")
    assert response.status_code == 400

    with Path(json_data_models).open() as file:
        data = json.load(file)

    supported_tasks = _get_supported_tasks(data.get("items", []))

    assert response.json() == {"detail": f"Unsupported task. Choose from: {supported_tasks}"}
