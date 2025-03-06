from enum import Enum

from pydantic import BaseModel, Field


class ModelRequirement(str, Enum):
    """Represents a type of requirement for a model"""

    API_KEY = "api_key"  # pragma: allowlist secret
    """Indicates that this model requires a configured API key for the related service.

        e.g. OPENAI_API_KEY, or MISTRAL_API_KEY or DEEPSEEK_API_KEY.
        """

    LLAMAFILE = "llamafile"
    """Indicates that this model requires Llamafile to be running."""


class ModelInfo(BaseModel):
    parameter_count: str
    tensor_type: str
    model_size: str


class ModelsResponse(BaseModel):
    """Contains detailed model information"""

    display_name: str = Field(
        title="Model name", description="Name of the model used in the task. It's just a display name"
    )
    model: str = Field(title="Model ID", description="Model ID used in the task")
    provider: str = Field(
        title="Model Provider",
        description=(
            "LiteLLM key for where the model is hosted (e.g. `openai`, `deepseek`, `gpt3`, etc). "
            "If using a HF model that is hosted in the inference job, use `hf`"
        ),
    )
    base_url: str | None = Field(
        title="Base URL",
        description="Base URL for the model API (if applicable, e.g. for Llamafile, vLLM, etc)",
        default=None,
    )
    website_url: str = Field(
        title="Information page URL",
        description="URI containing detailed information about the model",
    )
    description: str = Field(title="Model description", description="Detailed model description")
    requirements: list[ModelRequirement] = Field(
        default_factory=list,
        title="Model requirements",
        description="Additional requirements that need to be fulfilled before using the model "
        "(e.g. `{ModelRequirement.LLAMAFILE}` to indicate that a llamafile needs to be running "
        "or `{ModelRequirement.API_KEY}` to indicate that an API key is necessary)",
    )
    info: ModelInfo | None = Field(None, title="Model info", description="Detailed model capabilities")
    tasks: list[dict[str, dict | None]] = Field(
        ..., title="Applicable tasks", description="List of tasks to which the model can be applied"
    )
