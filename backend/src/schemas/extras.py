from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel
from ray.job_submission import JobStatus as RayJobStatus

from src.settings import DeploymentType

ItemType = TypeVar("ItemType")


class JobStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    STOPPED = "stopped"
    SUCCEEDED = "succeeded"

    @classmethod
    def from_ray(cls, ray_status: RayJobStatus) -> "JobStatus":
        match ray_status:
            case RayJobStatus.PENDING | RayJobStatus.RUNNING:
                return JobStatus.IN_PROGRESS
            case RayJobStatus.FAILED:
                return JobStatus.FAILED
            case RayJobStatus.STOPPED:
                return JobStatus.STOPPED
            case RayJobStatus.SUCCEEDED:
                return JobStatus.SUCCEEDED

    def is_complete(self) -> bool:
        return self in {JobStatus.FAILED, JobStatus.STOPPED, JobStatus.SUCCEEDED}


class HealthResponse(BaseModel):
    status: str
    deployment_type: DeploymentType


class ListingResponse(BaseModel, Generic[ItemType]):
    total: int
    items: list[ItemType]
