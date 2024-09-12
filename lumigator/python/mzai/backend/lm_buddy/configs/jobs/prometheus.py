from pydantic import Field

from lm_buddy.configs.common import LMBuddyConfig
from lm_buddy.configs.huggingface import DatasetConfig
from lm_buddy.configs.jobs.common import JobConfig
from lm_buddy.configs.vllm import VLLMCompletionsConfig
from lm_buddy.paths import AssetPath


class PrometheusEvaluationConfig(LMBuddyConfig):
    """Parameters specific to Prometheus evaluation."""

    num_answers: int = 3
    max_retries: int = 5
    scores: list = [1, 2, 3, 4, 5]
    min_score: int = 0
    max_score: int = 5
    enable_tqdm: bool = False
    conversation_template: str = "llama-2"
    conversation_system_message: str = "You are a fair evaluator language model."
    storage_path: str | None = None


class PrometheusJobConfig(JobConfig):
    """Configuration for a Prometheus judge evaluation task."""

    prometheus: VLLMCompletionsConfig = Field(
        description="Externally hosted Prometheus judge model."
    )
    dataset: DatasetConfig = Field(
        description="Dataset of text completions to evaluate using the Prometheus judge model."
    )
    evaluation: PrometheusEvaluationConfig = Field(
        default_factory=PrometheusEvaluationConfig,
        description="Settings for the Prometheus evaluation.",
    )

    def asset_paths(self) -> set[AssetPath]:
        paths = {self.dataset.path, self.prometheus.inference.engine}
        return {x for x in paths if x is not None}
