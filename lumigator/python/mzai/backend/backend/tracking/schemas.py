from pydantic import BaseModel


class RunOutputs(BaseModel):
    metrics: dict[str, float] | None = None
    parameters: dict[str, str] | None = None
    artifacts: dict[str, str] | None = None
