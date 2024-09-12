from typing import Literal, get_args

from pydantic import Field, field_validator

from lm_buddy.configs.common import LMBuddyConfig
from lm_buddy.configs.huggingface import AutoModelConfig, DatasetConfig
from lm_buddy.configs.jobs.common import JobConfig
from lm_buddy.configs.vllm import VLLMCompletionsConfig
from lm_buddy.paths import AssetPath

RagasEvaluationMetric = Literal[
    "faithfulness",
    "answer_relevancy",
    "context_recall",
    "context_precision",
]


class RagasEvaluationConfig(LMBuddyConfig):
    """Parameters specifically required for RAGAs Evaluation"""

    metrics: list[RagasEvaluationMetric] = Field(
        default_factory=lambda: list(get_args(RagasEvaluationMetric)),
        description="List of metric names for Ragas evaluation.",
    )
    embedding_model: AssetPath = Field(
        default="hf://sentence-transformers/all-mpnet-base-v2",
        description="Path to embedding model used with the evaluation judge.",
    )
    storage_path: str | None = Field(
        default=None,
        description="Path to store evaluation outputs. Defaults to the `LM_BUDDY_STORAGE` path.",
    )

    @field_validator("embedding_model", mode="before")
    def validate_embedding_model_arg(cls, x):
        """Allow for passing just a path string as the model argument."""
        if isinstance(x, str):
            return AutoModelConfig(path=x)
        return x


class RagasJobConfig(JobConfig):
    """Configuration to run a Ragas evaluation job.

    This job loads a dataset from an existing path on our cluster.
    The dataset must be formatted in the RAG context, with the question, generated answer,
    the contexts (retrieved), and optionally a ground truth field.
    """

    judge: VLLMCompletionsConfig = Field(description="Externally hosted Ragas judge model.")
    dataset: DatasetConfig = Field(
        description="Dataset of text completions to evaluate using the Ragas judge model."
    )
    evaluation: RagasEvaluationConfig = Field(
        default_factory=RagasEvaluationConfig,
        description="Settings for the Ragas evaluation.",
    )

    def asset_paths(self) -> set[AssetPath]:
        paths = {self.dataset.path, self.judge.inference.engine}
        return {x for x in paths if x is not None}
