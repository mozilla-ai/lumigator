from pydantic import Field, conlist, field_validator, model_validator

from lm_buddy.configs.common import LMBuddyConfig
from lm_buddy.configs.huggingface import (
    AutoModelConfig,
    AutoTokenizerConfig,
    DatasetConfig,
    QuantizationConfig,
)
from lm_buddy.configs.jobs.common import JobConfig
from lm_buddy.configs.vllm import VLLMCompletionsConfig
from lm_buddy.paths import AssetPath


class HuggingFaceEvaluationConfig(LMBuddyConfig):
    """Misc settings provided to an lm-harness evaluation job."""

    metrics: conlist(str, min_length=1)
    use_pipeline: bool = False
    enable_tqdm: bool = False
    max_samples: int | None = None
    storage_path: str | None = None
    return_input_data: bool = False
    return_predictions: bool = False


class HuggingFaceEvalJobConfig(JobConfig):
    """Configuration to run a HuggingFace evaluation job."""

    dataset: DatasetConfig = Field(
        description="Dataset of text completions to evaluate using the Prometheus judge model."
    )
    evaluation: HuggingFaceEvaluationConfig
    model: AutoModelConfig | VLLMCompletionsConfig
    quantization: QuantizationConfig | None = None
    tokenizer: AutoTokenizerConfig

    @model_validator(mode="before")
    def ensure_tokenizer_config(cls, values):
        """Set the tokenizer to the model path when not explicitly provided."""
        if values.get("tokenizer") is None:
            values["tokenizer"] = {}
            match values["model"]:
                case str() as model_path:
                    values["tokenizer"]["path"] = model_path
                case dict() as model_data:
                    # if dict we might have model.path specified
                    # if we don't it is VLLMCompletion and we are ok
                    # with anything as it will be ignored
                    if model_data.get("path") is None:
                        values["tokenizer"]["path"] = "oai://tokenizer"
                    else:
                        values["tokenizer"]["path"] = model_data.get("path")
                case AutoModelConfig() as model_config:
                    values["tokenizer"]["path"] = model_config.path
                # No fallback necessary, downstream validation will flag invalid model types
        return values

    @field_validator("model", mode="before")
    def validate_model_arg(cls, x):
        """Allow for passing just a path string as the model argument."""
        if isinstance(x, str):
            return AutoModelConfig(path=x)
        return x

    @field_validator("tokenizer", mode="before")
    def validate_tokenizer_arg(cls, x):
        """Allow for passing just a path string as the tokenizer argument."""
        if isinstance(x, str):
            return AutoTokenizerConfig(path=x)
        return x

    def asset_paths(self) -> list[AssetPath]:
        match self.model:
            case AutoModelConfig() as config:
                return {
                    self.dataset.path,
                    self.evaluation.output_path,
                    config.path,
                    self.tokenizer.path,
                }
            case VLLMCompletionsConfig() as config if config.inference.engine is not None:
                return {self.dataset.path, self.evaluation.output_path, config.inference.engine}
            case _:
                return {}
