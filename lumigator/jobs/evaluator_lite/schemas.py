"""Schema file that is loaded by the backend to validate the input/output data.
This file must only depend on pydantic and not on any other external library.
This is because the backend and this job will be running in different environments.
"""

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
    evaluation: EvaluationConfig
    model_config = ConfigDict(extra="forbid")


class BertScore(BaseModel):
    precision: list[float]
    recall: list[float]
    f1: list[float]
    hashcode: str
    precision_mean: float
    recall_mean: float
    f1_mean: float


class Meteor(BaseModel):
    meteor: list[float]
    meteor_mean: float


class Rouge(BaseModel):
    rouge1: list[float]
    rouge2: list[float]
    rougeL: list[float]  # noqa: N815
    rougeLsum: list[float]  # noqa: N815
    rouge1_mean: float
    rouge2_mean: float
    rougeL_mean: float  # noqa: N815
    rougeLsum_mean: float  # noqa: N815


class EvalJobMetrics(BaseModel):
    bertscore: BertScore | None = None
    meteor: Meteor | None = None
    rouge: Rouge | None = None


class EvalJobArtifacts(BaseModel):
    predictions: list[str] | None = None
    ground_truth: list[str] | None = None


class JobOutput(BaseModel):
    metrics: EvalJobMetrics
    parameters: EvalJobConfig
    artifacts: EvalJobArtifacts | None
