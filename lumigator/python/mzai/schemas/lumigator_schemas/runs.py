import datetime
from uuid import UUID

from pydantic import BaseModel

from lumigator_schemas.jobs import JobStatus


class RunCreate(BaseModel):
    name: str
    description: str = ""
    experiment_id: UUID
    model: str
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    model_url: str | None = None
    system_prompt: str | None = None
    inference_output_field: str = "predictions"
    config_template: str | None = None


class RunResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: JobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None


class RunResultResponse(BaseModel, from_attributes=True):
    id: UUID
    run_id: UUID


class RunResultDownloadResponse(BaseModel):
    id: UUID
    download_url: str
