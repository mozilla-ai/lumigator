from fastapi import APIRouter

from mzai.backend.settings import settings
from mzai.schemas.extras import HealthResponse
from mzai.schemas.jobs import JobSubmissionResponse
import requests
import json
from uuid import UUID
from mzai.backend.settings import settings
from typing import List

router = APIRouter()

__all__ = ["get_health"]


@router.get("/")
def get_health() -> HealthResponse:
    return HealthResponse(deployment_type=settings.DEPLOYMENT_TYPE, status="OK")


@router.get("/jobs/{job_id}")
def get_job_metadata(job_id: UUID) -> JobSubmissionResponse:
    resp = requests.get(f"{settings.RAY_DASHBOARD_URL}/api/jobs/{job_id}")
    if resp.status_code == 200:
        try:
            metadata = json.loads(resp.text)
            return JobSubmissionResponse(**metadata)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {resp.text}")
            return {"error": "Invalid JSON response"}
    else:
        return {"error": f"HTTP error {resp.status_code}"}


@router.get("/jobs/")
def get_all_jobs() -> List[JobSubmissionResponse]:
    resp = requests.get(f"{settings.RAY_DASHBOARD_URL}/api/jobs/")
    if resp.status_code == 200:
        try:
            metadata = json.loads(resp.text)
            submissions: List[JobSubmissionResponse] = [
                JobSubmissionResponse(**item) for item in metadata
            ]
            return submissions
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {resp.text}")
            return {"error": "Invalid JSON response"}
    else:
        return {"error": f"HTTP error {resp.status_code}"}
