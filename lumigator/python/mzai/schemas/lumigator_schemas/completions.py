
from pydantic import BaseModel, ConfigDict


class CompletionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: str


class CompletionRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: str
