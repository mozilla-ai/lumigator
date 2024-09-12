from typing import Literal

from pydantic import conlist, model_validator

from lm_buddy.configs.common import LMBuddyConfig
from lm_buddy.configs.huggingface import AutoModelConfig, QuantizationConfig
from lm_buddy.configs.jobs.common import JobConfig
from lm_buddy.configs.vllm import InferenceServerConfig
from lm_buddy.paths import AssetPath


class LocalChatCompletionsConfig(LMBuddyConfig):
    """Configuration for a "local-chat-completions" model in lm-harness.

    The "local-chat-completions" model is powered by a self-hosted inference server,
    specified as an `InferenceServerConfig`. Additional arguments are also provided
    to control the tokenizer type and generation parameters.
    """

    inference: InferenceServerConfig
    truncate: bool = False
    max_tokens: int = 256
    tokenizer_backend: Literal["huggingface", "tiktoken"] = "huggingface"

    @model_validator(mode="after")
    def validate_inference_engine(cls, config: "LocalChatCompletionsConfig"):
        if config.inference.engine is None:
            raise ValueError(
                "Inference config `engine` must be provided for use in "
                "lm-harness 'local-chat-completions' model."
            )
        return config


class LMHarnessEvaluationConfig(LMBuddyConfig):
    """Misc settings provided to an lm-harness evaluation job."""

    tasks: conlist(str, min_length=1)
    batch_size: int | None = None
    num_fewshot: int | None = None
    limit: int | float | None = None


class LMHarnessJobConfig(JobConfig):
    """Configuration to run an lm-evaluation-harness evaluation job."""

    model: AutoModelConfig | LocalChatCompletionsConfig
    evaluation: LMHarnessEvaluationConfig
    quantization: QuantizationConfig | None = None

    def asset_paths(self) -> list[AssetPath]:
        match self.model:
            case AutoModelConfig() as config:
                return {config.path}
            case LocalChatCompletionsConfig() as config if config.inference.engine is not None:
                return {config.inference.engine}
            case _:
                return {}
