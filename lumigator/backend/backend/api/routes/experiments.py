from http import HTTPStatus

from fastapi import APIRouter, status
from lumigator_schemas.experiments import (
    ExperimentIdCreate,
    GetExperimentResponse,
)
from lumigator_schemas.extras import ListingResponse

from backend.api.deps import ExperimentServiceDep
from backend.services.exceptions.base_exceptions import ServiceError
from backend.services.exceptions.experiment_exceptions import ExperimentNotFoundError

router = APIRouter()


def experiment_exception_mappings() -> dict[type[ServiceError], HTTPStatus]:
    return {
        ExperimentNotFoundError: status.HTTP_404_NOT_FOUND,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_experiment_id(service: ExperimentServiceDep, request: ExperimentIdCreate) -> GetExperimentResponse:
    """Create an experiment ID."""
    return GetExperimentResponse.model_validate(service.create_experiment(request).model_dump())


@router.get("/{experiment_id}")
def get_experiment(service: ExperimentServiceDep, experiment_id: str) -> GetExperimentResponse:
    """Get an experiment by ID."""
    return GetExperimentResponse.model_validate(service.get_experiment(experiment_id).model_dump())


@router.get("/")
def list_experiments(
    service: ExperimentServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[GetExperimentResponse]:
    """List all experiments."""
    return ListingResponse[GetExperimentResponse].model_validate(service.list_experiments(skip, limit).model_dump())


@router.delete("/{experiment_id}")
def delete_experiment(service: ExperimentServiceDep, experiment_id: str) -> None:
    """Delete an experiment by ID."""
    service.delete_experiment(experiment_id)
