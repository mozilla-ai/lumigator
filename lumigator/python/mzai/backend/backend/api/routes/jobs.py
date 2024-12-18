from uuid import UUID

from fastapi import APIRouter, status
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobAnnotateCreate,
    JobEvalCreate,
    JobInferenceCreate,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
)
from starlette.requests import Request
from starlette.responses import Response

from backend.api.deps import JobServiceDep
from backend.api.http_headers import HttpHeaders

router = APIRouter()


@router.post("/inference/", status_code=status.HTTP_201_CREATED)
def create_inference_job(
    service: JobServiceDep,
    job_create_request: JobInferenceCreate,
    request: Request,
    response: Response,
) -> JobResponse:
    job_response = service.create_job(job_create_request)

    url = request.url_for(get_job.__name__, job_id=job_response.id)
    response.headers[HttpHeaders.LOCATION] = f"{url}"

    return job_response


@router.post("/annotate/", status_code=status.HTTP_201_CREATED)
def create_annotation_job(
    service: JobServiceDep,
    job_create_request: JobAnnotateCreate,
    request: Request,
    response: Response,
) -> JobResponse:
    # Lumigator's opinion on the best summarization model
    # and the one that should generate annotations.
    # In the future, we could expose this via a config file
    # so that, for a supported task, there is a default
    # "reference" model. For now, we keep the current functionality:
    # Lumigator decides who annotates.

    inference_job_create_request = JobInferenceCreate(
        **job_create_request.dict(), model="hf://facebook/bart-large-cnn"
    )
    job_response = service.create_job(inference_job_create_request)

    url = request.url_for(get_job.__name__, job_id=job_response.id)
    response.headers[HttpHeaders.LOCATION] = f"{url}"

    return job_response


@router.post("/evaluate/", status_code=status.HTTP_201_CREATED)
def create_evaluation_job(
    service: JobServiceDep, job_create_request: JobEvalCreate, request: Request, response: Response
) -> JobResponse:
    job_response = service.create_job(job_create_request)

    url = request.url_for(get_job.__name__, job_id=job_response.id)
    response.headers[HttpHeaders.LOCATION] = f"{url}"

    return job_response


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
