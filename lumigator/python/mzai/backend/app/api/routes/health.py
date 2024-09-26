import json
from enum import Enum
from typing import List
from uuid import UUID

import requests
from fastapi import APIRouter
from pydantic import BaseModel

from app.settings import settings


class DeploymentType(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


# from mzai.schemas.extras import HealthResponse
# from mzai.schemas.jobs import JobSubmissionResponse

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class JobSubmissionResponse(BaseModel):
    type: str | None = None
    job_id: Optional[str] = None
    submission_id: str | None = None
    driver_info: Optional[str] = None
    status: str | None = None
    entrypoint: str | None = None
    message: str | None = None
    error_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: dict = Field(default_factory=dict)
    runtime_env: dict = Field(default_factory=dict)
    driver_agent_http_address: str | None = None
    driver_node_id: str | None = None
    driver_exit_code: int | None = None


class HealthResponse(BaseModel):
    status: str
    deployment_type: DeploymentType


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


@router.get("/deployments/")
def get_summarizer_status():
    print(settings.RAY_DASHBOARD_URL)
    resp = requests.get(f"{settings.RAY_DASHBOARD_URL}/api/serve/applications/")
    if resp.status_code == 200:
        try:
            data = resp.json()
            return data
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {resp.text}")
            return {"error": "Invalid JSON response"}
    else:
        return {"error": f"HTTP error {resp.status_code}"}
