import datetime
from uuid import UUID

from pydantic import BaseModel

from lumigator_schemas.jobs import JobStatus


class WorkflowCreate(BaseModel):
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
    name: str
    description: str
    status: JobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None


class WorkflowSummaryResponse(BaseModel, from_attributes=True):
    workflow_id: str
    experiment_id: str
    job_ids: list[str]
    metrics: dict
    artifacts: dict
    parameters: dict


# TODO: This schema will need to be refined when the WorkflowDetails route is implemented
class WorkflowDetailsResponse(BaseModel):
    workflow_id: str
    experiment_id: str
    job_ids: list[str]
    metrics_urls: list[str]  # same length as run_ids
    artifacts_urls: list[str]  # same length as run_ids


class WorkflowResultDownloadResponse(BaseModel):
    id: UUID
    download_url: str
