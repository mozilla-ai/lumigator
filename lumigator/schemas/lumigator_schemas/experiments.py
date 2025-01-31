import datetime
from uuid import UUID

from pydantic import BaseModel

from lumigator_schemas.workflows import WorkflowDetailsResponse


class ExperimentCreate(BaseModel):
    name: str
    description: str = ""
    model: str
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    model_url: str | None = None
    system_prompt: str | None = None
    inference_output_field: str = "predictions"
    config_template: str | None = None


class ExperimentIdCreate(BaseModel):
    name: str
    description: str = ""


class ExperimentIdResponse(BaseModel):
    id: str
    created_at: datetime.datetime


class GetExperimentResponse(BaseModel, from_attributes=True):
    id: str
    name: str
    created_at: datetime.datetime
    workflows: list[WorkflowDetailsResponse] | None = None


class ExperimentResponse(BaseModel, from_attributes=True):
    id: str
    name: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None


class ExperimentResultResponse(BaseModel, from_attributes=True):
    id: str
    experiment_id: UUID


class ExperimentResultDownloadResponse(BaseModel):
    id: str
    download_url: str
