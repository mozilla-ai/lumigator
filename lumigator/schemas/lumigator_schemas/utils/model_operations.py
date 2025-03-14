from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def merge_models(base_model: T | None, overlay_model: T | None, deep_merge: bool | None = False) -> tuple[T, set[str]]:
    """Merge two Pydantic model instances with overlay_model taking precedence.

    :param base_model: Base model to merge into
    :param overlay_model: Model with values that will override base_model
    :param deep_merge: Whether to recursively merge nested dictionaries (True)
                      or just overwrite top-level keys (False)
    :returns: Tuple containing (merged model of the same type, set of overwritten keys)
    """
    # Handle None cases
    if base_model is None:
        model_class = type(overlay_model) if overlay_model is not None else None
        if model_class is None:
            raise ValueError("Both models cannot be None")
        return overlay_model.model_copy() if overlay_model is not None else model_class(), set()

    if overlay_model is None:
        return base_model.model_copy(), set()

    # Convert both to dictionaries
    base_dict = base_model.model_dump()
    overlay_dict = overlay_model.model_dump()

    # Merge dictionaries recursively or at top level
    merged_dict, overwritten_keys = deep_merge_dicts(base_dict, overlay_dict, deep_merge)

    # Create a new instance of the same type as the input models
    model_class = type(base_model)
    return model_class.model_validate(merged_dict), overwritten_keys


def deep_merge_dicts(
    base_dict: dict[str, Any], overlay_dict: dict[str, Any], deep_merge: bool | None = False
) -> tuple[dict[str, Any], set[str]]:
    """Recursively merge dictionaries with overlay_dict taking precedence.

    :param base_dict: Base dictionary
    :param overlay_dict: Dictionary with values that will override base_dict
    :param deep_merge: Whether to recursively merge nested dictionaries (True)
                      or just overwrite top-level keys (False)
    :returns: Tuple of (merged dictionary, set of overwritten key names)
    """
    result = base_dict.copy()
    overwritten_keys = set()

    for key, value in overlay_dict.items():
        if deep_merge and key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            nested_result, nested_overwritten = deep_merge_dicts(result[key], value, deep_merge)
            result[key] = nested_result
            # Add nested keys with their path
            overwritten_keys.update({f"{key}.{nested_key}" for nested_key in nested_overwritten})
        else:
            if key in result and result[key] != value:
                overwritten_keys.add(key)
            result[key] = value

    return result, overwritten_keys
