import pytest
from pydantic import ValidationError

from lm_buddy.configs.jobs.lm_harness import (
    LMHarnessEvaluationConfig,
    LMHarnessJobConfig,
    LocalChatCompletionsConfig,
)
from lm_buddy.configs.vllm import InferenceServerConfig
from tests.test_utils import copy_pydantic_json


@pytest.fixture
def local_completions_config(inference_server_config):
    return LocalChatCompletionsConfig(
        inference=inference_server_config,
        tokenizer_backend="huggingface",
        max_tokens=256,
        truncate=True,
    )


@pytest.fixture
def lm_harness_evaluation_config():
    return LMHarnessEvaluationConfig(
        tasks=["task1", "task2", "task3"],
        num_fewshot=5,
    )


@pytest.fixture
def lm_harness_job_config(
    request,
    model_config_with_artifact,
    local_completions_config,
    quantization_config,
    wandb_run_config,
    lm_harness_evaluation_config,
):
    if request.param == "model_config_with_artifact":
        return LMHarnessJobConfig(
            name="lm-harness-job-config",
            model=model_config_with_artifact,
            evaluation=lm_harness_evaluation_config,
            tracking=wandb_run_config,
            quantization=quantization_config,
        )
    elif request.param == "local_completions_config":
        return LMHarnessJobConfig(
            name="lm-harness-job-config",
            model=local_completions_config,
            evaluation=lm_harness_evaluation_config,
            tracking=wandb_run_config,
            quantization=quantization_config,
        )


@pytest.mark.parametrize(
    "lm_harness_job_config",
    ["model_config_with_artifact", "local_completions_config"],
    indirect=True,
)
def test_serde_round_trip(lm_harness_job_config):
    assert copy_pydantic_json(lm_harness_job_config) == lm_harness_job_config


@pytest.mark.parametrize(
    "lm_harness_job_config",
    ["model_config_with_artifact", "local_completions_config"],
    indirect=True,
)
def test_parse_yaml_file(lm_harness_job_config):
    with lm_harness_job_config.to_tempfile() as config_path:
        assert lm_harness_job_config == LMHarnessJobConfig.from_yaml_file(config_path)


@pytest.mark.parametrize(
    "file_suffix", ["lm_harness_hf_config.yaml", "lm_harness_inference_server_config.yaml"]
)
def test_load_example_config(examples_dir, file_suffix):
    """Load the example configs to make sure they stay up to date."""
    config_file = examples_dir / "configs" / "evaluation" / file_suffix
    config = LMHarnessJobConfig.from_yaml_file(config_file)
    assert copy_pydantic_json(config) == config


def test_inference_engine_provided():
    with pytest.raises(ValidationError):
        LocalChatCompletionsConfig(
            inference=InferenceServerConfig(base_url="url", engine=None),
            tokenizer_backend="huggingface",
            max_tokens=256,
        )
