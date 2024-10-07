import datetime
from uuid import UUID

from pydantic import BaseModel
from typing import Optional
from schemas.jobs import JobStatus


class ExperimentCreate(BaseModel):
    name: str
    description: str = ""
    model: str
    dataset: UUID
    max_samples: int | None = None
    model_url: str | None = None
    system_prompt: str | None = None
    config_template: str | None = None


class ExperimentResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: JobStatus
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None


class ExperimentResultResponse(BaseModel, from_attributes=True):
    id: UUID
    experiment_id: UUID


class ExperimentResultDownloadResponse(BaseModel):
    id: UUID
    download_url: str
