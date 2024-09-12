import pytest
from peft import PeftType, TaskType

from lm_buddy.configs.huggingface import (
    AdapterConfig,
    AutoModelConfig,
    AutoTokenizerConfig,
    DatasetConfig,
    QuantizationConfig,
)
from lm_buddy.configs.vllm import InferenceServerConfig
from lm_buddy.configs.wandb import WandbRunConfig


@pytest.fixture
def model_config_with_repo_id():
    return AutoModelConfig(path="hf://mistral-ai/mistral-7", trust_remote_code=True)


@pytest.fixture
def model_config_with_artifact():
    artifact_path = "wandb://project/model-artifact:latest"
    return AutoModelConfig(path=artifact_path, trust_remote_code=True, torch_dtype="float16")


@pytest.fixture
def tokenizer_config_with_repo_id():
    return AutoTokenizerConfig(path="mistral-ai/mistral-7", trust_remote_code=True)


@pytest.fixture
def tokenizer_config_with_artifact():
    artifact_path = "wandb://project/tokenizer-artifact:latest"
    return AutoTokenizerConfig(path=artifact_path, trust_remote_code=True)


@pytest.fixture
def dataset_config_with_repo_id():
    return DatasetConfig(path="hf://databricks/dolly15k", text_field="text", split="train")


@pytest.fixture
def dataset_config_with_artifact():
    artifact_path = "wandb://project/dataset-artifact:latest"
    return DatasetConfig(path=artifact_path)


@pytest.fixture
def quantization_config():
    return QuantizationConfig(load_in_8bit=True)


@pytest.fixture
def adapter_config():
    return AdapterConfig(
        peft_type=PeftType.LORA,
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.2,
    )


@pytest.fixture
def wandb_run_config():
    return WandbRunConfig(id="12345", project="research", entity="mzai")


@pytest.fixture
def inference_server_config():
    engine = "wandb://entity/project/model-artifact:latest"
    return InferenceServerConfig(base_url="http://0.0.0.0:8000", engine=engine)
