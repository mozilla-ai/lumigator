import json
import urllib
from http import HTTPStatus
from uuid import UUID
from typing import Annotated

import loguru

import loguru
import requests
from fastapi import APIRouter, HTTPException
from lumigator_schemas.extras import HealthResponse
from lumigator_schemas.jobs import JobSubmissionResponse

from backend.settings import settings

router = APIRouter()

@router.get("/")
def get_health() -> HealthResponse:
    return HealthResponse(deployment_type=settings.DEPLOYMENT_TYPE, status="OK")


@router.get("/jobs/{job_id}")
def get_job_metadata(job_id: UUID) -> JobSubmissionResponse:
    resp = requests.get(urllib.parse.urljoin(settings.ray_jobs, f"{job_id}"))

    if resp.status_code == HTTPStatus.NOT_FOUND:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Job metadata for ID: {job_id} not found - {resp.text or ''}",
        )
    elif resp.status_code != HTTPStatus.OK:
        loguru.logger.error(f"Unexpected status code getting job metadata text: {resp.status_code}")
        loguru.logger.error(f"Upstream job metadata response: {resp}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error getting job metadata for ID: {job_id} - {resp.text or ''}",
        )

    try:
        metadata = json.loads(resp.text)
        return JobSubmissionResponse(**metadata)
    except json.JSONDecodeError as e:
        loguru.logger.error(f"JSON decode error: {e}")
        loguru.logger.error(f"Response text: {resp.text}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Invalid JSON response"
        ) from e

@router.get("/jobs/{job_id}/logs")
def get_job_logs(job_id: UUID) -> JobLogsResponse:
    resp = requests.get(urllib.parse.urljoin(settings.ray_jobs, f"{job_id}/logs"))

    if resp.status_code == HTTPStatus.NOT_FOUND:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Job logs for ID: {job_id} not found - {resp.text or ''}",
        )
    elif resp.status_code == HTTPStatus.BAD_REQUEST:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Job ID: {job_id} not submitted via the Ray API - {resp.text or ''}",
        )
    elif resp.status_code != HTTPStatus.OK:
        loguru.logger.error(f"Unexpected status code getting job logs text: {resp.status_code}")
        loguru.logger.error(f"Upstream job metadata response: {resp}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error getting job logs for ID: {job_id} - {resp.text or ''}",
        )

    try:
        metadata = json.loads(resp.text)
        return JobLogsResponse(**metadata)
    except json.JSONDecodeError as e:
        loguru.logger.error(f"JSON decode error: {e}")
        loguru.logger.error(f"Response text: {resp.text}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Invalid JSON response"
        ) from e


@router.get("/jobs/")
def get_all_jobs() -> list[JobSubmissionResponse]:
    resp = requests.get(settings.ray_jobs)
    if resp.status_code != HTTPStatus.OK:
        loguru.logger.error(f"Unexpected status code getting job logs text: {resp.status_code}")
        loguru.logger.error(f"Upstream job metadata response: {resp}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error getting job logs - {resp.text or ''}",
        )
    try:
        metadata = json.loads(resp.text)
        submissions: list[JobSubmissionResponse] = [
            JobSubmissionResponse(**item) for item in metadata
        ]
        return submissions
    except json.JSONDecodeError as e:
        loguru.logger.error(f"JSON decode error: {e}")
        loguru.logger.error(f"Response text: {resp.text}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Invalid JSON response"
        ) from e
