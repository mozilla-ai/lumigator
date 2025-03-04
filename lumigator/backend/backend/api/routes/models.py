from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException, Query
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.models import ModelsResponse

MODELS_PATH = Path(__file__).resolve().parents[2] / "models.yaml"

router = APIRouter()


def _get_supported_tasks(data: dict) -> list[str]:
    tasks = set()
    for model in data:
        for task in model.get("tasks", []):
            tasks.update(task.keys())

    return list(tasks)


def _filter_models_by_tasks(models: list, requested_tasks: list[str]) -> list:
    """Filter models that support any of the requested tasks."""
    filtered_models = []

    for model in models:
        model_tasks = set()
        for task_dict in model.get("tasks", []):
            model_tasks.update(task_dict.keys())

        # If any of the requested tasks is supported by this model
        if any(task in model_tasks for task in requested_tasks):
            filtered_models.append(model)

    return filtered_models


@router.get("/")
def get_suggested_models(
    task: list[str] | None = Query(default=None, description="Filter models by task types"),
) -> ListingResponse[ModelsResponse]:
    """Get a list of suggested models for the given tasks.

    Args:
        task (List[str], optional): The task names to filter by.

    Returns:
        ListingResponse[ModelsResponse]: A list of suggested models.
    """
    with Path(MODELS_PATH).open() as file:
        data = yaml.safe_load(file)

    supported_tasks = _get_supported_tasks(data)

    # Return all models if no tasks specified
    filtered_data = data

    # If tasks are specified, validate and filter
    if task:
        # Check if all requested tasks are supported
        unsupported_tasks = [t for t in task if t not in supported_tasks]
        if unsupported_tasks:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported task(s): {unsupported_tasks}. Choose from: {supported_tasks}",
            )

        # Filter models by the requested tasks
        filtered_data = _filter_models_by_tasks(data, task)

    return_data = {
        "total": len(filtered_data),
        "items": filtered_data,
    }
    return ListingResponse[ModelsResponse].model_validate(return_data)
