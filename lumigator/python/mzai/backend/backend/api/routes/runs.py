"""These are the runs routes.
A run is a single execution of an experiment, which can be a single job or a batch of jobs.
"""

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
async def create_run(
    service: ExperimentServiceDep, request: ExperimentCreate, background_tasks: BackgroundTasks
) -> ExperimentResponse:
    return ExperimentResponse.model_validate(service.create_experiment(request, background_tasks))


@router.get("/{run_id}/jobs")
def get_run_jobs(service: ExperimentServiceDep, run_id: UUID) -> ListingResponse[UUID]:
    return service.get_all_owned_jobs(run_id)


@router.get("/")
def list_runs(
    service: ExperimentServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[ExperimentResponse]:
    return ListingResponse[ExperimentResponse].model_validate(
        service.list_runs(skip, limit).model_dump()
    )


@router.get("/{run_id}/result")
def get_run_result(
    service: JobServiceDep,
    run_id: UUID,
) -> ExperimentResultResponse:
    """Return the results metadata for a run if available in the DB."""
    # not yet implemented
    pass


@router.get("/{run_id}/result/download")
def get_run_result_download(
    service: JobServiceDep,
    run_id: UUID,
) -> ExperimentResultDownloadResponse:
    """Return run results file URL for downloading."""
    # not yet implemented
    pass
