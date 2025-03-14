import itertools
from http import HTTPStatus
from pathlib import Path

import loguru
import yaml
from fastapi import APIRouter, HTTPException, Query, status
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.models import ModelsResponse
from pydantic_core._pydantic_core import ValidationError

DEFAULT_TASKS_QUERY = Query(default=None, description="Filter models by task types")
MODELS_PATH = Path(__file__).resolve().parents[2] / "models.yaml"

router = APIRouter()


def _get_model_tasks(model: ModelsResponse) -> set[str]:
    """Extract all task types (in lowercase) that the model supports."""
    return set([key.lower() for task_dict in model.tasks for key in task_dict.keys()])


def _get_supported_tasks(models: list[ModelsResponse]) -> set[str]:
    """Get the distinct set of supported (lowercase) task types across all models."""
    return set(itertools.chain(*map(_get_model_tasks, models)))


def _filter_models_by_tasks(models: list[ModelsResponse], requested_tasks: set[str]) -> list[ModelsResponse]:
    """Filter models, returning only those that support any of the requested tasks."""
    return [model for model in models if any(task in _get_model_tasks(model) for task in requested_tasks)]


@router.get(
    "/",
    response_model=ListingResponse[ModelsResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Successful Response"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad Request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
def get_suggested_models(
    tasks: list[str] | None = DEFAULT_TASKS_QUERY,
) -> ListingResponse[ModelsResponse]:
    """Get a list of suggested models for the given tasks.

    Usage: GET api/v1/models/?tasks=summarization&tasks=translation

    Args:
        tasks (List[str], optional): The task names to filter by.

    Returns:
        ListingResponse[ModelsResponse]: A list of suggested models.
    """
    with Path(MODELS_PATH).open() as file:
        data = yaml.safe_load(file)

    # Validate that every item in the data is a ModelsResponse before we continue.
    try:
        models = [ModelsResponse.model_validate(item) for item in data]
    except ValidationError as e:
        loguru.logger.exception("Unable to validate loaded models data: {}", e)
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, "Model data not available") from None

    # If no tasks are specified, return all models.
    if not tasks:
        return ListingResponse[ModelsResponse](total=len(models), items=models)

    # Check if all requested tasks are supported
    requested_tasks = set(map(str.lower, tasks))
    supported_tasks = _get_supported_tasks(models)
    unsupported_tasks = requested_tasks.difference(supported_tasks)
    if unsupported_tasks:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Unsupported task(s): {unsupported_tasks}. Choose from: {supported_tasks}",
        ) from None

    # Filter models by the requested tasks
    result_items = _filter_models_by_tasks(models, requested_tasks)

    return ListingResponse[ModelsResponse](total=len(result_items), items=result_items)
