import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from lumigator_schemas.tasks import SummarizationTaskDefinition, TaskDefinition
from lumigator_schemas.workflows import WorkflowDetailsResponse


class ExperimentCreate(BaseModel):
    name: str
    description: str = ""
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    task_definition: TaskDefinition = Field(default_factory=lambda: SummarizationTaskDefinition())


class GetExperimentResponse(BaseModel, from_attributes=True):
    id: str
    name: str
    description: str
    created_at: datetime.datetime
    task_definition: TaskDefinition
    dataset: UUID
    updated_at: datetime.datetime | None = None
    workflows: list[WorkflowDetailsResponse] | None = None
