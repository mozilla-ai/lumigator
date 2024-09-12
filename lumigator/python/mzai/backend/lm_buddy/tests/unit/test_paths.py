import pytest
from pydantic import TypeAdapter, ValidationError

from lm_buddy.paths import AssetPath, strip_path_prefix


def test_asset_path_validation():
    # Imbues the LoadableAssetPath type with Pydantic validation methods
    validator = TypeAdapter(AssetPath)

    valid_paths = [
        "hf://repo-name",
        "file:///path/to/file",
        "wandb://entity/project/name:version",
    ]
    for path in valid_paths:
        validator.validate_python(path)

    invalid_paths = ["file://not/absolute", "hf://bad..name", "random://scheme", 12345]
    for path in invalid_paths:
        with pytest.raises(ValidationError):
            validator.validate_python(path)


def test_strip_prefix():
    file_path = "file:///path/to/file"
    assert strip_path_prefix(file_path) == "/path/to/file"

    hf_path = "hf://distilgpt2"
    assert strip_path_prefix(hf_path) == "distilgpt2"

    wandb_path = "wandb://entity/project/name:version"
    assert strip_path_prefix(wandb_path) == "entity/project/name:version"
