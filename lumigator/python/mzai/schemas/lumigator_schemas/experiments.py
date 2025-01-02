import datetime
from uuid import UUID

from pydantic import BaseModel

from lumigator_schemas.jobs import JobStatus


class ExperimentRunCreate(BaseModel):
    experiment_id: UUID
    run_description: str = ""
    model: str | None = None
    model_url: str | None = None
    system_prompt: str | None = None
    config_template: str | None = None


class ExperimentCreate(BaseModel):
    name: str
    description: str = ""
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    compared_models: list[ExperimentRunCreate] = []


class RunResponse(BaseModel):
    id: UUID
    status: JobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None


class ExperimentResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: JobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None
    runs: list[RunResponse] = []


class ExperimentResultResponse(BaseModel, from_attributes=True):
    id: UUID
    parent_experiment_id: UUID


class RunResultDownloadResponse(BaseModel, from_attributes=True):
    id: UUID
    experiment_id: UUID
    experiment_result_id: UUID
    status: JobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None


class ExperimentResultDownloadResponse(BaseModel):
    id: UUID
    download_url: str
    experiment_results_id: list[UUID] = []

    """
     , for consistency?
    this implies storing the link of experiment_id --> list[run_id] somewhere (e.g. our DB)
    else, the frontend would need to keep track of run_ids, which we don't want
    """
