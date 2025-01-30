import datetime
from uuid import UUID

from pydantic import BaseModel

from lumigator_schemas.jobs import JobResults, JobStatus


class WorkflowCreate(BaseModel):
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


class WorkflowResponse(BaseModel, from_attributes=True):
    id: UUID
    experiment_id: UUID
    name: str
    description: str
    status: JobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None


# TODO: This schema will need to be refined when the get_workflow route is implemented
class WorkflowDetailsResponse(BaseModel, from_attributes=True):
    workflow_id: UUID
    experiment_id: UUID
    jobs: list[JobResults]
    metrics: dict
    artifacts: dict
    parameters: dict


class WorkflowResultDownloadResponse(BaseModel):
    id: UUID
    download_url: str
