from pydantic import BaseModel, ConfigDict, Field, computed_field
from utils import resolve_model_repo


class DatasetConfig(BaseModel):
    path: str
    model_config = ConfigDict(extra="forbid")


class JobConfig(BaseModel):
    max_samples: int = -1  # set to all samples by default
    storage_path: str
    output_field: str = "prediction"
    enable_tqdm: bool = True
    model_config = ConfigDict(extra="forbid")


class InferenceServerConfig(BaseModel):
    base_url: str
    engine: str
    system_prompt: str | None
    max_retries: int = 3
    model_config = ConfigDict(extra="forbid")


class SamplingParameters(BaseModel):
    max_tokens: int = 1024
    frequency_penalty: float = 0.0
    temperature: float = 1.0
    top_p: float = 1.0
    model_config = ConfigDict(extra="forbid")


class HfPipelineConfig(BaseModel, arbitrary_types_allowed=True):
    model_path: str = Field(title="The Model HF Hub repo ID", exclude=True)
    task: str
    model_config = ConfigDict(extra="forbid")

    @computed_field
    @property
    def model(self) -> str:
        """Returns the model name.

        Returns:
            str: The model name.
        """
        return resolve_model_repo(self.model_path)


class InferenceJobConfig(BaseModel):
    name: str
    dataset: DatasetConfig
    job: JobConfig
    inference_server: InferenceServerConfig | None = None
    params: SamplingParameters | None = None
    hf_pipeline: HfPipelineConfig | None = None
    model_config = ConfigDict(extra="forbid")
