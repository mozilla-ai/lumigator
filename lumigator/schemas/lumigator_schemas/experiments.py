import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator

from lumigator_schemas.tasks import TaskDefinition, TaskType, TextGenerationValidator, TranslationValidator
from lumigator_schemas.workflows import WorkflowDetailsResponse


class ExperimentCreate(BaseModel):
    name: str
    description: str = ""
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    task_definition: TaskDefinition

    @model_validator(mode="after")
    def validate_and_set_defaults(self):
        validators = {
            TaskType.TRANSLATION: TranslationValidator(),
            TaskType.SUMMARIZATION: TextGenerationValidator(),
            TaskType.TEXT_GENERATION: TextGenerationValidator(),
        }
        validator = validators.get(self.task)
        validator.validate(self)
        return self


class GetExperimentResponse(BaseModel, from_attributes=True):
    id: str
    name: str
    description: str
    created_at: datetime.datetime
    task: TaskType
    dataset: UUID
    updated_at: datetime.datetime | None = None
    workflows: list[WorkflowDetailsResponse] | None = None
