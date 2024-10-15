import uuid
from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.records.base import BaseRecord
from backend.records.mixins import DateTimeMixin, JobStatusMixin, NameDescriptionMixin


class JobRecord(BaseRecord, NameDescriptionMixin, JobStatusMixin, DateTimeMixin):
    __tablename__ = "jobs"


class JobResultRecord(BaseRecord):
    __tablename__ = "job-results"

    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"), unique=True)
    metrics: Mapped[dict[str, Any]]
