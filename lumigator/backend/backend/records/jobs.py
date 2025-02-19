import uuid
from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Text

from backend.records.base import BaseRecord
from backend.records.mixins import DateTimeMixin, JobStatusMixin, NameDescriptionMixin


class JobRecord(BaseRecord, NameDescriptionMixin, JobStatusMixin, DateTimeMixin):
    __tablename__ = "jobs"

    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiments.id"), nullable=True)
    logs: Mapped[str] = mapped_column(Text)
    job_type: Mapped[str]


class JobResultRecord(BaseRecord):
    __tablename__ = "job-results"

    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"), unique=True)
    metrics: Mapped[dict[str, Any]]
