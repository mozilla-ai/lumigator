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
    metrics: list[str] = Field(default=["rouge", "meteor", "bertscore", "bleu"])
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


class Bleu(BaseModel):
    bleu: list[float]
    bleu_mean: float


class Rouge(BaseModel):
    rouge1: list[float]
    rouge2: list[float]
    rougeL: list[float]  # noqa: N815
    rougeLsum: list[float]  # noqa: N815
    rouge1_mean: float
    rouge2_mean: float
    rougeL_mean: float  # noqa: N815
    rougeLsum_mean: float  # noqa: N815


class GEvalMetric(BaseModel):
    """A single result from a G-Eval evaluation (a score + an explanation)."""

    score: float
    reason: str


class GEvalSummarizationMetrics(BaseModel):
    """The following metric names and their respective prompts are defined in `g_eval_prompts.json`."""

    coherence: list[GEvalMetric]
    coherence_mean: float
    consistency: list[GEvalMetric]
    consistency_mean: float
    fluency: list[GEvalMetric]
    fluency_mean: float
    relevance: list[GEvalMetric]
    relevance_mean: float


class TokenLength(BaseModel):
    ref_token_length: list[int]
    pred_token_length: list[int]
    ref_token_length_mean: float
    pred_token_length_mean: float


class EvalJobMetrics(BaseModel):
    bertscore: BertScore | None = None
    meteor: Meteor | None = None
    rouge: Rouge | None = None
    bleu: Bleu | None = None
    g_eval_summarization: GEvalSummarizationMetrics | None = None
    token_length: TokenLength | None = None


class EvalJobArtifacts(BaseModel):
    predictions: list[str] | None = None
    ground_truth: list[str] | None = None
    evaluation_time: float | None


class JobOutput(BaseModel):
    metrics: EvalJobMetrics
    parameters: EvalJobConfig
    artifacts: EvalJobArtifacts | None
