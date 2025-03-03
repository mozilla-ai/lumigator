import datetime
from uuid import UUID

from pydantic import BaseModel, Field, PositiveInt

from lumigator_schemas.jobs import (
    JobResults,
    LowercaseEnum,
)
from lumigator_schemas.tasks import SummarizationTaskDefinition, TaskDefinition, get_default_system_prompt


class WorkflowStatus(LowercaseEnum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


class WorkflowCreateRequest(BaseModel):
    name: str
    description: str = ""
    experiment_id: str | None = None
    task_definition: TaskDefinition = Field(default_factory=lambda: SummarizationTaskDefinition())
    model: str
    provider: str
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    base_url: str | None = None
    system_prompt: str | None = Field(default_factory=lambda data: get_default_system_prompt(data["task_definition"]))
    inference_output_field: str = "predictions"
    config_template: str | None = None
    job_timeout_sec: PositiveInt = 60 * 10


class WorkflowResponse(BaseModel, from_attributes=True):
    id: str
    experiment_id: str
    model: str
    name: str
    description: str
    system_prompt: str
    status: WorkflowStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None


# This schema extends workflow response and adds a few more fields
class WorkflowDetailsResponse(WorkflowResponse):
    jobs: list[JobResults] | None = None
    metrics: dict | None = None
    parameters: dict | None = None
    artifacts_download_url: str | None = None
