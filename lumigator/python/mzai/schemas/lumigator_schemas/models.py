from typing import Any

from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    parameter_count: str
    tensor_type: str
    model_size: str


class ModelsResponse(BaseModel):
    name: str
    uri: str
    website_url: str
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    info: ModelInfo | None = None
    tasks: list[dict[str, dict | None]]
