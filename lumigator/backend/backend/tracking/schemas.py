from pydantic import BaseModel


class RunOutputs(BaseModel):
    metrics: dict[str, float] | None = {}
    parameters: dict[str, str] | None = {}
    artifacts: dict[str, str] | None = {}
