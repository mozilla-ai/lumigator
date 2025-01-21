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
    requires_api_key: bool = False
    info: ModelInfo | None = None
    tasks: list[dict[str, dict | None]]
