from enum import Enum
from typing import Annotated

import torch
from huggingface_hub.utils import validate_repo_id
from loguru import logger
from pydantic import AfterValidator, BeforeValidator, ConfigDict, Field, computed_field
from transformers.pipelines import check_task, get_supported_tasks

from schemas import DatasetConfig
from schemas import GenerationConfig as BaseGenerationConfig
from schemas import HfPipelineConfig as BaseHfPipelineConfig
from schemas import InferenceJobConfig as BaseInferenceJobConfig
from schemas import InferenceServerConfig as BaseInferenceServerConfig
from schemas import JobConfig as BaseJobConfig


def _validate_torch_dtype(x: str | torch.dtype) -> str | torch.dtype:
    """Validate the given torch dtype.

    If set to "auto", the dtype will be inferred from the Hugging Face model configuration
    Otherwise, convert the string to a torch.dtype if it is a valid torch dtype

    Args:
        x (str | torch.dtype): The torch dtype to validate.

    Raises:
        ValueError: If the given dtype is not a valid torch dtype.
    """
    match x:
        case torch.dtype():
            return x
        case str() if x == "auto":
            return x
        case str() if hasattr(torch, x) and isinstance(getattr(torch, x), torch.dtype):
            return getattr(torch, x)
        case _:
            raise ValueError(f"{x} is not a valid torch.dtype.")


TorchDtype = Annotated[torch.dtype | str, BeforeValidator(lambda x: _validate_torch_dtype(x))]


def _validate_model_name_or_path(path: str) -> str:
    """Validate the given model RI.

    Resorve the model repo ID and check if it is a valid HuggingFace repo ID.

    Args:
        path (str): The model URI to validate.

    Raises:
        ValueError: If the path is not a valid HuggingFace repo ID.
    """
    if validate_repo_id(path):  # if the path is a valid repo this will return None
        raise ValueError(f"'{path}' is not a valid HuggingFace repo ID.")

    return path


AssetPath = Annotated[str, AfterValidator(lambda x: _validate_model_name_or_path(x))]


def _validate_task(task: str) -> None:
    """Validate the given task.

    There are two types of tasks, simple and parameterized tasks
    For example, "translation" is a simple task but "translation_xx_to_yy" is a parameterized task.
    Normalize the task to the corresponding simple task and compare it with the supported tasks.

    Args:
        task (str): The task to validate.

    Raises:
        ValueError: If the task is not supported.
    """
    supported_tasks = get_supported_tasks()
    normalized_task, _, _ = check_task(task)

    if normalized_task not in supported_tasks:
        raise ValueError(f"Task '{task}' is not supported. Supported tasks are: {supported_tasks}")

    return task


SupportedTask = Annotated[str, AfterValidator(lambda x: _validate_task(x))]


class JobConfig(BaseJobConfig):
    max_samples: int = -1  # set to all samples by default
    storage_path: str
    output_field: str = "predictions"
    enable_tqdm: bool = True
    model_config = ConfigDict(extra="forbid")


class InferenceServerConfig(BaseInferenceServerConfig):
    max_retries: int = 3


class GenerationConfig(BaseGenerationConfig):
    max_new_tokens: int | None = None
    frequency_penalty: float = 0.0
    temperature: float = 1.0
    top_p: float = 1.0
    model_config = ConfigDict(extra="forbid")


class Accelerator(str, Enum):
    AUTO = "auto"
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


class HfPipelineConfig(BaseHfPipelineConfig, arbitrary_types_allowed=True):
    model_name_or_path: AssetPath = Field(title="The Model HF Hub repo ID", exclude=True)
    task: SupportedTask
    revision: str = "main"  # Model version: branch, tag, or commit ID
    use_fast: bool = True  # Whether or not to use a Fast tokenizer if possible
    trust_remote_code: bool = False
    torch_dtype: TorchDtype = "auto"
    accelerator: Accelerator = Field(title="Accelerator", default=Accelerator.AUTO, exclude=True)
    model_config = ConfigDict(extra="forbid")

    @computed_field
    @property
    def device(self) -> torch.device:
        """Returns the device to be used for inference.

        Returns:
            torch.device: The device to be used for inference.
        """
        if self.accelerator == Accelerator.AUTO:
            if torch.cuda.is_available():
                logger.info("CUDA is available. Using CUDA.")
                return torch.device("cuda")

            if torch.backends.mps.is_available():
                logger.info("Metal Performance Shaders (MPS) is available. Using MPS.")
                return torch.device("mps")  # Metal Performance Shaders (macOS)

            logger.info("CUDA is not available. Using CPU.")
            return torch.device("cpu")

        logger.info(f"Using {self.accelerator}.")
        return self.accelerator


# FIXME It seems like _either_ inference_server _or_ hf_pipeline
# is needed; a subclass, generic or similar should be used
# to model this situation
class InferenceJobConfig(BaseInferenceJobConfig):
    name: str
    dataset: DatasetConfig
    job: JobConfig
    system_prompt: str | None = Field(title="System Prompt", default=None, exclude=True)
    inference_server: InferenceServerConfig | None = None
    generation_config: GenerationConfig | None = Field(default_factory=GenerationConfig)
    hf_pipeline: HfPipelineConfig | None = None
    model_config = ConfigDict(extra="forbid")
