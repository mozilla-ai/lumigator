"""These are the runs routes.
A run is a single execution of an experiment, which can be a single job or a batch of jobs.
"""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, status
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.workflows import (
    WorkflowCreate,
    WorkflowResponse,
    WorkflowResultDownloadResponse,
    WorkflowResultResponse,
)

from backend.api.deps import WorkflowServiceDep

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_run(
    service: WorkflowServiceDep, request: WorkflowCreate, background_tasks: BackgroundTasks
) -> WorkflowResponse:
    """A run is a single execution of an experiment, which can be a single job or a batch of jobs.
    It must be associated with an experiment id
    (which means you must already have created an experiment and have that ID in the request).
    """
    return WorkflowResponse.model_validate(service.create_run(request, background_tasks))


@router.get("/{run_id}")
def get_run(service: WorkflowServiceDep, run_id: UUID) -> WorkflowResponse:
    return WorkflowResponse.model_validate(service.get_run(run_id).model_dump())


@router.get("/{experiment_id}/jobs")
def get_run_jobs(service: WorkflowServiceDep, experiment_id: UUID) -> ListingResponse[UUID]:
    return service.get_jobs(experiment_id)


@router.get("/{run_id}/result")
def get_run_result(
    service: WorkflowServiceDep,
    run_id: UUID,
) -> WorkflowResultResponse:
    """Return the results metadata for a run if available in the DB."""
    # not yet implemented
    pass


@router.get("/{run_id}/result/download")
def get_run_result_download(
    service: WorkflowServiceDep,
    run_id: UUID,
) -> WorkflowResultDownloadResponse:
    """Return run results file URL for downloading."""
    # not yet implemented
    pass
