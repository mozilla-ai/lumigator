from uuid import UUID

from inference.schemas import (
    DatasetConfig,
    HuggingFacePipelineConfig,
    InferenceJobConfig,
    InferenceServerConfig,
    JobConfig,
    SamplingParameters,
)
from lumigator_schemas.jobs import JobCreate, JobType

from backend.services.exceptions.job_exceptions import JobValidationError
from backend.services.job_interface import JobDefinition

# Served models
OAI_API_URL: str = "https://api.openai.com/v1"
MISTRAL_API_URL: str = "https://api.mistral.ai/v1"
DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1"

DEFAULT_SUMMARIZER_PROMPT: str = "You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences."  # noqa: E501


class JobInterfaceInference(JobDefinition):
    def generate_config(self, request: JobCreate, record_id: UUID, dataset_path: str, storage_path: str):
        # TODO Move to a custom validator in the schema
        if request.job_config.task == "text-generation" and not request.job_config.system_prompt:
            raise JobValidationError("System prompt is required for text generation tasks.") from None
        job_config = InferenceJobConfig(
            name=f"{request.name}/{record_id}",
            dataset=DatasetConfig(path=dataset_path),
            job=JobConfig(
                max_samples=request.max_samples,
                storage_path=storage_path,
                # TODO Should be unnecessary, check
                output_field=request.job_config.output_field or "predictions",
            ),
        )
        if request.job_config.provider == "hf":
            # Custom logic: if provider is hf, we run the hf model inside the ray job
            job_config.hf_pipeline = HuggingFacePipelineConfig(
                model_name_or_path=request.job_config.model,
                task=request.job_config.task,
                accelerator=request.job_config.accelerator,
                revision=request.job_config.revision,
                use_fast=request.job_config.use_fast,
                trust_remote_code=request.job_config.trust_remote_code,
                torch_dtype=request.job_config.torch_dtype,
                max_new_tokens=500,
            )
        else:
            # It will be a pass through to LiteLLM
            job_config.inference_server = InferenceServerConfig(
                base_url=request.job_config.base_url if request.job_config.base_url else None,
                model=request.job_config.model,
                provider=request.job_config.provider,
                system_prompt=request.job_config.system_prompt or DEFAULT_SUMMARIZER_PROMPT,
                max_retries=3,
            )
        job_config.params = SamplingParameters(
            max_tokens=request.job_config.max_tokens,
            frequency_penalty=request.job_config.frequency_penalty,
            temperature=request.job_config.temperature,
            top_p=request.job_config.top_p,
        )
        return job_config

    def store_as_dataset(self) -> bool:
        return True


# Inference job details
# FIXME tweak paths in the backend
INFERENCE_WORK_DIR = "../jobs/inference"
INFERENCE_PIP_REQS = "../jobs/inference/requirements_cpu.txt"
INFERENCE_COMMAND: str = "python inference.py"

JOB_DEFINITION: JobDefinition = JobInterfaceInference(
    command=INFERENCE_COMMAND,
    pip_reqs=INFERENCE_PIP_REQS,
    work_dir=INFERENCE_WORK_DIR,
    config_model=InferenceJobConfig,
    type=JobType.INFERENCE,
)
