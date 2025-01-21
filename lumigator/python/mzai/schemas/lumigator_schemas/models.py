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
    requirements: list[str] = Field(default_factory=list)
    info: ModelInfo | None = None
    tasks: list[dict[str, dict | None]]
