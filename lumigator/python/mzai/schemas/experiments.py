import datetime
from uuid import UUID

from pydantic import BaseModel

from mzai.schemas.jobs import JobStatus


class ExperimentCreate(BaseModel):
    name: str
    description: str = ""
    model: str
    dataset: UUID
    max_samples: int | None = None
    model_url: str | None = None
    system_prompt: str | None = None
    config_template: str | None = None

class ExperimentResult(BaseModel):
    download_url: str

# The experiment data is retrieved like .../experiments/{experiment_id}
# The experiment result is retrieved like .../experiments/{experiment_id}/result
class ExperimentResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: JobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
    result: ExperimentResult | None

