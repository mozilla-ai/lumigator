import pytest
from evaluator.configs.huggingface import AutoModelConfig
from evaluator.configs.jobs.lm_harness import (
    LMHarnessEvaluationConfig,
    LMHarnessJobConfig,
)
from evaluator.configs.wandb import WandbRunConfig
from evaluator.entrypoint import Evaluator
from evaluator.paths import format_file_path


@pytest.fixture
def job_config(llm_model_path) -> LMHarnessJobConfig:
    model_config = AutoModelConfig(path=format_file_path(llm_model_path))
    tracking_config = WandbRunConfig(project="test-project")
    evaluation_config = LMHarnessEvaluationConfig(tasks=["glue"], limit=5)
    return LMHarnessJobConfig(
        name="test-job",
        model=model_config,
        evaluation=evaluation_config,
        tracking=tracking_config,
    )


def test_lm_harness_job(job_config):
    evaluator = Evaluator()
    result = evaluator.evaluate(job_config)
    assert len(result.tables) == 10
    assert len(result.artifacts) == 1  # One table artifact
