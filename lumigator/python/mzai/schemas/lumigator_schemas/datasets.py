import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DatasetFormat(str, Enum):
    JOB = "job"


class DatasetDownloadResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: UUID
    download_urls: list[str]


class DatasetResponse(BaseModel, from_attributes=True):
    model_config = ConfigDict(extra='forbid')
    id: UUID
    filename: str
    format: DatasetFormat
    size: int
    ground_truth: bool
    created_at: datetime.datetime
