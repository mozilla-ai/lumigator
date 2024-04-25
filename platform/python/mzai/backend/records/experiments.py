import uuid
from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from mzai.backend.db import BaseRecord
from mzai.backend.records.mixins import DateTimeMixin, NameDescriptionMixin
from mzai.schemas.jobs import JobStatus


class ExperimentRecord(BaseRecord, NameDescriptionMixin, DateTimeMixin):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    status: Mapped[JobStatus] = mapped_column(default=JobStatus.CREATED)


class ExperimentResultRecord(BaseRecord):
    __tablename__ = "experiment-results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiments.id"), unique=True)
    metrics: Mapped[dict[str, Any]]  # TODO: This will almost certainly change
