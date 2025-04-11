from fastapi.testclient import TestClient
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.models import ModelsResponse

from backend.api.routes.models import _filter_models_by_tasks, _get_supported_tasks


def test_get_suggested_models_single_task_ok(test_client: TestClient, model_specs_data):
    response = test_client.get("/models/?tasks=summarization")
    assert response.status_code == 200
    models = ListingResponse[ModelsResponse].model_validate(response.json())

    # Filter models that only support summarization
    filtered_data = _filter_models_by_tasks(model_specs_data, {"summarization"})

    assert models.total == len(filtered_data)
    assert len(models.items) == len(filtered_data)


def test_get_suggested_models_multiple_tasks_ok(test_client: TestClient, model_specs_data):
    response = test_client.get("/models/?tasks=summarization&tasks=translation")
    assert response.status_code == 200
    models = ListingResponse[ModelsResponse].model_validate(response.json())

    # Filter models that support either summarization or translation
    filtered_data = _filter_models_by_tasks(model_specs_data, {"summarization", "translation"})

    assert models.total == len(filtered_data)
    assert len(models.items) == len(filtered_data)


def test_get_suggested_models_no_task_specified(test_client: TestClient, model_specs_data):
    # Should return all models based on your implementation
    response = test_client.get("/models/")
    assert response.status_code == 200
    models = ListingResponse[ModelsResponse].model_validate(response.json())

    assert models.total == len(model_specs_data)
    assert len(models.items) == len(model_specs_data)


def test_get_suggested_models_invalid_task(test_client: TestClient, model_specs_data):
    response = test_client.get("/models/?tasks=invalid_task")
    assert response.status_code == 400

    supported_tasks = _get_supported_tasks(model_specs_data)

    # Check that the error message contains the supported tasks
    error_detail = response.json()["detail"]
    assert "Unsupported task(s)" in error_detail
    assert "invalid_task" in error_detail
    assert str(supported_tasks) in error_detail or ", ".join(supported_tasks) in error_detail
