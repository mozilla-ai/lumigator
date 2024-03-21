from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str = Field(..., example="Ok")
