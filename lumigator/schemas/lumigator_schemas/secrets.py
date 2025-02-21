<<<<<<< HEAD
from pydantic import BaseModel, Field


class SecretUploadRequest(BaseModel):
    """Represents a secret upload request."""

    value: str = Field(..., max_length=1024, min_length=1)
    description: str


class SecretGetRequest(BaseModel):
    """Represents the result of a get secret request."""

    name: str = Field(..., max_length=255, min_length=1)
    description: str
=======
from pydantic import BaseModel

class Secret(BaseModel):
    secret_name: str | None = None
    secret_value: str | None = None
    description: str = ""
>>>>>>> 3b8469c6 (Rename keys to secrets)
