from sqlalchemy.orm import Mapped

from mzai.backend.records.base import BaseRecord
from mzai.backend.records.mixins import CreatedAtMixin
from mzai.schemas.datasets import DatasetFormat


class DatasetRecord(BaseRecord, CreatedAtMixin):
    __tablename__ = "datasets"

    filename: Mapped[str]
    format: Mapped[DatasetFormat]
    size: Mapped[int]
