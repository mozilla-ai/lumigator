import uuid

from sqlalchemy.orm import Mapped, mapped_column

from src.db import BaseRecord
from src.records.mixins import DateTimeMixin, NameDescriptionMixin
from src.schemas.extras import JobStatus


class FinetuningJobRecord(BaseRecord, NameDescriptionMixin, DateTimeMixin):
    __tablename__ = "finetuning-jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[str]
    status: Mapped[JobStatus]
