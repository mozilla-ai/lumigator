from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException
from lumigator_schemas.extras import ListingResponse

SUPPORTED_TASKS = ["summarization"]
MODELS_PATH = Path(__file__).resolve().parents[2] / "models.yaml"

router = APIRouter()


@router.get("/{task_name}")
def get_suggested_models(task_name: str) -> ListingResponse[dict]:
    """Get a list of suggested models for the given task.

    Args:
        task_name (str): The task name.

    Returns:
        ListingResponse[str]: A list of suggested models.
    """
    # Currently, only summarization task is supported.
    if task_name != "summarization":
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported task. Choose from: {SUPPORTED_TASKS}",
        )

    with Path(MODELS_PATH).open() as file:
        data = yaml.safe_load(file)

    return_data = {
        "total": len(data),
        "items": data,
    }
    return ListingResponse[dict].model_validate(return_data)
