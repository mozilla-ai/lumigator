import datetime
from uuid import UUID

from pydantic import BaseModel

from lumigator_schemas.workflows import WorkflowDetailsResponse


class ExperimentCreate(BaseModel):
    name: str
    description: str = ""
    model: str
    task: str | None = "summarization"
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    model_url: str | None = None
    system_prompt: str | None = None
    inference_output_field: str = "predictions"
    config_template: str | None = None


class ExperimentIdCreate(BaseModel):
    name: str
    description: str = ""
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    task: str | None = "summarization"


class GetExperimentResponse(BaseModel, from_attributes=True):
    id: str
    name: str
    description: str
    created_at: datetime.datetime
    task: str
    dataset: UUID
    updated_at: datetime.datetime | None = None
    workflows: list[WorkflowDetailsResponse] | None = None


class ExperimentResultResponse(BaseModel, from_attributes=True):
    id: str
    experiment_id: UUID


class ExperimentResultDownloadResponse(BaseModel):
    id: str
    download_url: str
