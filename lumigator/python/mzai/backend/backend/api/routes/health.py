import json
from uuid import UUID

import requests
from fastapi import APIRouter
from schemas.extras import HealthResponse
from schemas.jobs import JobSubmissionResponse

from backend.settings import settings

router = APIRouter()


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
def get_all_jobs() -> list[JobSubmissionResponse]:
    resp = requests.get(f"{settings.RAY_DASHBOARD_URL}/api/jobs/")
    if resp.status_code == 200:
        try:
            metadata = json.loads(resp.text)
            submissions: list[JobSubmissionResponse] = [
                JobSubmissionResponse(**item) for item in metadata
            ]
            return submissions
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {resp.text}")
            return {"error": "Invalid JSON response"}
    else:
        return {"error": f"HTTP error {resp.status_code}"}
