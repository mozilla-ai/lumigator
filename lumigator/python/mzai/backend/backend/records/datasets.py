import uuid

from lumigator_schemas.datasets import DatasetFormat
from sqlalchemy.orm import Mapped, mapped_column

from backend.records.base import BaseRecord
from backend.records.mixins import CreatedAtMixin


class DatasetRecord(BaseRecord, CreatedAtMixin):
    __tablename__ = "datasets"

    filename: Mapped[str]
    format: Mapped[DatasetFormat]
    size: Mapped[int]
    ground_truth: Mapped[bool]
    run_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, default=None)
    generated: Mapped[bool] = mapped_column(default=False)
    generated_by: Mapped[str | None] = mapped_column(nullable=True, default=None)
