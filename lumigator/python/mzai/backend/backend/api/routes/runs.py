"""These are the runs routes.
A run is a single execution of an experiment, which can be a single job or a batch of jobs.
"""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, status
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.runs import (
    RunCreate,
    RunResponse,
    RunResultDownloadResponse,
    RunResultResponse,
)

from backend.api.deps import RunServiceDep

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_run(
    service: RunServiceDep, request: RunCreate, background_tasks: BackgroundTasks
) -> RunResponse:
    """A run is a single execution of an experiment, which can be a single job or a batch of jobs.
    It must be associated with an experiment id
    (which means you must already have created an experiment and have that ID in the request).
    """
    return RunResponse.model_validate(service.create_run(request, background_tasks))


@router.get("/{run_id}")
def get_run(service: RunServiceDep, run_id: UUID) -> RunResponse:
    return RunResponse.model_validate(service.get_run(run_id).model_dump())


@router.get("/{run_id}/jobs")
def get_run_jobs(service: RunServiceDep, experiment_id: UUID) -> ListingResponse[UUID]:
    return service.get_jobs(experiment_id)


@router.get("/{run_id}/result")
def get_run_result(
    service: RunServiceDep,
    run_id: UUID,
) -> RunResultResponse:
    """Return the results metadata for a run if available in the DB."""
    # not yet implemented
    pass


@router.get("/{run_id}/result/download")
def get_run_result_download(
    service: RunServiceDep,
    run_id: UUID,
) -> RunResultDownloadResponse:
    """Return run results file URL for downloading."""
    # not yet implemented
    pass
