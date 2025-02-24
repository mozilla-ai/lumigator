from abc import ABC, abstractmethod
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """TaskType refers to the different usecases supported.
    We use the same terminology as the HuggingFace library and support a subset of the tasks.
    Refer: https://huggingface.co/tasks
    When using HF models, the task type is used to determine the pipeline to use.
    """

    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    TEXT_GENERATION = "text-generation"


class TranslationDefinition(BaseModel):
    task: Literal[TaskType.TRANSLATION]
    source_language: str = Field(..., examples=["en", "English"])
    target_language: str = Field(..., examples=["de", "German"])


class SummarizationDefinition(BaseModel):
    task: Literal[TaskType.SUMMARIZATION]


class TextGenerationDefinition(BaseModel):
    task: Literal[TaskType.TEXT_GENERATION]


TaskDefinition = Annotated[
    TranslationDefinition | SummarizationDefinition | TextGenerationDefinition, Field(discriminator="task")
]


class TaskValidator(ABC):
    @abstractmethod
    def validate(self, config):
        pass


class TextGenerationValidator(TaskValidator):
    def validate(self, config):
        if config.source_language or config.target_language:
            raise ValueError(
                f"Fields source_language and target_language should not be provided when task={TaskType.SUMMARIZATION}"
                f"but got source_language={config.source_language} and target_language={config.target_language}"
            )


class TranslationValidator(TaskValidator):
    def validate(self, config):
        if not config.source_language or not config.target_language:
            raise ValueError(
                f"Both source_language and target_language must be provided when task='{TaskType.TRANSLATION},"
                f"but got source_language={config.source_language} and target_language={config.target_language}"
            )
