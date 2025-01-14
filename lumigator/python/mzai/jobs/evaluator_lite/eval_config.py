from pydantic import BaseModel, ConfigDict, Field


class DatasetConfig(BaseModel):
    path: str
    model_config = ConfigDict(extra="forbid")


class ModelConfig(BaseModel):
    path: str
    model_config = ConfigDict(extra="forbid")


class EvaluationConfig(BaseModel):
    metrics: list[str] = Field(default=["rouge", "meteor", "bertscore"])
    max_samples: int = 0
    return_input_data: bool = False
    return_predictions: bool = False
    storage_path: str
    model_config = ConfigDict(extra="forbid")


class EvalJobConfig(BaseModel):
    name: str
    dataset: DatasetConfig
    model: ModelConfig
    evaluation: EvaluationConfig
    model_config = ConfigDict(extra="forbid")
