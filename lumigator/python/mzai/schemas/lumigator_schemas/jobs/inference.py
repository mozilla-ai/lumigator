from pydantic import BaseModel, ConfigDict


class DatasetConfig(BaseModel):
    path: str
    model_config = ConfigDict(extra="forbid")


class JobConfig(BaseModel):
    max_samples: int
    storage_path: str
    output_field: str
    enable_tqdm: bool | None
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
    max_length: int


class InferenceJobConfig(BaseModel):
    name: str
    dataset: DatasetConfig
    job: JobConfig
    inference_server: InferenceServerConfig | None
    params: SamplingParameters | None
    hf_pipeline: HfPipelineConfig | None = None
    model_config = ConfigDict(extra="forbid")
