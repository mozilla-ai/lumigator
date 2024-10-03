from sqlalchemy.orm import Mapped

from backend.records.base import BaseRecord
from backend.records.mixins import CreatedAtMixin
from schemas.datasets import DatasetFormat


class DatasetRecord(BaseRecord, CreatedAtMixin):
    __tablename__ = "datasets"

    filename: Mapped[str]
    format: Mapped[DatasetFormat]
    size: Mapped[int]
