from enum import Enum

import torch
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, computed_field
from utils import resolve_model_repo


class Accelerator(str, Enum):
    AUTO = "auto"
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


class DatasetConfig(BaseModel):
    path: str
    model_config = ConfigDict(extra="forbid")


class JobConfig(BaseModel):
    max_samples: int = -1  # set to all samples by default
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


class HfPipelineConfig(BaseModel, arbitrary_types_allowed=True):
    model_path: str = Field(title="The Model HF Hub repo ID", exclude=True)
    task: str
    revision: str = "main"  # Model version: branch, tag, or commit ID
    use_fast: bool = True  # Whether or not to use a Fast tokenizer if possible
    trust_remote_code: bool = False
    torch_dtype: str = "auto"
    accelerator: str = Field(title="Accelerator", default=Accelerator.AUTO, exclude=True)
    model_config = ConfigDict(extra="forbid")

    @computed_field
    @property
    def model(self) -> str:
        """Returns the model name.

        Returns:
            str: The model name.
        """
        return resolve_model_repo(self.model_path)

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


class InferenceJobConfig(BaseModel):
    name: str
    dataset: DatasetConfig
    job: JobConfig
    inference_server: InferenceServerConfig | None = None
    params: SamplingParameters | None = None
    hf_pipeline: HfPipelineConfig | None = None
    model_config = ConfigDict(extra="forbid")
