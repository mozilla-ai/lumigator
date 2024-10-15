from schemas.datasets import DatasetFormat
from sqlalchemy.orm import Mapped

from backend.records.base import BaseRecord
from backend.records.mixins import CreatedAtMixin


class DatasetRecord(BaseRecord, CreatedAtMixin):
    __tablename__ = "datasets"

    filename: Mapped[str]
    format: Mapped[DatasetFormat]
    size: Mapped[int]
    ground_truth: Mapped[bool]
