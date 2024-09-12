from pydantic import Field, field_validator, model_validator

from lm_buddy.configs.common import LMBuddyConfig
from lm_buddy.configs.huggingface import (
    AdapterConfig,
    AutoModelConfig,
    AutoTokenizerConfig,
    DatasetConfig,
    QuantizationConfig,
    TrainerConfig,
)
from lm_buddy.configs.jobs.common import JobConfig
from lm_buddy.paths import AssetPath


class FinetuningRayConfig(LMBuddyConfig):
    """Misc settings passed to Ray train for finetuning.

    Includes information for scaling, checkpointing, and runtime storage.
    """

    use_gpu: bool = True
    num_workers: int | None = None
    storage_path: str | None = None  # TODO: This should be set globally somehow


class FinetuningJobConfig(JobConfig):
    """Configuration to submit an LLM finetuning job."""

    model: AutoModelConfig
    dataset: DatasetConfig
    tokenizer: AutoTokenizerConfig
    quantization: QuantizationConfig | None = None
    adapter: AdapterConfig | None = None
    trainer: TrainerConfig = Field(default_factory=TrainerConfig)
    ray: FinetuningRayConfig = Field(default_factory=FinetuningRayConfig)

    @model_validator(mode="before")
    def ensure_tokenizer_config(cls, values):
        """Set the tokenizer to the model path when not explicitly provided."""
        if values.get("tokenizer") is None:
            values["tokenizer"] = {}
            match values["model"]:
                case str() as model_path:
                    values["tokenizer"]["path"] = model_path
                case dict() as model_data:
                    values["tokenizer"]["path"] = model_data["path"]
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
        return {self.model.path, self.dataset.path, self.tokenizer.path}
