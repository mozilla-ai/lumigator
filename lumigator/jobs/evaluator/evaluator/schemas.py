from pydantic import BaseModel, ConfigDict


class JobResultObject(BaseModel):
    model_config = ConfigDict(extra="forbid")
    metrics: dict | None
    parameters: dict | None
    artifacts: dict | None
