from pydantic import BaseModel


def copy_pydantic_json(model: BaseModel) -> BaseModel:
    """Copy a Pydantic model through round-trip JSON serialization."""
    return model.__class__.model_validate_json(model.model_dump_json())
