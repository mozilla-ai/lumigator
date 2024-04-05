import uuid

from sqlalchemy.orm import Mapped, mapped_column

from mzai.model_builder.backend.db import BaseRecord
from mzai.model_builder.backend.records.mixins import DateTimeMixin, NameDescriptionMixin
from mzai.model_builder.schemas.extras import JobStatus


class FinetuningJobRecord(BaseRecord, NameDescriptionMixin, DateTimeMixin):
    __tablename__ = "finetuning-jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[str]
    status: Mapped[JobStatus]
