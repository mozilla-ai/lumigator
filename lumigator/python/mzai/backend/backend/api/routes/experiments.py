from uuid import UUID

from fastapi import APIRouter, status

from backend.api.deps import ExperimentServiceDep
from schemas.experiments import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
    ExperimentResultResponse,
)
from schemas.extras import ListingResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_experiment(
    service: ExperimentServiceDep,
    request: ExperimentCreate,
) -> ExperimentResponse:
    return service.create_experiment(request)


@router.get("/{experiment_id}")
def get_experiment(service: ExperimentServiceDep, experiment_id: UUID) -> ExperimentResponse:
    return service.get_experiment(experiment_id)


@router.get("/")
def list_experiments(
    service: ExperimentServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[ExperimentResponse]:
    return service.list_experiments(skip, limit)


@router.get("/{experiment_id}/result")
def get_experiment_result(
    service: ExperimentServiceDep,
    experiment_id: UUID,
) -> ExperimentResultResponse:
    """Return experiment results metadata if available in the DB."""
    return service.get_experiment_result(experiment_id)


@router.get("/{experiment_id}/result/download")
def get_experiment_result_download(
    service: ExperimentServiceDep,
    experiment_id: UUID,
) -> ExperimentResultDownloadResponse:
    """Return experiment results file URL for downloading."""
    return service.get_experiment_result_download(experiment_id)
