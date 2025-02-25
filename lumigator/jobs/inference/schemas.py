"""Schema file that is loaded by the backend to validate the input/output data.
This file must only depend on pydantic and not on any other external library.
This is because the backend and this job will be running in different environments.
"""

from pydantic import BaseModel, ConfigDict


class DatasetConfig(BaseModel):
    path: str
    model_config = ConfigDict(extra="forbid")


class JobConfig(BaseModel):
    max_samples: int
    storage_path: str
    output_field: str | None = "predictions"
    enable_tqdm: bool = True
    model_config = ConfigDict(extra="forbid")


class InferenceServerConfig(BaseModel):
    base_url: str | None = None
    model: str
    provider: str
    system_prompt: str | None
    max_retries: int
    model_config = ConfigDict(extra="forbid")


class GenerationConfig(BaseModel):
    """Custom and limited configuration for generation.
    Sort of a subset of HF GenerationConfig
    https://huggingface.co/docs/transformers/en/main_classes/text_generation#transformers.GenerationConfig
    """

    max_new_tokens: int
    frequency_penalty: float
    temperature: float
    top_p: float
    model_config = ConfigDict(extra="forbid")


class HuggingFacePipelineConfig(BaseModel, arbitrary_types_allowed=True):
    model_name_or_path: str
    revision: str
    use_fast: bool
    trust_remote_code: bool
    torch_dtype: str
    accelerator: str
    model_config = ConfigDict(extra="forbid")
    truncation: bool = True
    task: str | None = None


class InferenceJobConfig(BaseModel):
    name: str
    dataset: DatasetConfig
    job: JobConfig
    system_prompt: str | None = None
    inference_server: InferenceServerConfig | None = None
    generation_config: GenerationConfig | None = None
    hf_pipeline: HuggingFacePipelineConfig | None = None
    model_config = ConfigDict(extra="forbid")


class InferenceJobOutput(BaseModel):
    predictions: list | None = None
    examples: list
    ground_truth: list | None = None
    model: str
    inference_time: float


class JobOutput(BaseModel):
    # Nothing to put in metrics yet
    # but eventually we will have metrics like tok/s, latency, average output length, etc.
    metrics: None
    artifacts: InferenceJobOutput
    parameters: InferenceJobConfig
