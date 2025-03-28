"""Schema file that is loaded by the backend to validate the input/output data.
This file must only depend on pydantic and not on any other external library.
This is because the backend and this job will be running in different environments.
"""

from lumigator_schemas.tasks import SummarizationTaskDefinition, TaskDefinition, TaskType
from pydantic import BaseModel, ConfigDict, Field, PositiveInt, model_validator


class DatasetConfig(BaseModel):
    path: str
    model_config = ConfigDict(extra="forbid")


class JobConfig(BaseModel):
    max_samples: int
    batch_size: PositiveInt = 1
    storage_path: str
    output_field: str | None = "predictions"
    enable_tqdm: bool = True
    model_config = ConfigDict(extra="forbid")


class InferenceServerConfig(BaseModel):
    base_url: str | None = None
    model: str
    provider: str
    max_retries: int
    model_config = ConfigDict(extra="forbid")


class GenerationConfig(BaseModel):
    """Custom and limited configuration for generation.
    Sort of a subset of HF GenerationConfig
    https://huggingface.co/docs/transformers/en/main_classes/text_generation#transformers.GenerationConfig
    """

    max_new_tokens: int
    frequency_penalty: float
    temperature: float
    top_p: float
    model_config = ConfigDict(extra="forbid")


class HuggingFacePipelineConfig(BaseModel, arbitrary_types_allowed=True):
    model_name_or_path: str
    task: TaskType
    revision: str
    use_fast: bool
    trust_remote_code: bool
    torch_dtype: str
    accelerator: str
    model_config = ConfigDict(extra="forbid")
    truncation: bool = True


class InferenceJobConfig(BaseModel):
    name: str
    dataset: DatasetConfig
    job: JobConfig
    system_prompt: str | None = None
    inference_server: InferenceServerConfig | None = None
    generation_config: GenerationConfig | None = None
    hf_pipeline: HuggingFacePipelineConfig | None = None
    task_definition: TaskDefinition = Field(default_factory=lambda: SummarizationTaskDefinition())
    model_config = ConfigDict(extra="forbid")


class InferenceMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt_tokens: int
    total_tokens: int
    completion_tokens: int
    reasoning_tokens: int
    answer_tokens: int


class AverageInferenceMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")
    avg_prompt_tokens: float
    avg_total_tokens: float
    avg_completion_tokens: float
    avg_reasoning_tokens: float | None = None
    avg_answer_tokens: float = None


class InferenceJobOutput(BaseModel):
    predictions: list | None = None
    reasoning: list | None = None
    examples: list
    ground_truth: list | None = None
    model: str
    inference_time: float
    inference_metrics: list[InferenceMetrics | None] = []


class PredictionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prediction: str
    reasoning: str | None = None
    metrics: InferenceMetrics | None = None


class JobOutput(BaseModel):
    metrics: AverageInferenceMetrics | dict = {}
    artifacts: InferenceJobOutput
    parameters: InferenceJobConfig

    @model_validator(mode="before")
    @classmethod
    def ensure_metrics_default(cls, values):
        # If metrics is set to None, set it to an empty dict.
        if values.get("metrics") is None:
            values["metrics"] = {}
        return values
