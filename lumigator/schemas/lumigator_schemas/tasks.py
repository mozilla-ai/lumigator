from enum import Enum
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class LowercaseEnum(str, Enum):
    """Can be used to ensure that values for enums are returned in lowercase."""

    def __new__(cls, value):
        obj = super().__new__(cls, value.lower())
        obj._value_ = value.lower()
        return obj


class TaskType(LowercaseEnum, Enum):
    """TaskType refers to the different use cases supported.
    We use the same terminology as the HuggingFace library and support a subset of the tasks.
    Refer: https://huggingface.co/tasks
    When using HF models, the task type is used to determine the pipeline to use.
    """

    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    TEXT_GENERATION = "text-generation"


class Metric(LowercaseEnum, Enum):
    """Metric refers to the different metrics used as defaults and supported for evaluation."""

    ROUGE = "rouge"
    METEOR = "meteor"
    BERTSCORE = "bertscore"
    BLEU = "bleu"
    COMET = "comet"


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


@lru_cache(maxsize=len(TaskType))
def get_metrics_for_task(task_type: TaskType) -> set[Metric]:
    """Retrieves the set of default metrics associated with the given task type.

    :param task_type: The task type for which metrics should be retrieved (e.g. 'summarization', 'translation').
    :return: A set of metrics associated with the given task type.
    :raises KeyError: If the task type is mapped to a set of default metrics.
    """
    # NOTE: If changing the default metrics, please ensure that they do not include
    # any requirements for external API calls that require an API key to be configured.
    metrics_by_task = {
        TaskType.SUMMARIZATION: {Metric.BERTSCORE, Metric.METEOR, Metric.ROUGE},
        TaskType.TRANSLATION: {Metric.BLEU, Metric.COMET, Metric.METEOR},
        TaskType.TEXT_GENERATION: {Metric.BERTSCORE, Metric.BLEU, Metric.METEOR, Metric.ROUGE},
    }

    return metrics_by_task[task_type]
