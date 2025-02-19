from urllib.parse import urlparse
from uuid import UUID

from lumigator_schemas import JobCreate

from backend.services.exceptions.job_exceptions import JobValidationError

from .schemas import (
    DatasetConfig,
    HuggingFacePipelineConfig,
    InferenceJobConfig,
    InferenceServerConfig,
    JobConfig,
    SamplingParameters,
)

# Served models
OAI_API_URL: str = "https://api.openai.com/v1"
MISTRAL_API_URL: str = "https://api.mistral.ai/v1"
DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1"


def _set_model_type(request: JobCreate) -> str:
    """Sets model URL based on protocol address"""
    if request.job_config.model.startswith("oai://"):
        model_url = OAI_API_URL
    elif request.job_config.model.startswith("mistral://"):
        model_url = MISTRAL_API_URL
    elif request.job_config.model.startswith("ds://"):
        model_url = DEEPSEEK_API_URL
    else:
        model_url = request.job_config.model_url

    return model_url


DEFAULT_SUMMARIZER_PROMPT: str = "You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences."  # noqa: E501


class JobInterfaceInference:
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
        model_parsed = urlparse(request.job_config.model)
        # Maybe use just the protocol to decide?
        if model_parsed.scheme == "oai":
            job_config.inference_server = InferenceServerConfig(
                base_url=_set_model_type(request),
                engine=request.job_config.model,
                # FIXME Inferences may not always be summarizations!
                system_prompt=request.job_config.system_prompt or DEFAULT_SUMMARIZER_PROMPT,
                max_retries=3,
            )
            job_config.params = SamplingParameters(
                max_tokens=request.job_config.max_tokens,
                frequency_penalty=request.job_config.frequency_penalty,
                temperature=request.job_config.temperature,
                top_p=request.job_config.top_p,
            )
        if model_parsed.scheme == "mistral":
            job_config.inference_server = InferenceServerConfig(
                base_url=_set_model_type(request),
                engine=request.job_config.model,
                system_prompt=request.job_config.system_prompt or DEFAULT_SUMMARIZER_PROMPT,
                max_retries=3,
            )
            job_config.params = SamplingParameters(
                max_tokens=request.job_config.max_tokens,
                frequency_penalty=request.job_config.frequency_penalty,
                temperature=request.job_config.temperature,
                top_p=request.job_config.top_p,
            )
        if model_parsed.scheme == "llamafile":
            job_config.inference_server = InferenceServerConfig(
                base_url=_set_model_type(request),
                engine=request.job_config.model,
                system_prompt=request.job_config.system_prompt or DEFAULT_SUMMARIZER_PROMPT,
                max_retries=3,
            )
            job_config.params = SamplingParameters(
                max_tokens=request.job_config.max_tokens,
                frequency_penalty=request.job_config.frequency_penalty,
                temperature=request.job_config.temperature,
                top_p=request.job_config.top_p,
            )
        else:
            # Pending fix for apis
            job_config.hf_pipeline = HuggingFacePipelineConfig(
                model_uri=request.job_config.model,
                task=request.job_config.task,
                accelerator=request.job_config.accelerator,
                revision=request.job_config.revision,
                use_fast=request.job_config.use_fast,
                trust_remote_code=request.job_config.trust_remote_code,
                torch_dtype=request.job_config.torch_dtype,
                max_new_tokens=500,
            )
        return job_config

    def store_as_dataset(self) -> bool:
        return True


# Inference job details
INFERENCE_WORK_DIR = "../jobs/inference"
INFERENCE_PIP_REQS = "requirements.txt"
INFERENCE_COMMAND: str = "python inference.py"

JOB_INTERFACE = JobInterfaceInference(
    command=INFERENCE_COMMAND,
    pip_reqs=INFERENCE_PIP_REQS,
    work_dir=INFERENCE_WORK_DIR,
    config_model=InferenceJobConfig,
)
