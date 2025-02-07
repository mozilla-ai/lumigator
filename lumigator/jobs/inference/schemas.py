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
    output_field: str | None = None
    enable_tqdm: bool | None = None
    model_config = ConfigDict(extra="forbid")


class InferenceServerConfig(BaseModel):
    base_url: str
    engine: str
    system_prompt: str | None
    max_retries: int
    model_config = ConfigDict(extra="forbid")


class SamplingParameters(BaseModel):
    max_tokens: int
    frequency_penalty: float
    temperature: float
    top_p: float
    model_config = ConfigDict(extra="forbid")


class HfPipelineConfig(BaseModel, arbitrary_types_allowed=True):
    model_uri: str
    revision: str
    use_fast: bool
    trust_remote_code: bool
    torch_dtype: str
    accelerator: str
    model_config = ConfigDict(extra="forbid")
    max_new_tokens: int
    truncation: bool = True
    task: str | None = None


class InferenceJobConfig(BaseModel):
    name: str
    dataset: DatasetConfig
    job: JobConfig
    inference_server: InferenceServerConfig | None = None
    params: SamplingParameters | None = None
    hf_pipeline: HfPipelineConfig | None = None
    model_config = ConfigDict(extra="forbid")


class InferenceJobOutput(BaseModel):
    predictions: list | None = None
    examples: list
    ground_truth: list | None = None
    model: str
