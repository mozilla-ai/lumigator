import dataclasses
from typing import Any

from peft import PeftConfig, PeftType, TaskType
from pydantic import field_validator, model_validator
from transformers import BitsAndBytesConfig

from lm_buddy.configs.common import LMBuddyConfig, SerializableTorchDtype
from lm_buddy.paths import AssetPath, PathPrefix

DEFAULT_TEXT_FIELD: str = "text"


class AutoModelConfig(LMBuddyConfig):
    """Settings passed to a HuggingFace AutoModel instantiation.

    The model to load can either be a HuggingFace repo or an artifact reference on W&B.
    """

    path: AssetPath
    trust_remote_code: bool = False
    torch_dtype: SerializableTorchDtype | None = None


class AutoTokenizerConfig(LMBuddyConfig):
    """Settings passed to a HuggingFace AutoTokenizer instantiation."""

    path: AssetPath
    trust_remote_code: bool | None = None
    use_fast: bool | None = None
    mod_max_length: int | None = None


class DatasetConfig(LMBuddyConfig):
    """Settings passed to load a HuggingFace text dataset.

    The dataset can either contain a single text column named by the `text_field` parameter,
    or a `prompt_template` can be provided to format columns of the dataset as the `text_field`.
    """

    path: AssetPath
    text_field: str = DEFAULT_TEXT_FIELD
    prompt_template: str | None = None
    split: str | None = None
    test_size: float | None = None
    seed: int | None = None

    @model_validator(mode="after")
    def validate_split_if_huggingface_path(cls, config: "DatasetConfig"):
        """
        Ensure a  `split` is provided when loading a HuggingFace dataset directly from HF Hub.
        This makes it such that the `load_dataset` function returns the type `Dataset`
        instead of `DatasetDict`, which makes some of the downstream logic easier.
        """
        if config.split is None and config.path.startswith(PathPrefix.HUGGINGFACE):
            raise ValueError(
                "A `split` must be specified when loading a dataset directly from HuggingFace."
            )
        return config


class AdapterConfig(LMBuddyConfig, extra="allow"):
    """Configuration containing PEFT adapter settings.

    The type of adapter is controlled by the required `peft_type` field,
    which must be one of the allowed values from the PEFT `PeftType` enumeration.
    Extra arguments are allowed and are passed down to the HuggingFace `PeftConfig`
    class determined by the `peft_type` argument.

    The `task_type` for the adapter is also required.
    By default, this is set to `TaskType.CAUSAL_LM`
    which is appropriate for causal language model finetuning.
    See the allowed values in the PEFT `TaskType` enumeration.
    """

    peft_type: PeftType
    task_type: TaskType = TaskType.CAUSAL_LM

    @staticmethod
    def _get_peft_config_class(peft_type: PeftType) -> type[PeftConfig]:
        # Internal import to avoid bringing the global variable from peft into module scope
        from peft.mapping import PEFT_TYPE_TO_CONFIG_MAPPING

        return PEFT_TYPE_TO_CONFIG_MAPPING[peft_type]

    @field_validator("peft_type", "task_type", mode="before")
    def sanitize_enum_args(cls, x):
        if isinstance(x, str):
            x = x.strip().upper()
        return x

    @model_validator(mode="after")
    def validate_adapter_args(cls, config: "AdapterConfig"):
        peft_type = config.peft_type

        # PeftConfigs are standard dataclasses so can extract their allowed field names
        adapter_cls = cls._get_peft_config_class(peft_type)
        allowed_fields = {x.name for x in dataclasses.fields(adapter_cls)}

        # Filter fields to those found on the PeftConfig
        extra_fields = config.model_fields_set.difference(allowed_fields)
        if extra_fields:
            raise ValueError(f"Unknown arguments for {peft_type} adapter: {extra_fields}")

        return config

    def as_huggingface(self) -> PeftConfig:
        adapter_cls = self._get_peft_config_class(self.peft_type)
        return adapter_cls(**self.model_dump())


class QuantizationConfig(LMBuddyConfig):
    """Basic quantization settings to pass to training and evaluation jobs.

    Note that in order to use BitsAndBytes quantization on Ray,
    you must ensure that the runtime environment is installed with GPU support.
    This can be configured by setting the `entrypoint_num_gpus > 0` when submitting a job
    to the cluster.
    """

    load_in_8bit: bool | None = None
    load_in_4bit: bool | None = None
    bnb_4bit_quant_type: str = "fp4"
    bnb_4bit_compute_dtype: SerializableTorchDtype | None = None

    def as_huggingface(self) -> BitsAndBytesConfig:
        return BitsAndBytesConfig(
            load_in_4bit=self.load_in_4bit,
            load_in_8bit=self.load_in_8bit,
            bnb_4bit_compute_dtype=self.bnb_4bit_compute_dtype,
            bnb_4bit_quant_type=self.bnb_4bit_quant_type,
        )


class TrainerConfig(LMBuddyConfig):
    """Configuration for a HuggingFace trainer/training arguments.

    This mainly encompasses arguments passed to the HuggingFace `TrainingArguments` class,
    but also contains some additional parameters for the `Trainer` or `SFTTrainer` classes.
    """

    max_seq_length: int | None = None
    num_train_epochs: float | None = None
    per_device_train_batch_size: int | None = None
    per_device_eval_batch_size: int | None = None
    learning_rate: float | None = None
    weight_decay: float | None = None
    gradient_accumulation_steps: int | None = None
    gradient_checkpointing: bool | None = None
    evaluation_strategy: str | None = None
    eval_steps: float | None = None
    logging_strategy: str | None = None
    logging_steps: float | None = None
    save_strategy: str | None = None
    save_steps: int | None = None

    def training_args(self) -> dict[str, Any]:
        """Return the arguments to the HuggingFace `TrainingArguments` class."""
        return self.model_dump(exclude={"max_seq_length"}, exclude_none=True)
