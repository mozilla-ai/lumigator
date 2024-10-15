from fastapi import APIRouter

from backend.settings import settings
from schemas.extras import HealthResponse
from schemas.jobs import JobSubmissionResponse
import requests
import json
from uuid import UUID
from backend.settings import settings
from typing import List

router = APIRouter()


@router.get("/")
def get_health() -> HealthResponse:
    return HealthResponse(deployment_type=settings.DEPLOYMENT_TYPE, status="OK")


@router.get("/jobs/{job_id}")
def get_job_metadata(job_id: UUID) -> JobSubmissionResponse:
    resp = requests.get(f"{settings.RAY_DASHBOARD_URL}/api/ray_submit/{job_id}")
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
    resp = requests.get(f"{settings.RAY_DASHBOARD_URL}/api/ray_submit/")
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
