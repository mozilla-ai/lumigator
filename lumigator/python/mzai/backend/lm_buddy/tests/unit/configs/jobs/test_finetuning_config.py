import pytest
from pydantic import ValidationError

from lm_buddy.configs.huggingface import DatasetConfig
from lm_buddy.configs.jobs.finetuning import FinetuningJobConfig, FinetuningRayConfig
from tests.test_utils import copy_pydantic_json


@pytest.fixture
def finetuning_ray_config():
    return FinetuningRayConfig(
        num_workers=4,
        use_gpu=True,
    )


@pytest.fixture
def finetuning_job_config(
    model_config_with_artifact,
    dataset_config_with_artifact,
    tokenizer_config_with_artifact,
    quantization_config,
    adapter_config,
    wandb_run_config,
    finetuning_ray_config,
):
    return FinetuningJobConfig(
        name="finetuning-job-config",
        model=model_config_with_artifact,
        dataset=dataset_config_with_artifact,
        tokenizer=tokenizer_config_with_artifact,
        quantization=quantization_config,
        adapter=adapter_config,
        tracking=wandb_run_config,
        ray=finetuning_ray_config,
    )


def test_serde_round_trip(finetuning_job_config):
    assert copy_pydantic_json(finetuning_job_config) == finetuning_job_config


def test_parse_yaml_file(finetuning_job_config):
    with finetuning_job_config.to_tempfile() as config_path:
        assert finetuning_job_config == FinetuningJobConfig.from_yaml_file(config_path)


def test_load_example_config(examples_dir):
    """Load the example configs to make sure they stay up to date."""
    config_file = examples_dir / "configs" / "finetuning" / "finetuning_config.yaml"
    config = FinetuningJobConfig.from_yaml_file(config_file)
    assert copy_pydantic_json(config) == config


def test_argument_validation():
    model_path = "hf://model-repo-id"
    tokenizer_path = "hf://tokenizer-repo-id"
    dataset_config = DatasetConfig(path="hf://dataset-repo-id", split="train")

    # Strings should be upcast to configs as the path argument
    allowed_config = FinetuningJobConfig(
        name="test",
        model=model_path,
        tokenizer=tokenizer_path,
        dataset=dataset_config,
    )
    assert allowed_config.model.path == model_path
    assert allowed_config.tokenizer.path == tokenizer_path

    # Check passing invalid arguments is validated for each asset type
    with pytest.raises(ValidationError):
        FinetuningJobConfig(name="test", model=12345, dataset=dataset_config)
    with pytest.raises(ValidationError):
        FinetuningJobConfig(name="test", model=model_path, tokenizer=12345, dataset=dataset_config)
    with pytest.raises(ValidationError):
        FinetuningJobConfig(name="test", model=model_path, tokenizer=tokenizer_path, dataset=12345)

    # Check that tokenizer is set to model path when absent
    missing_tokenizer_config = FinetuningJobConfig(
        name="test", model=model_path, dataset=dataset_config
    )
    assert missing_tokenizer_config.tokenizer.path == model_path
