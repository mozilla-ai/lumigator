from enum import Enum

from pydantic import BaseModel, Field


class ModelRequirement(str, Enum):
    """Represents a type of requirement for a model"""

    API_KEY = "api_key"  # pragma: allowlist secret
    """Indicates that this model requires a configured API key for the related service.

        e.g. OPENAI_API_KEY, or MISTRAL_API_KEY.
        """

    LLAMAFILE = "llamafile"
    """Indicates that this model requires Llamafile to be running."""


class ModelInfo(BaseModel):
    parameter_count: str
    tensor_type: str
    model_size: str


class ModelsResponse(BaseModel):
    name: str
    uri: str
    website_url: str
    description: str
    requirements: list[ModelRequirement] = Field(default_factory=list)
    info: ModelInfo | None = None
    tasks: list[dict[str, dict | None]]
