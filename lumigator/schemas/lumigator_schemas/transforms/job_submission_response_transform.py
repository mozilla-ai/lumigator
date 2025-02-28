import json
import re
import uuid
from itertools import dropwhile
from json import JSONDecodeError
from shlex import split
from typing import Any


def transform_job_submission_response(input_data: dict) -> dict:
    entrypoint = input_data.get("entrypoint", None)

    if not isinstance(entrypoint, str):
        return input_data

    parsed_entrypoint = _parse_entrypoint(entrypoint)
    if parsed_entrypoint:
        input_data["config"] = parsed_entrypoint

    return input_data


def _parse_entrypoint(entrypoint: str) -> dict[str, Any] | None:
    """Parses the entrypoint string and extracts the configuration as a JSON object.

    This method processes the entrypoint string, extracting the associated JSON
    object (from Ray) using a specified flag.

    It further processes the extracted JSON to populate it with additional dataset information,
    sample limits, and model name or path, as required for further processing.

    :param entrypoint: The entrypoint string that contains the configuration.
        This string is parsed to extract the configuration in JSON format.
    :returns (dict[str, Any] | None): A dictionary representing the parsed configuration
        if successful, or None if no valid configuration could be extracted.
    """
    # Extract JSON for the specified flag.
    json_object = _extract_json_token(split(entrypoint), "--config")
    if not json_object:
        return None

    json_object["dataset"] = _extract_dataset(json_object)
    json_object["max_samples"] = _extract_max_samples(json_object)
    json_object["model_name_or_path"] = _extract_model_name_or_path(json_object)

    return json_object


def _extract_json_token(tokens: list[str], flag: str) -> dict[str, Any] | None:
    """Extracts the token from the list following on from the specified flag and parses it as JSON.

    This method iterates through a list of tokens, finds the token that matches the given
    flag, and then extracts the next token as a JSON string. It attempts to parse the string
    as JSON and returns the resulting object. If no valid JSON token is found, or if the JSON
    parsing fails, it returns None.

    :param tokens: A list of tokens, where one of the tokens is expected to
        be a flag followed by a JSON-formatted string.
    :param flag: The flag used to identify the position of the desired JSON token in
        the token list.
    :returns (dict[str, Any] | None): A parsed JSON object if the JSON token is found and
        successfully parsed, or None if the token is not found or if parsing fails.
    """
    # Drop tokens until we reach the flag
    token_iter = dropwhile(lambda t: t != flag, tokens)
    next(token_iter, None)  # Consume the flag itself
    config_json = next(token_iter, None)  # Get the actual config JSON

    if not config_json:
        return None

    # Remove potential wrapping single quotes.
    config_json = config_json.strip().lstrip("'").rstrip("'")

    try:
        return json.loads(config_json)
    except JSONDecodeError:
        return None


def _extract_dataset(config_dict: dict[str, Any]) -> dict[str, Any]:
    """Extracts the dataset ID and (file) name from the specified config dictionary.

    Retrieves the `dataset` path from the given config dictionary and attempts
    to extract the dataset ID (in UUID format) and the file name from the path. If the dataset
    path is missing or the UUID extraction fails, it raises a `ValueError`.

    :param config_dict: A dictionary containing the configuration data,
       which must include a "dataset" field with a "path" key.
    :returns (dict[str, Any]): A dictionary containing the extracted "id" (UUID) and
       "name" (file name) of the dataset.
    :raises ValueError: If the dataset path cannot be found or if the extracted dataset
       ID is not a valid UUID.
    """
    dataset_path = config_dict.get("dataset", {}).get("path", "")
    if not dataset_path:
        raise ValueError(f"Unable to parse dataset path from entrypoint config: {config_dict}")

    match = re.search(
        r".*/datasets/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/([^/]+)$", dataset_path, re.I
    )

    if not match:
        raise ValueError(f"Could not extract dataset ID and file name from path: {dataset_path}")

    dataset_id = match.group(1)
    file_name = match.group(2)

    try:
        dataset_uuid = uuid.UUID(dataset_id)
    except ValueError as e:
        raise ValueError(f"Extracted dataset ID '{dataset_id}' is not a valid UUID") from e

    return {"id": dataset_uuid, "name": file_name}


def _extract_model_name_or_path(config_dict: dict[str, Any]) -> str | None:
    """Extract and normalize the model path or name from the given configuration dictionary.

    Retrieves the model name (or path) from various locations in the provided configuration.
    If no model path or name is found, it returns `None`.

    :param config_dict (dict[str, Any]): A dictionary containing the configuration data,
        which may include model information under different sections like `model`, `hf_pipeline`,
        or `inference_server`.
    :returns  (str | None): The model name or path if found, otherwise `None`.
    """
    # NOTE: Some jobs don't have models (e.g. evaluation).
    model_name_or_path = (
        config_dict.get("model", {}).get("path")
        or config_dict.get("model", {}).get("inference", {}).get("model")
        or config_dict.get("hf_pipeline", {}).get("model_name_or_path")
        or config_dict.get("inference_server", {}).get("model")
    )

    return model_name_or_path


def _extract_max_samples(config_dict: dict[str, Any]) -> int:
    """Extract the `max_samples` value from the configuration dictionary in the `job` and `evaluation` entries.

    :param config_dict (dict[str, Any]): The configuration dictionary to extract `max_samples` from.
    :returns  (int): The value of `max_samples` if found.
    :raises ValueError: If `max_samples` is not found in the `job` or `evaluation` sections.
    """
    for key in ("job", "evaluation"):
        if (max_samples := config_dict.get(key, {}).get("max_samples")) is not None:
            return max_samples
    raise ValueError(f"Unable to parse max_samples from entrypoint config: {config_dict}")
