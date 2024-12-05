import re
from enum import Enum
from typing import Annotated

from huggingface_hub.utils import HFValidationError, validate_repo_id
from pydantic import AfterValidator


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

    if path.startswith(PathPrefix.HUGGINGFACE):
        if not is_valid_huggingface_repo_id(raw_path):
            raise ValueError(f"'{raw_path}' is not a valid HuggingFace repo ID.")
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


class PathPrefix(str, Enum):
    HUGGINGFACE = "hf://"
    OPENAI = "oai://"
    MISTRAL = "mistral://"
    LLAMAFILE = "llamafile://"
