import pytest
from pydantic import ValidationError

from evaluator.configs.huggingface import DatasetConfig
from evaluator.paths import format_huggingface_path


def test_split_is_required():
    with pytest.raises(ValidationError):
        dataset_path = format_huggingface_path("imdb")
        DatasetConfig(path=dataset_path, split=None)
