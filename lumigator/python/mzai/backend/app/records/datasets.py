from enum import Enum

from sqlalchemy.orm import Mapped

from app.records.base import BaseRecord
from app.records.mixins import CreatedAtMixin

# from mzai.schemas.datasets import DatasetFormat


class DatasetFormat(str, Enum):
    EXPERIMENT = "experiment"


class DatasetRecord(BaseRecord, CreatedAtMixin):
    __tablename__ = "datasets"

    filename: Mapped[str]
    format: Mapped[DatasetFormat]
    size: Mapped[int]
