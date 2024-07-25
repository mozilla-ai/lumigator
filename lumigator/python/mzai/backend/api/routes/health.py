from fastapi import APIRouter

from mzai.backend.settings import settings
from mzai.schemas.extras import HealthResponse
from mzai.schemas.jobs import JobStatus
import requests
import json
from uuid import UUID
from mzai.backend.settings import settings

router = APIRouter()


@router.get("/")
async def get_health() -> HealthResponse:
    return HealthResponse(deployment_type=settings.DEPLOYMENT_TYPE, status="OK")

@router.get("/jobs/{job_id}")
async def get_job_health(job_id: UUID) -> dict:
    resp = requests.get(f"{settings.RAY_DASHBOARD_URL}/api/jobs/{job_id}")
    if resp.status_code == 200:
        try:
            rst = json.loads(resp.text)
            status = rst["status"]
            return json.loads(status)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {resp.text}")
            return {"error": "Invalid JSON response"}
    else:
        return {"error": f"HTTP error {resp.status_code}"}

@router.get("/jobs/")
async def get_jobs() -> dict:
    resp = requests.get(f"{settings.RAY_DASHBOARD_URL}/api/jobs")
    if resp.status_code == 200:
        try:
            rst = json.loads(resp.text)
            status = rst["status"]
            return json.loads(status)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {resp.text}")
            return {"error": "Invalid JSON response"}
    else:
        return {"error": f"HTTP error {resp.status_code}"}
