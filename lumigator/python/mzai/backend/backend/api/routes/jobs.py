import json
from http import HTTPStatus
from uuid import UUID

import loguru
import requests
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    Job,
    JobEvalCreate,
    JobInferenceCreate,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
    JobSubmissionResponse,
)
from starlette.requests import Request
from starlette.responses import Response

from backend.api.deps import JobServiceDep
from backend.api.http_headers import HttpHeaders
from backend.settings import settings

router = APIRouter()


@router.post("/inference/", status_code=status.HTTP_201_CREATED)
def create_inference_job(
    service: JobServiceDep,
    job_create_request: JobInferenceCreate,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
) -> JobResponse:
    # The FastAPI BackgroundTasks object is used to run a function in the background.
    # It is a wrapper arount Starlette's BackgroundTasks object.
    # A background task should be attached to a response,
    # and will run only once the response has been sent.
    # See here: https://www.starlette.io/background/
    job_response = service.create_job(job_create_request, background_tasks)

    url = request.url_for(get_job.__name__, job_id=job_response.id)
    response.headers[HttpHeaders.LOCATION] = f"{url}"

    return job_response


@router.post("/evaluate/", status_code=status.HTTP_201_CREATED)
def create_evaluation_job(
    service: JobServiceDep,
    job_create_request: JobEvalCreate,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
) -> JobResponse:
    job_response = service.create_job(job_create_request, background_tasks)

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
) -> ListingResponse[Job]:
    jobs = service.list_jobs(skip, limit)
    if not jobs or jobs.total == 0 or len(jobs.items) == 0:
        return jobs

    # Force a DB update of the job status by querying each one, not ideal for will do for now.
    for job in jobs.items:
        job = service.get_job(job.id)

    # Get all jobs Ray knows about.
    ray_jobs = _get_all_ray_jobs()

    results = list[Job]()

    # Merge Ray jobs into the repositories jobs
    for job in jobs.items:
        found_job = next(
            (x for x in filter(lambda x: x.submission_id == str(job.id), ray_jobs)), None
        )
        if found_job is None:
            continue

        # Combine both types of response.
        x = found_job.model_dump()  # JobSubmissionResponse
        y = job.model_dump()  # JobResponse
        merged = {**x, **y}
        results.append(Job(**merged))

    return ListingResponse[Job](
        total=jobs.total,
        items=results,
    )


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


def _get_all_ray_jobs() -> list[JobSubmissionResponse]:
    resp = requests.get(settings.RAY_JOBS_URL)
    if resp.status_code != HTTPStatus.OK:
        loguru.logger.error(
            f"Unexpected status code getting all jobs: {resp.status_code}, error: {resp.text or ''}"
        )
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Unexpected error getting job logs",
        )

    try:
        metadata = json.loads(resp.text)
        return [JobSubmissionResponse(**item) for item in metadata]
    except json.JSONDecodeError as e:
        loguru.logger.error(f"JSON decode error: {e}")
        loguru.logger.error(f"Response text: {resp.text}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Invalid JSON response"
        ) from e
