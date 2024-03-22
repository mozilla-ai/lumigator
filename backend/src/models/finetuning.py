import uuid

from sqlalchemy.orm import Mapped, mapped_column

from src.db import BaseSQLModel
from src.models.common import DateTimeSQLMixin
from src.schemas.extras import JobStatus


class FinetuningJob(BaseSQLModel, DateTimeSQLMixin):
    __tablename__ = "finetuning-jobs"

    # TODO: How to auto-generate id so we don't have to pass it on create?
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    submission_id: Mapped[str]
    status: Mapped[JobStatus]
