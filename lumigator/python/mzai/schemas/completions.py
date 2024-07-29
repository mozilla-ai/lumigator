import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class CompletionResponse(BaseModel):
    completion_response: str


class CompletionRequest(BaseModel):
    text: str
