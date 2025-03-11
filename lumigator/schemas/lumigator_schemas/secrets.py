from pydantic import BaseModel, ConfigDict, Field


class SecretUploadRequest(BaseModel):
    """Represents a secret upload request."""

    value: str = Field(..., max_length=1024, min_length=1)
    description: str


class SecretGetRequest(BaseModel):
    """Represents the result of a get secret request.

    NOTE: The secret value should never be exposed to the end user.
    """

    name: str = Field(..., max_length=255, min_length=1)
    description: str

    model_config = ConfigDict(from_attributes=True)
