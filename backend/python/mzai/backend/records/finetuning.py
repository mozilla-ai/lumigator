import uuid

from mzai.backend.db import BaseRecord
from mzai.backend.records.mixins import DateTimeMixin, NameDescriptionMixin
from mzai.schemas.extras import JobStatus
from sqlalchemy.orm import Mapped, mapped_column


class FinetuningJobRecord(BaseRecord, NameDescriptionMixin, DateTimeMixin):
    __tablename__ = "finetuning-jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[str]
    status: Mapped[JobStatus]
