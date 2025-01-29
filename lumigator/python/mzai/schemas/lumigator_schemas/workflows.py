import datetime
from uuid import UUID

from pydantic import BaseModel

from lumigator_schemas.jobs import JobResults, LowercaseEnum


class WorkflowStatus(LowercaseEnum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


class WorkflowCreateRequest(BaseModel):
    name: str
    description: str = ""
    experiment_id: str
    model: str
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    model_url: str | None = None
    system_prompt: str | None = None
    inference_output_field: str = "predictions"
    config_template: str | None = None


class WorkflowResponse(BaseModel, from_attributes=True):
    id: str
    experiment_id: str
    name: str
    description: str
    status: WorkflowStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None


# This schema extends workflow response and adds a few more fields
class WorkflowDetailsResponse(WorkflowResponse):
    jobs: list[JobResults] | None = None
    metrics: dict | None = None
    parameters: dict | None = None


class WorkflowResultDownloadResponse(BaseModel):
    id: str
    download_url: str
