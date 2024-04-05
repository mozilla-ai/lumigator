from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, status

from mzai.backend.api.deps import FinetuningServiceDep
from mzai.backend.schemas.extras import ListingResponse
from mzai.backend.schemas.finetuning import (
    FinetuningJobCreate,
    FinetuningJobResponse,
    FinetuningJobUpdate,
    FinetuningLogsResponse,
)

router = APIRouter()


@router.post("/jobs", status_code=status.HTTP_201_CREATED)
def create_finetuning_job(
    service: FinetuningServiceDep,
    background_tasks: BackgroundTasks,
    request: FinetuningJobCreate,
) -> FinetuningJobResponse:
    return service.create_job(request, background_tasks)


@router.get("/jobs/{job_id}")
def get_finetuning_job(service: FinetuningServiceDep, job_id: UUID) -> FinetuningJobResponse:
    return service.get_job(job_id)


@router.get("/jobs/{job_id}/logs")
def get_finetuning_job_logs(service: FinetuningServiceDep, job_id: UUID) -> FinetuningLogsResponse:
    return service.get_job_logs(job_id)


@router.get("/jobs")
def list_finetuning_jobs(
    service: FinetuningServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[FinetuningJobResponse]:
    return service.list_jobs(skip, limit)


@router.put("/jobs/{job_id}")
def update_finetuning_job(
    service: FinetuningServiceDep,
    job_id: UUID,
    request: FinetuningJobUpdate,
) -> FinetuningJobResponse:
    return service.update_job(job_id, request)
