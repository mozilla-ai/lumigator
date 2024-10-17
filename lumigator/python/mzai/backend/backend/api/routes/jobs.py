from uuid import UUID

from fastapi import APIRouter, status

from backend.api.deps import JobServiceDep
from schemas.jobs import (
    JobCreate,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
)
from schemas.extras import ListingResponse

router = APIRouter()


@router.post("/inference", status_code=status.HTTP_201_CREATED)
def create_job(
    service: JobServiceDep,
    request: JobCreate,
) -> JobResponse:
    return service.create_inference_job(request, type)

@router.post("/evaluate", status_code=status.HTTP_201_CREATED)
def create_job(
    service: JobServiceDep,
    request: JobCreate,
) -> JobResponse:
    return service.create_evaluation_job(request, type)


@router.get("/{job_id}")
def get_job(service: JobServiceDep, job_id: UUID) -> JobResponse:
    return service.get_job(job_id)


@router.get("/")
def list_jobs(
    service: JobServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[JobResponse]:
    return service.list_jobs(skip, limit)


@router.get("/{job_id}/result")
def get_job_result(
    service: JobServiceDep,
    job_id: UUID,
) -> JobResultResponse:
    """Return job results metadata if available in the DB."""
    return service.get_job_result(job_id)


@router.get("/{job_id}/result/download")
def get_job_result_download(
    service: JobServiceDep,
    job_id: UUID,
) -> JobResultDownloadResponse:
    """Return job results file URL for downloading."""
    return service.get_job_result_download(job_id)
