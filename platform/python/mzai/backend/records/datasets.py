import uuid

from sqlalchemy.orm import Mapped, mapped_column

from mzai.backend.db import BaseRecord
from mzai.backend.records.mixins import CreatedAtMixin
from mzai.schemas.datasets import DatasetFormat


class DatasetRecord(BaseRecord, CreatedAtMixin):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    filename: Mapped[str]
    format: Mapped[DatasetFormat]
    size: Mapped[int]
