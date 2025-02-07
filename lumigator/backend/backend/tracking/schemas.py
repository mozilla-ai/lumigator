from pydantic import BaseModel


class RunOutputs(BaseModel):
    metrics: dict[str, float] | None = {}
    parameters: dict[str, str] | None = {}
    artifacts: dict[str, str] | None = {}
    ray_job_id: str | None = None  # we need this in order to retrieve the ray logs currently
