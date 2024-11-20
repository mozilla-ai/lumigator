from pydantic import BaseModel, ConfigDict

from lumigator_schemas.jobs import JobType

# Model class definitions

class DatasetConfig(BaseModel):
    path: str
    model_config = ConfigDict(extra="forbid")


class JobConfig(BaseModel):
    max_samples: int = -1 # set to all samples by default
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


class InferenceJobConfig(BaseModel):
    name: str
    dataset: DatasetConfig
    job: JobConfig
    inference_server: InferenceServerConfig
    params: SamplingParameters
    model_config = ConfigDict(extra="forbid")

# Job properties
# NOTE maybe make a @property and/or a dict/obj/pydantic model
# typing.Protocol might be used to allow IDE support
COMMAND = "python inference.py"
PIP_REQS = "requirements.txt"
WORK_DIR = None
MODEL = InferenceJobConfig
JOB_TYPE = JobType.INFERENCE