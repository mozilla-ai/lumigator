from pydantic import BaseModel


class ModelInfo(BaseModel):
    parameter_count: str
    tensor_type: str
    model_size: str


class ModelsResponse(BaseModel):
    name: str
    uri: str
    website_url: str
    description: str
    info: ModelInfo | None = None
    tasks: list[dict[str, dict | None]]
