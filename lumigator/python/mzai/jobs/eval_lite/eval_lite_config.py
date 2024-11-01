from pydantic import BaseModel, ConfigDict


class DatasetConfig(BaseModel):
    path: str
    model_config = ConfigDict(extra="forbid")

class JobConfig(BaseModel):
    max_samples: int = 0
    storage_path: str
    input_field: str = "prediction"
    enable_tqdm: bool = True
    model_config = ConfigDict(extra="forbid")

class EvalJobConfig(BaseModel):
    name: str
    dataset: DatasetConfig
    job: JobConfig
    model_config = ConfigDict(extra="forbid")
