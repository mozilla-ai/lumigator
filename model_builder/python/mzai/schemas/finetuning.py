import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from mzai.schemas.extras import JobStatus


class FinetuningEvent(str, Enum):
    JOB_FAILED = "job_failed"
    JOB_SUCCEEDED = "job_succeeded"


class FinetuningMessage(BaseModel):
    details: str
    event: FinetuningEvent


class FinetuningJobCreate(BaseModel):
    name: str
    description: str = ""
    config: dict = Field(default_factory=dict)


class FinetuningJobUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class FinetuningJobResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: JobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None


class FinetuningLogsResponse(BaseModel):
    id: UUID
    status: JobStatus
    logs: list[str]
