import datetime
from uuid import UUID

from pydantic import BaseModel, Field, PositiveInt

from lumigator_schemas.jobs import (
    GenerationConfig,
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
    secret_key_name: str | None = Field(
        None,
        title="Secret Key Name",
        description="An optional secret key name. Identifies an existing secret stored in Lumigator "
        "that should be used to access the provider.",
    )
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    batch_size: PositiveInt = 1
    base_url: str | None = None
    system_prompt: str | None = Field(default_factory=lambda data: get_default_system_prompt(data["task_definition"]))
    inference_output_field: str = "predictions"
    config_template: str | None = None
    generation_config: GenerationConfig = Field(default_factory=GenerationConfig)
    job_timeout_sec: PositiveInt = 60 * 60
    # Eventually metrics should be managed by the experiment level https://github.com/mozilla-ai/lumigator/issues/1105
    metrics: list[str] | None = None


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
