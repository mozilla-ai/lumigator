import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class DatasetFormat(str, Enum):
    EXPERIMENT = "experiment"


class DatasetDownloadResponse(BaseModel):
    id: UUID
    download_url: str


class DatasetResponse(BaseModel, from_attributes=True):
    id: UUID
    filename: str
    format: DatasetFormat
    size: int
    created_at: datetime.datetime
