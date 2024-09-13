from sqlalchemy.orm import Mapped, mapped_column

from mzai.backend.records.base import BaseRecord
from mzai.backend.records.mixins import CreatedAtMixin, NameDescriptionMixin


class TaskRecord(BaseRecord, NameDescriptionMixin, CreatedAtMixin):
    __tablename__ = "tasks"
    models: Mapped[list[str]] = mapped_column(nullable=False)
