from enum import Enum
from uuid import UUID

from pydantic import BaseModel
from ray.job_submission import JobStatus as RayJobStatus


class JobType(str, Enum):
    EXPERIMENT = "experiment"


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


class JobEvent(BaseModel):
    id: UUID
    type: JobType
    status: JobStatus
    detail: str | None = None
