from schemas.datasets import DatasetFormat
from sqlalchemy.orm import Mapped

from app.records.base import BaseRecord
from app.records.mixins import CreatedAtMixin


class DatasetRecord(BaseRecord, CreatedAtMixin):
    __tablename__ = "datasets"

    filename: Mapped[str]
    format: Mapped[DatasetFormat]
    size: Mapped[int]
