from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskType(str, Enum):
    """TaskType refers to the different usecases supported.
    We use the same terminology as the HuggingFace library and support a subset of the tasks.
    Refer: https://huggingface.co/tasks
    When using HF models, the task type is used to determine the pipeline to use.
    """

    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    TEXT_GENERATION = "text-generation"


class SummarizationTaskDefinition(BaseModel):
    task: Literal[TaskType.SUMMARIZATION] = TaskType.SUMMARIZATION
    model_config = ConfigDict(extra="forbid")


class TranslationTaskDefinition(BaseModel):
    task: Literal[TaskType.TRANSLATION] = TaskType.TRANSLATION
    source_language: str = Field(examples=["en", "English"])
    target_language: str = Field(examples=["de", "German"])
    model_config = ConfigDict(extra="forbid")


class TextGenerationTaskDefinition(BaseModel):
    task: Literal[TaskType.TEXT_GENERATION] = TaskType.TEXT_GENERATION
    model_config = ConfigDict(extra="forbid")


TaskDefinition = Annotated[
    SummarizationTaskDefinition | TranslationTaskDefinition | TextGenerationTaskDefinition, Field(discriminator="task")
]
