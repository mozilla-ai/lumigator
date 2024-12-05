from typing import Annotated, Any

import torch
from paths import AssetPath
from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer, WithJsonSchema
from transformers import BitsAndBytesConfig


def validate_torch_dtype(x: Any) -> torch.dtype:
    match x:
        case torch.dtype():
            return x
        case str() if hasattr(torch, x) and isinstance(getattr(torch, x), torch.dtype):
            return getattr(torch, x)
        case _:
            raise ValueError(f"{x} is not a valid torch.dtype.")


"""Custom type validator for a `torch.dtype` object.

Accepts `torch.dtype` instances or strings representing a valid dtype from the `torch` package.
Ref: https://docs.pydantic.dev/latest/concepts/types/#custom-types
"""
SerializableTorchDtype = Annotated[
    torch.dtype,
    BeforeValidator(lambda x: validate_torch_dtype(x)),
    PlainSerializer(lambda x: str(x).split(".")[1]),
    WithJsonSchema({"type": "string"}, mode="validation"),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]


class AutoModelConfig(
    BaseModel,
    arbitrary_types_allowed=True,
):
    """Settings passed to a HuggingFace AutoModel instantiation.

    The model to load can either be a HuggingFace repo or an artifact reference on W&B.
    """

    path: AssetPath
    trust_remote_code: bool = False
    torch_dtype: SerializableTorchDtype | None = None


class QuantizationConfig(BaseModel):
    """Basic quantization settings to pass to evaluation jobs.

    Note that in order to use BitsAndBytes quantization on Ray,
    you must ensure that the runtime environment is installed with GPU support.
    This can be configured by setting the `entrypoint_num_gpus > 0` when submitting a job
    to the cluster.
    """

    load_in_8bit: bool | None = None
    load_in_4bit: bool | None = None
    bnb_4bit_quant_type: str = "fp4"
    bnb_4bit_compute_dtype: Any | None = None

    def as_huggingface(self) -> BitsAndBytesConfig:
        return BitsAndBytesConfig(
            load_in_4bit=self.load_in_4bit,
            load_in_8bit=self.load_in_8bit,
            bnb_4bit_compute_dtype=self.bnb_4bit_compute_dtype,
            bnb_4bit_quant_type=self.bnb_4bit_quant_type,
        )


class AutoTokenizerConfig(BaseModel):
    """Settings passed to a HuggingFace AutoTokenizer instantiation."""

    path: AssetPath
    trust_remote_code: bool | None = False
    use_fast: bool | None = True
    mod_max_length: int | None = 1024


class DatasetConfig(BaseModel):
    path: str
    model_config = ConfigDict(extra="forbid")


class JobConfig(BaseModel):
    max_samples: int = -1  # set to all samples by default
    storage_path: str
    system_prompt: str | None = ""
    task: str | None = None
    output_field: str = "prediction"
    enable_tqdm: bool = True
    model_config = ConfigDict(extra="forbid")


class InferenceServerConfig(BaseModel):
    base_url: str
    engine: str
    max_retries: int = 3
    model_config = ConfigDict(extra="forbid")


class SamplingParameters(BaseModel):
    max_tokens: int = 1024
    frequency_penalty: float = 0.0
    temperature: float = 1.0
    top_p: float = 1.0
    model_config = ConfigDict(extra="forbid")


class InferenceJobConfig(BaseModel):
    name: str
    dataset: DatasetConfig
    job: JobConfig
    model: AutoModelConfig | None = None
    tokenizer: AutoTokenizerConfig | None = None
    inference_server: InferenceServerConfig | None = None
    params: SamplingParameters | None = None
    model_config = ConfigDict(extra="forbid")
