import json
from http import HTTPStatus
from typing import Annotated
from urllib.parse import urljoin
from uuid import UUID

import loguru
import requests
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from lumigator_schemas.datasets import DatasetResponse
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
)
from ray.job_submission import JobDetails as RayJobDetails
from starlette.requests import Request
from starlette.responses import Response

from backend.api.deps import DatasetServiceDep, JobServiceDep
from backend.api.http_headers import HttpHeaders
from backend.services.exceptions.base_exceptions import ServiceError
from backend.services.exceptions.job_exceptions import (
    JobNotFoundError,
    JobTypeUnsupportedError,
    JobUpstreamError,
)
from backend.settings import settings

router = APIRouter()


def job_exception_mappings() -> dict[type[ServiceError], HTTPStatus]:
    return {
        JobNotFoundError: status.HTTP_404_NOT_FOUND,
        JobTypeUnsupportedError: status.HTTP_501_NOT_IMPLEMENTED,
        JobUpstreamError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }


@router.post("/inference/", status_code=status.HTTP_201_CREATED)
def create_inference_job(
    service: JobServiceDep,
    job_create_request: JobInferenceCreate,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
) -> JobResponse:
    job_response = service.create_job(job_create_request)

    service.add_background_task(
        background_tasks, service.handle_inference_job, job_response.id, job_create_request
    )

    url = request.url_for(get_job.__name__, job_id=job_response.id)
    response.headers[HttpHeaders.LOCATION] = f"{url}"

    return job_response


@router.post("/annotate/", status_code=status.HTTP_201_CREATED)
def create_annotation_job(
    service: JobServiceDep,
    job_create_request: JobAnnotateCreate,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
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
    inference_job_create_request.store_to_dataset = True
    job_response = service.create_job(inference_job_create_request)

    service.add_background_task(
        background_tasks,
        service.handle_inference_job,
        job_response.id,
        inference_job_create_request,
    )

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
    job_types: Annotated[list[str], Query()] = (),
) -> ListingResponse[Job]:
    """Retrieves job data from the Lumigator repository where Ray
    metadata is also available.

    Results are a merged representation which form an augmented view of a 'job'.

    NOTE: Lumigator repository data takes precedence over Ray metadata.
    """
    # if job_type not in ["inference", "annotate", "evaluate"]:
    #     raise ValueError(f"Unknown job type {job_type}") from None
    # jobs = service.list_jobs_per_type(job_type, skip, limit)

    loguru.logger.info(f"Listing jobs, job_types={job_types}")

    jobs = service.list_jobs(skip, limit, job_types)
    if not jobs or jobs.total == 0 or len(jobs.items) == 0:
        return jobs

    # Force a DB update of the job status by querying each one, not ideal for will do for now.
    for job in jobs.items:
        job = service.get_job(job.id)

    # Get all jobs Ray knows about on a dict
    ray_jobs = {ray_job.submission_id: ray_job for ray_job in _get_all_ray_jobs()}

    results = list[Job]()

    # Merge Ray jobs into the repositories jobs
    job: JobResponse
    for job in jobs.items:
        job_id = str(job.id)
        if job_id in ray_jobs:
            # Combine both types of response.
            found_job: RayJobDetails
            found_job = ray_jobs[job_id]
            ray_job_info = found_job.dict()
            lm_info = job.model_dump()
            merged = {**ray_job_info, **lm_info}
            results.append(Job(**merged))

    return ListingResponse[Job](
        total=jobs.total,
        items=results,
    )


@router.get("/{job_id}")
def get_job(
    service: JobServiceDep,
    job_id: UUID,
) -> Job:
    """Retrieves merged job data from the Lumigator repository and Ray
    for a valid UUID.

    The result is a merged representation which forms an augmented view of a 'job'.

    NOTE: Lumigator repository data takes precedence over Ray metadata.
    """
    job: JobResponse
    job = service.get_job(job_id)
    ray_job: RayJobDetails
    ray_job = _get_ray_job(job_id)

    # Combine both types of response.
    ray_info = ray_job.dict()
    lm_info = job.model_dump()
    merged = {**ray_info, **lm_info}
    return Job(**merged)


@router.get("/{job_id}/logs")
def get_job_logs(job_id: UUID) -> JobLogsResponse:
    resp = requests.get(urljoin(settings.RAY_JOBS_URL, f"{job_id}/logs"), timeout=5)  # 5 seconds

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


# TODO refactor all job results handling
@router.get("/{job_id}/dataset")
def get_job_dataset(
    service: DatasetServiceDep,
    job_id: UUID,
) -> DatasetResponse | None:
    """Return the job-associated dataset if available in the DB."""
    return service.get_dataset_by_job_id(job_id)


@router.get("/{job_id}/result/download")
def get_job_result_download(
    service: JobServiceDep,
    job_id: UUID,
) -> JobResultDownloadResponse:
    """Return job results file URL for downloading."""
    return service.get_job_result_download(job_id)


def _get_all_ray_jobs() -> list[RayJobDetails]:
    """Returns metadata that exists in the Ray cluster for all jobs."""
    resp = requests.get(settings.RAY_JOBS_URL, timeout=5)  # 5 seconds
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
        return [RayJobDetails(**item) for item in metadata]
    except json.JSONDecodeError as e:
        loguru.logger.error(f"JSON decode error: {e}")
        loguru.logger.error(f"Response text: {resp.text}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Invalid JSON response"
        ) from e


def _get_ray_job(job_id: UUID) -> RayJobDetails:
    """Returns metadata on the specified job if it exists in the Ray cluster."""
    resp = requests.get(urljoin(settings.RAY_JOBS_URL, f"{job_id}"), timeout=5)  # 5 seconds

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
        return RayJobDetails(**metadata)
    except json.JSONDecodeError as e:
        loguru.logger.error(f"JSON decode error: {e}")
        loguru.logger.error(f"Response text: {resp.text or ''}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Invalid JSON response"
        ) from e
