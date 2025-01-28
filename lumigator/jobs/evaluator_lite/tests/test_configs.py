import copy

import pytest
from pydantic import ValidationError

from schemas import DatasetConfig, EvalJobConfig, EvaluationConfig, ModelConfig


def test_valid_config():
    """Tests a valid EvalJobConfig"""
    config = EvalJobConfig(
        name="my_eval_job",
        dataset=DatasetConfig(path="/path/to/dataset"),
        model=ModelConfig(path="/path/to/model"),
        evaluation=EvaluationConfig(storage_path="/path/to/results"),
    )
    assert config


def test_invalid_config_missing_required_fields():
    """Tests that required fields are present"""
    with pytest.raises(ValueError):
        EvalJobConfig(
            name="my_eval_job",
            dataset=DatasetConfig(),  # Missing 'path'
            model=ModelConfig(path="/path/to/model"),
            evaluation=EvaluationConfig(),
        )


def test_valid_config_with_custom_metrics():
    """Tests a valid config with custom metrics"""
    config = EvalJobConfig(
        name="my_eval_job",
        dataset=DatasetConfig(path="/path/to/dataset"),
        model=ModelConfig(path="/path/to/model"),
        evaluation=EvaluationConfig(metrics=["bleu", "lumi"], storage_path="/path/to/results"),
    )
    assert config
