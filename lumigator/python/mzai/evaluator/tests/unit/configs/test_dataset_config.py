import pytest
from evaluator.configs.huggingface import DatasetConfig
from evaluator.paths import format_huggingface_path
from pydantic import ValidationError


def test_split_is_required():
    with pytest.raises(ValidationError):
        dataset_path = format_huggingface_path("imdb")
        DatasetConfig(path=dataset_path, split=None)
