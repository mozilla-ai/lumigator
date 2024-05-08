from uuid import UUID

from fastapi import APIRouter, status

from mzai.backend.api.deps import ExperimentServiceDep
from mzai.schemas.experiments import ExperimentCreate, ExperimentResponse, ExperimentResultResponse
from mzai.schemas.extras import ListingResponse

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
    return service.get_experiment_result(experiment_id)
