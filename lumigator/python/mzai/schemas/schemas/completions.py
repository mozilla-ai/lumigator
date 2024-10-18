
from pydantic import BaseModel


class CompletionResponse(BaseModel):
    text: str


class CompletionRequest(BaseModel):
    text: str
