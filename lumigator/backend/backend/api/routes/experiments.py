from http import HTTPStatus

from fastapi import APIRouter, status
from lumigator_schemas.experiments import (
    ExperimentCreate,
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
async def create_experiment_id(service: ExperimentServiceDep, request: ExperimentCreate) -> GetExperimentResponse:
    """Create an experiment ID."""
    experiment = await service.create_experiment(request)
    return GetExperimentResponse.model_validate(experiment.model_dump())


@router.get("/{experiment_id}")
async def get_experiment(service: ExperimentServiceDep, experiment_id: str) -> GetExperimentResponse:
    """Get an experiment by ID."""
    experiment = await service.get_experiment(experiment_id)
    return GetExperimentResponse.model_validate(experiment.model_dump())


@router.get("/")
async def list_experiments(
    service: ExperimentServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[GetExperimentResponse]:
    """List all experiments."""
    experiments = await service.list_experiments(skip, limit)
    return ListingResponse[GetExperimentResponse].model_validate(experiments.model_dump())


@router.delete("/{experiment_id}")
async def delete_experiment(service: ExperimentServiceDep, experiment_id: str) -> None:
    """Delete an experiment by ID."""
    await service.delete_experiment(experiment_id)
