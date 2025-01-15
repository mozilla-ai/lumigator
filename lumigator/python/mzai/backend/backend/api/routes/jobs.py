import json
from http import HTTPStatus
from urllib.parse import urljoin
from uuid import UUID

import loguru
import requests
from fastapi import APIRouter, HTTPException, status
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    Job,
    JobAnnotateCreate,
    JobEvalCreate,
    JobEvalLiteCreate,
    JobInferenceCreate,
    JobLogsResponse,
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
    """This uses a hardcoded model, that is, Lumigator's opinion on what
    reference model should be used to generate annotations.
    See more: https://blog.mozilla.ai/lets-build-an-app-for-evaluating-llms/
    """
    inference_job_create_request = JobInferenceCreate(
        **job_create_request.dict(),
        model="hf://facebook/bart-large-cnn",
        output_field="ground_truth",
    )
    job_response = service.create_job(inference_job_create_request)

    url = request.url_for(get_job.__name__, job_id=job_response.id)
    response.headers[HttpHeaders.LOCATION] = f"{url}"

    return job_response


@router.post("/evaluate/", status_code=status.HTTP_201_CREATED)
def create_evaluation_job(
    service: JobServiceDep,
    job_create_request: JobEvalCreate,
    request: Request,
    response: Response,
) -> JobResponse:
    job_response = service.create_job(job_create_request)

    url = request.url_for(get_job.__name__, job_id=job_response.id)
    response.headers[HttpHeaders.LOCATION] = f"{url}"

    return job_response


# TODO: remove the code above and refactor the method below to answer
#       to "/evaluate/" when we deprecate evaluator
@router.post("/eval_lite/", status_code=status.HTTP_201_CREATED)
def create_evaluation_lite_job(
    service: JobServiceDep,
    job_create_request: JobEvalLiteCreate,
    request: Request,
    response: Response,
) -> JobResponse:
    job_response = service.create_job(job_create_request)

    url = request.url_for(get_job.__name__, job_id=job_response.id)
    response.headers[HttpHeaders.LOCATION] = f"{url}"

    return job_response


@router.get("/")
def list_jobs(
    service: JobServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[Job]:
    """Attempts to retrieve job data from the Lumigator repository where Ray
    metadata is also available.

    Results are a merged representation which form an augmented view of a 'job'.

    NOTE: Lumigator repository data takes precedence over Ray metadata.
    """
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


@router.get("/{job_id}")
def get_job(service: JobServiceDep, job_id: UUID) -> Job:
    """Attempts to retrieve merged job data from the Lumigator repository and Ray.

    NOTE: Lumigator repository data takes precedence over Ray metadata.
    """
    job = service.get_job(job_id)
    ray_job = _get_ray_job(job_id)

    # Combine both types of response.
    x = ray_job.model_dump()  # JobSubmissionResponse
    y = job.model_dump()  # JobResponse
    merged = {**x, **y}
    return Job(**merged)


@router.get("/{job_id}/logs")
def get_job_logs(job_id: UUID) -> JobLogsResponse:
    resp = requests.get(urljoin(settings.RAY_JOBS_URL, f"{job_id}/logs"))

    if resp.status_code == HTTPStatus.NOT_FOUND:
        loguru.logger.error(
            f"Upstream job logs not found: {resp.status_code}, error: {resp.text or ''}"
        )
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Job logs for ID: {job_id} not found",
        )
    elif resp.status_code != HTTPStatus.OK:
        loguru.logger.error(
            f"Unexpected status code getting job logs: {resp.status_code}, error: {resp.text or ''}"
        )
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error getting job logs for ID: {job_id}",
        )

    try:
        metadata = json.loads(resp.text)
        return JobLogsResponse(**metadata)
    except json.JSONDecodeError as e:
        loguru.logger.error(f"JSON decode error: {e}")
        loguru.logger.error(f"Response text: {resp.text}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Invalid JSON response"
        ) from e


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
    """Returns metadata that exists in the Ray cluster for all jobs."""
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


def _get_ray_job(job_id: UUID) -> JobSubmissionResponse:
    """Returns metadata on the specified job if it exists in the Ray cluster."""
    resp = requests.get(urljoin(settings.RAY_JOBS_URL, f"{job_id}"))

    if resp.status_code == HTTPStatus.NOT_FOUND:
        loguru.logger.error(
            f"Upstream job metadata not found ({resp.status_code}), error:  {resp.text or ''}"
        )
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Job metadata for ID: {job_id} not found",
        )
    elif resp.status_code != HTTPStatus.OK:
        loguru.logger.error(
            "Unexpected status code getting job metadata text: "
            f"{resp.status_code}, error: {resp.text or ''}"
        )
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error getting job metadata for ID: {job_id}",
        )

    try:
        metadata = json.loads(resp.text)
        return JobSubmissionResponse(**metadata)
    except json.JSONDecodeError as e:
        loguru.logger.error(f"JSON decode error: {e}")
        loguru.logger.error(f"Response text: {resp.text or ''}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Invalid JSON response"
        ) from e
