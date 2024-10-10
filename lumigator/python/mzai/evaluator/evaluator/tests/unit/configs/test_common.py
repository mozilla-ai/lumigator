import pytest
import torch
from evaluator.configs.common import (
    EvaluatorConfig,
    SerializableTorchDtype,
)
from pydantic import ValidationError


def test_config_settings():
    class TestConfig(EvaluatorConfig):
        value: int

    # Validate assignment
    config = TestConfig(value=42)
    with pytest.raises(ValidationError):
        config.value = "dogs"

    # Extra forbid
    with pytest.raises(ValidationError):
        TestConfig(value=42, foo="bar")


def test_config_as_tempfile():
    class TestConfig(EvaluatorConfig):
        name: str

    config = TestConfig(name="test-config")
    config_name = "my-job-config.yaml"
    with config.to_tempfile(name=config_name) as path:
        assert path.name == config_name
        assert TestConfig.from_yaml_file(path) == config


def test_serializable_torch_dtype():
    class TestConfig(EvaluatorConfig):
        torch_dtype: SerializableTorchDtype

    config = TestConfig(torch_dtype="bfloat16")
    assert config.torch_dtype == torch.bfloat16

    # Invalid dtypes
    with pytest.raises(ValueError):
        TestConfig(torch_dtype=5)
    with pytest.raises(ValueError):
        TestConfig(torch_dtype="dogs")
