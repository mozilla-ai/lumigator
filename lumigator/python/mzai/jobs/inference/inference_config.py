from pydantic import BaseModel


class DatasetConfig(BaseModel):
    path: str


class JobConfig(BaseModel):
    max_samples: int = 0
    storage_path: str
    output_field: str = "prediction"
    enable_tqdm: bool = True


class InferenceServerConfig(BaseModel):
    base_url: str
    engine: str
    system_prompt: str | None
    max_retries: int = 3


class SamplingParameters(BaseModel):
    max_tokens: int = 1024
    frequency_penalty: float = 0.0
    temperature: float = 1.0
    top_p: float = 1.0


class InferenceJobConfig(BaseModel):
    name: str
    dataset: DatasetConfig
    job: JobConfig
    server: InferenceServerConfig
    params: SamplingParameters
