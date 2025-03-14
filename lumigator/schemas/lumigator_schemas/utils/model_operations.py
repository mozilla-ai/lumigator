from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def merge_models(
    base_model: T | None, overlay_model: T | None, deep_merge: bool | None = True
) -> tuple[T, set[str], set[str]]:
    """Merge two Pydantic model instances with overlay_model taking precedence when it has a value.

    :param base_model: Base model to merge into
    :param overlay_model: Model with values that will override base_model
    :param deep_merge: Whether to recursively merge nested dictionaries (True)
                or just overwrite top-level keys (False). Defaults to True if not supplied.
    :returns: Tuple containing (merged model of the same type, set of overwritten keys, set of skipped keys)
    """
    if base_model is None:
        model_class = type(overlay_model) if overlay_model is not None else None
        if model_class is None:
            raise ValueError("Both models cannot be None")
        return overlay_model.model_copy() if overlay_model is not None else model_class(), set(), set()

    if overlay_model is None:
        return base_model.model_copy(), set(), set()

    # Convert both to dictionaries
    base_dict = base_model.model_dump()
    overlay_dict = overlay_model.model_dump()

    # Merge dictionaries recursively or at top level
    merged_dict, overwritten_keys, skipped_keys = deep_merge_dicts(base_dict, overlay_dict, deep_merge)

    # Create a new instance of the same type as the input models
    model_class = type(base_model)
    return model_class.model_validate(merged_dict), overwritten_keys, skipped_keys


def deep_merge_dicts(
    base_dict: dict[str, Any], overlay_dict: dict[str, Any], deep_merge: bool | None = True
) -> tuple[dict[str, Any], set[str], set[str]]:
    """Recursively merge dictionaries with overlay_dict taking precedence when it has a value.

    :param base_dict: Base dictionary
    :param overlay_dict: Dictionary with values that will override base_dict
    :param deep_merge: Whether to recursively merge nested dictionaries (True)
                or just overwrite top-level keys (False). Defaults to True if not supplied.
    :returns: Tuple of (merged dictionary, set of overwritten key names, set of skipped key names)
    """
    result = base_dict.copy()
    overwritten_keys = set()
    skipped_keys = set()

    # Add skipped keys from base_dict that aren't in overlay_dict
    skipped_keys.update(base_dict.keys() - overlay_dict.keys())

    for key, value in overlay_dict.items():
        if deep_merge and key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            nested_result, nested_overwritten, nested_skipped = deep_merge_dicts(result[key], value, deep_merge)
            result[key] = nested_result
            # Add nested keys with their path
            overwritten_keys.update({f"{key}.{nested_key}" for nested_key in nested_overwritten})
            skipped_keys.update({f"{key}.{nested_key}" for nested_key in nested_skipped})
        elif key in result:
            if result[key] != value:
                # If the value is different, overwrite it
                overwritten_keys.add(key)
                result[key] = value
            else:
                # If the value is the same, mark it as skipped
                skipped_keys.add(key)
        else:
            # If the key is not in the base_dict, just add it
            result[key] = value

    return result, overwritten_keys, skipped_keys
