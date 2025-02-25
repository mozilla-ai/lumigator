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


SYSTEM_PROMPT_DEFAULTS = {
    TaskType.SUMMARIZATION: "You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences.",  # noqa: E501
    TaskType.TRANSLATION: lambda task_definition: (
        f"translate {task_definition.source_language} to {task_definition.target_language}:"
    ),
}


def validate_system_prompt(task_type: TaskType, system_prompt: str | None) -> None:
    if task_type == TaskType.TEXT_GENERATION and not system_prompt:
        raise ValueError(
            f"system_prompt required for task=`{TaskType.TEXT_GENERATION.value}`, Received: {system_prompt}"
        )


def get_default_system_prompt(task_definition: TaskDefinition) -> str:
    generator = SYSTEM_PROMPT_DEFAULTS.get(task_definition.task)
    if not generator:
        raise ValueError(f"No default system_prompt defined for {task_definition.task.value}")
    return generator(task_definition) if callable(generator) else generator
