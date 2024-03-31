from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, status

from src.api.deps import FinetuningServiceDep
from src.handlers import FinetuningJobHandler
from src.schemas.extras import ListingResponse
from src.schemas.finetuning import (
    FinetuningJobCreate,
    FinetuningJobResponse,
    FinetuningJobUpdate,
    FinetuningLogsResponse,
)

router = APIRouter()


@router.post("/jobs", response_model=FinetuningJobResponse, status_code=status.HTTP_201_CREATED)
def create_finetuning_job(
    service: FinetuningServiceDep,
    background: BackgroundTasks,
    request: FinetuningJobCreate,
):
    response = service.create_job(request)
    submission_id = service.get_job_submission_id(response.id)
    handler = FinetuningJobHandler(response.id)
    background.add_task(handler.poll, submission_id)
    return response


@router.get("/jobs/{job_id}", response_model=FinetuningJobResponse)
def get_finetuning_job(service: FinetuningServiceDep, job_id: UUID):
    return service.get_job(job_id)


@router.get("/jobs/{job_id}/logs", response_model=FinetuningLogsResponse)
def get_finetuning_job_logs(service: FinetuningServiceDep, job_id: UUID):
    return service.get_job_logs(job_id)


@router.get("/jobs", response_model=ListingResponse[FinetuningJobResponse])
def list_finetuning_jobs(service: FinetuningServiceDep, skip: int = 0, limit: int = 100):
    return service.list_jobs(skip, limit)


@router.put("/jobs/{job_id}", response_model=FinetuningJobResponse)
def update_finetuning_job(
    service: FinetuningServiceDep,
    job_id: UUID,
    request: FinetuningJobUpdate,
):
    return service.update_job(job_id, request)
