from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class JobType(str, Enum):
    EXPERIMENT = "experiment"
    FINETUNING = "finetuning"


class JobStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


class JobConfig(BaseModel):
    job_id: UUID
    job_type: JobType
    args: dict[str, Any]


class JobEvent(BaseModel):
    job_id: UUID
    job_type: JobType
    status: JobStatus
    detail: str | None = None


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
