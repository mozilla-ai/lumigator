import pytest

from lumigator.python.mzai.backend.lm_buddy import LMBuddy
from lumigator.python.mzai.backend.lm_buddy.configs.huggingface import AutoModelConfig
from lumigator.python.mzai.backend.lm_buddy.configs.jobs.lm_harness import LMHarnessEvaluationConfig, LMHarnessJobConfig
from lumigator.python.mzai.backend.lm_buddy.configs.wandb import WandbRunConfig
from lumigator.python.mzai.backend.lm_buddy.paths import format_file_path


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
    buddy = LMBuddy()
    result = buddy.evaluate(job_config)
    assert len(result.tables) == 10
    assert len(result.artifacts) == 1  # One table artifact
