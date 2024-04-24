from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel
from ray.job_submission import JobStatus as RayJobStatus

from mzai.backend.settings import DeploymentType

ItemType = TypeVar("ItemType")


class JobStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"
    SUCCEEDED = "succeeded"

    @classmethod
    def from_ray(cls, ray_status: RayJobStatus) -> "JobStatus":
        match ray_status:
            case RayJobStatus.PENDING:
                return JobStatus.CREATED
            case RayJobStatus.RUNNING:
                return JobStatus.RUNNING
            case RayJobStatus.FAILED:
                return JobStatus.FAILED
            case RayJobStatus.STOPPED:
                return JobStatus.STOPPED
            case RayJobStatus.SUCCEEDED:
                return JobStatus.SUCCEEDED


class HealthResponse(BaseModel):
    status: str
    deployment_type: DeploymentType


class ListingResponse(BaseModel, Generic[ItemType]):
    total: int
    items: list[ItemType]
