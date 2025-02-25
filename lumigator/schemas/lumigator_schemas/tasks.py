from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    system_prompt: str = Field(
        default="You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences.",  # noqa: E501
        description="System prompt for summarization tasks",
    )
    model_config = ConfigDict(extra="forbid")


class TranslationTaskDefinition(BaseModel):
    task: Literal[TaskType.TRANSLATION] = TaskType.TRANSLATION
    system_prompt: str | None = Field(
        default=None, description="System prompt for translation tasks", examples=["translate English to German"]
    )
    source_language: str = Field(examples=["en", "English"])
    target_language: str = Field(examples=["de", "German"])
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def set_translation_prompt(self):
        if not self.system_prompt:
            self.system_prompt = f"translate {self.source_language} to {self.target_language}:"
        return self


class TextGenerationTaskDefinition(BaseModel):
    task: Literal[TaskType.TEXT_GENERATION] = TaskType.TEXT_GENERATION
    system_prompt: str = Field(description="System prompt needs to be set by the user for for text-generation tasks")
    model_config = ConfigDict(extra="forbid")


TaskDefinition = Annotated[
    SummarizationTaskDefinition | TranslationTaskDefinition | TextGenerationTaskDefinition, Field(discriminator="task")
]
