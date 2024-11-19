import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from lumigator_schemas.jobs import JobStatus


class ExperimentCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    description: str = ""
    model: str
    dataset: UUID
    max_samples: int = -1 # set to all samples by default
    model_url: str | None = None
    system_prompt: str | None = None
    config_template: str | None = None


class ExperimentResponse(BaseModel, from_attributes=True):
    model_config = ConfigDict(extra='forbid')
    id: UUID
    name: str
    description: str
    status: JobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None


class ExperimentResultResponse(BaseModel, from_attributes=True):
    model_config = ConfigDict(extra='forbid')
    id: UUID
    experiment_id: UUID


class ExperimentResultDownloadResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: UUID
    download_url: str
