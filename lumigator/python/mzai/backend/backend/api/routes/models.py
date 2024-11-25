from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException
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


@router.get("/{task_name}")
def get_suggested_models(task_name: str) -> ListingResponse[ModelsResponse]:
    """Get a list of suggested models for the given task.

    Args:
        task_name (str): The task name.

    Returns:
        ListingResponse[str]: A list of suggested models.
    """
    with Path(MODELS_PATH).open() as file:
        data = yaml.safe_load(file)

    supported_tasks = _get_supported_tasks(data)

    # Currently, only summarization task is supported.
    if task_name != "summarization":
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported task. Choose from: {supported_tasks}",
        )

    return_data = {
        "total": len(data),
        "items": data,
    }
    return ListingResponse[ModelsResponse].model_validate(return_data)
