import re
from enum import Enum
from pathlib import Path
from typing import Annotated

import wandb
from huggingface_hub.utils import HFValidationError, validate_repo_id
from pydantic import AfterValidator
from wandb.sdk.artifacts.exceptions import ArtifactNotLoggedError


class PathPrefix(str, Enum):
    FILE = "file://"
    HUGGINGFACE = "hf://"
    WANDB = "wandb://"
    S3 = "s3://"
    OPENAI = "oai://"
    MISTRAL = "mistral://"
    LLAMAFILE = "llamafile://"


def strip_path_prefix(path: str) -> str:
    """Strip the 'scheme://' prefix from the start of a string."""
    pattern = r"^\w+\:\/\/"
    return re.sub(pattern, "", path)


def is_valid_huggingface_repo_id(s: str) -> bool:
    """Simple test to check if an HF model is valid using HuggingFace's tools."""
    try:
        validate_repo_id(s)
        return True
    except HFValidationError:
        return False


def is_valid_wandb_path(wandb_path: str) -> bool:
    """Basic validation for W&B path format."""
    return bool(wandb_path)


def is_valid_s3_path(s3_path: str) -> bool:
    """Basic validation for S3 paths."""
    return bool(re.match(r"s3://[\w\-.]+/.*", s3_path))


def is_valid_openai_model_name(model_name: str) -> bool:
    """Basic validation for OpenAI model names."""
    return bool(model_name)


def is_valid_mistral_model_name(model_name: str) -> bool:
    """Basic validation for Mistral model names."""
    return bool(model_name)


def is_valid_llamafile_model_name(model_name: str) -> bool:
    """Basic validation for Llamafile model names."""
    return bool(model_name)


def validate_asset_path(path: str) -> "AssetPath":
    raw_path = strip_path_prefix(path)

    if path.startswith(PathPrefix.FILE):
        if not Path(raw_path).is_absolute():
            raise ValueError(f"'{raw_path}' is not an absolute file path.")
    elif path.startswith(PathPrefix.HUGGINGFACE):
        if not is_valid_huggingface_repo_id(raw_path):
            raise ValueError(f"'{raw_path}' is not a valid HuggingFace repo ID.")
    elif path.startswith(PathPrefix.WANDB):
        if not is_valid_wandb_path(raw_path):
            raise ValueError(f"'{raw_path}' is not a validpath.")
    elif path.startswith(PathPrefix.S3):
        if not is_valid_s3_path(path):
            raise ValueError(f"'{raw_path}' is not a valid S3 path.")
    elif path.startswith(PathPrefix.OPENAI):
        if not is_valid_openai_model_name(raw_path):
            raise ValueError(f"'{raw_path}' is not a valid OpenAI model name.")
    elif path.startswith(PathPrefix.MISTRAL):
        if not is_valid_mistral_model_name(raw_path):
            raise ValueError(f"'{raw_path}' is not a valid Mistral model name.")
    elif path.startswith(PathPrefix.LLAMAFILE):
        if not is_valid_llamafile_model_name(raw_path):
            raise ValueError(f"'{raw_path}' is not a valid Llamafile model name.")
    else:
        allowed_prefixes = {x.value for x in PathPrefix}
        raise ValueError(f"'{path}' does not begin with an allowed prefix: {allowed_prefixes}")
    return path


AssetPath = Annotated[str, AfterValidator(lambda x: validate_asset_path(x))]


def format_file_path(path: str | Path) -> AssetPath:
    path = Path(path).absolute()
    return f"{PathPrefix.FILE.value}{path}"


def format_huggingface_path(repo_id: str) -> AssetPath:
    return f"{PathPrefix.HUGGINGFACE.value}{repo_id}"


def format_artifact_path(artifact: wandb.Artifact) -> AssetPath:
    try:
        return f"{PathPrefix.WANDB.value}{artifact.qualified_name}"
    except ArtifactNotLoggedError as e:
        msg = (
            "Unable to construct an `AssetPath` from artifact missing project/entity fields. "
            "Make sure to log the artifact before calling this method."
        )
        raise ValueError(msg) from e


def format_s3_path(bucket: str, key: str) -> AssetPath:
    return f"{PathPrefix.S3.value}{bucket}/{key}"


def format_openai_model_uri(model_name: str) -> AssetPath:
    return f"{PathPrefix.OPENAI.value}{model_name}"


def format_mistral_model_uri(model_name: str) -> AssetPath:
    return f"{PathPrefix.MISTRAL.value}{model_name}"


def format_llamafile_model_uri(model_name: str) -> AssetPath:
    return f"{PathPrefix.LLAMAFILE.value}{model_name}"
