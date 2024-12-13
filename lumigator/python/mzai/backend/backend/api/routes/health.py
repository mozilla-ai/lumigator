import json
from http import HTTPStatus
from urllib.parse import urljoin
from uuid import UUID

import loguru
import requests
from fastapi import APIRouter, HTTPException
from lumigator_schemas.extras import HealthResponse
from lumigator_schemas.jobs import JobLogsResponse

from backend.settings import settings

router = APIRouter()


@router.get("/")
def get_health() -> HealthResponse:
    return HealthResponse(deployment_type=settings.DEPLOYMENT_TYPE, status="OK")


@router.get("/jobs/{job_id}/logs")
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
