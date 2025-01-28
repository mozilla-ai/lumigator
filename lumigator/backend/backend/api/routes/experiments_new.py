from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, status
from lumigator_schemas.experiments import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
    ExperimentResultResponse,
)
from lumigator_schemas.extras import ListingResponse

from backend.api.deps import ExperimentServiceDep, JobServiceDep

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_experiment(
    service: ExperimentServiceDep, request: ExperimentCreate, background_tasks: BackgroundTasks
) -> ExperimentResponse:
    return ExperimentResponse.model_validate(service.create_experiment(request, background_tasks))


@router.get("/{experiment_id}")
def get_experiment(service: ExperimentServiceDep, experiment_id: UUID) -> ExperimentResponse:
    return ExperimentResponse.model_validate(service.get_experiment(experiment_id).model_dump())


@router.get("/{experiment_id}/jobs")
def get_experiment_jobs(
    service: ExperimentServiceDep, experiment_id: UUID
) -> ListingResponse[UUID]:
    return service.get_all_owned_jobs(experiment_id)


@router.get("/")
def list_experiments(
    service: ExperimentServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[ExperimentResponse]:
    return ListingResponse[ExperimentResponse].model_validate(
        service.list_experiments(skip, limit).model_dump()
    )


@router.get("/{experiment_id}/result")
def get_experiment_result(
    service: JobServiceDep,
    experiment_id: UUID,
) -> ExperimentResultResponse:
    """Return experiment results metadata if available in the DB."""
    return ExperimentResultResponse.model_validate(
        service.get_job_result(experiment_id).model_dump()
    )


@router.get("/{experiment_id}/result/download")
def get_experiment_result_download(
    service: JobServiceDep,
    experiment_id: UUID,
) -> ExperimentResultDownloadResponse:
    """Return experiment results file URL for downloading."""
    return ExperimentResultDownloadResponse.model_validate(
        service.get_job_result_download(experiment_id).model_dump()
    )
