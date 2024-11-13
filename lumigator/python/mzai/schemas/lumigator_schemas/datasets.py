import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class DatasetFormat(str, Enum):
    JOB = "job"


class DatasetDownloadResponse(BaseModel):
    id: UUID
    download_urls: list[str]


class DatasetResponse(BaseModel, from_attributes=True):
    id: UUID
    filename: str
    format: DatasetFormat
    size: int
    ground_truth: bool
    created_at: datetime.datetime
