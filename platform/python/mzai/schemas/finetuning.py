import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from mzai.schemas.extras import JobStatus


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
