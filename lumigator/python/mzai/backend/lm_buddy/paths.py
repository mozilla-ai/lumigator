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


def strip_path_prefix(path: str) -> str:
    """Strip the 'scheme://' prefix from the start of a string."""
    pattern = "^\w+\:\/\/"
    return re.sub(pattern, "", path)


def is_valid_huggingface_repo_id(s: str):
    """
    Simple test to check if an HF model is valid using HuggingFace's tools.
    Sadly, theirs throws an exception and has no return.

    Args:
        s: string to test.
    """
    try:
        validate_repo_id(s)
        return True
    except HFValidationError:
        return False


def validate_asset_path(path: str) -> "AssetPath":
    raw_path = strip_path_prefix(path)
    if path.startswith(PathPrefix.FILE):
        if not Path(raw_path).is_absolute():
            raise ValueError(f"'{raw_path}' is not an absolute file path.")
    elif path.startswith(PathPrefix.HUGGINGFACE):
        if not is_valid_huggingface_repo_id(raw_path):
            raise ValueError(f"'{raw_path}' is not a valid HuggingFace repo ID.")
    elif path.startswith(PathPrefix.WANDB):
        # TODO: Validate the W&B path structure?
        pass
    elif path.startswith(PathPrefix.S3):
        # TODO: Validate the S3 path structure?
        # e.g. if the assumption is we always want a file or a dir, we could
        # use https://s3pathlib.readthedocs.io to verify (.is_file() or ._is_dir())
        pass
    elif path.startswith(PathPrefix.OPENAI):
        # TODO: Validate the OAI model name?
        pass
    elif path.startswith(PathPrefix.MISTRAL):
        # TODO: Validate the mistral model name?
        pass
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
