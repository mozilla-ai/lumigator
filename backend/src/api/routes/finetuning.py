from uuid import UUID

from fastapi import APIRouter

from src.api.deps import FinetuningServiceDep
from src.schemas.extras import ListingResponse
from src.schemas.finetuning import (
    FinetuningJobCreate,
    FinetuningJobResponse,
    FinetuningLogsResponse,
)

router = APIRouter()


@router.post("/jobs", response_model=FinetuningJobResponse)
def create_finetuning_job(service: FinetuningServiceDep, request: FinetuningJobCreate):
    return service.create_job(request)


@router.get("/jobs/{job_id}", response_model=FinetuningJobResponse)
def get_finetuning_job(service: FinetuningServiceDep, job_id: UUID):
    return service.get_job(job_id)


@router.get("/jobs/{job_id}/logs", response_model=FinetuningLogsResponse)
def get_finetuning_job_logs(service: FinetuningServiceDep, job_id: UUID):
    return service.get_job_logs(job_id)


@router.get("/jobs", response_model=ListingResponse[FinetuningJobResponse])
def list_finetuning_jobs(service: FinetuningServiceDep, skip: int = 0, limit: int = 100):
    return service.list_jobs(skip, limit)
