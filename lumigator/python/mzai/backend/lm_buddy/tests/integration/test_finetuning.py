import pytest

from lm_buddy import LMBuddy
from lm_buddy.configs.huggingface import AutoModelConfig, DatasetConfig, TrainerConfig
from lm_buddy.configs.jobs.finetuning import FinetuningJobConfig, FinetuningRayConfig
from lm_buddy.configs.wandb import WandbRunConfig
from lm_buddy.paths import format_file_path
from lm_buddy.tracking.artifact_utils import ArtifactType


@pytest.fixture
def job_config(llm_model_path, text_dataset_path) -> FinetuningJobConfig:
    model_config = AutoModelConfig(path=format_file_path(llm_model_path))
    dataset_config = DatasetConfig(
        path=format_file_path(text_dataset_path),
        text_field="text",
        split="train",
    )
    trainer_config = TrainerConfig(
        max_seq_length=8,
        num_train_epochs=1,
        save_steps=1,
        save_strategy="epoch",
    )
    tracking_config = WandbRunConfig(project="test-project")
    ray_config = FinetuningRayConfig(num_workers=1, use_gpu=False)
    return FinetuningJobConfig(
        name="test-job",
        model=model_config,
        dataset=dataset_config,
        trainer=trainer_config,
        tracking=tracking_config,
        ray=ray_config,
    )


def test_finetuning_job(job_config):
    # Run test job
    buddy = LMBuddy()
    result = buddy.finetune(job_config)

    # One model artifact should be generated as a result
    artifacts = result.artifacts
    assert len(artifacts) == 1
    assert artifacts[0].type == ArtifactType.MODEL
