from pydantic import BaseModel, ConfigDict, Field


class DatasetConfig(BaseModel):
    path: str


class ModelConfig(BaseModel):
    path: str


class EvaluationConfig(BaseModel):
    metrics: list[str] = Field(default=["rouge", "meteor", "bertscore"])
    use_pipeline: bool = False
    max_samples: int = 0
    return_input_data: bool = False
    return_predictions: bool = False
    storage_path: str = ""


class EvalJobConfig(BaseModel):
    name: str | None
    dataset: DatasetConfig
    model: ModelConfig
    evaluation: EvaluationConfig
    model_config = ConfigDict(extra="forbid")
