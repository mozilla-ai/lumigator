import uuid
from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.records.base import BaseRecord
from app.records.mixins import DateTimeMixin, JobStatusMixin, NameDescriptionMixin


class ExperimentRecord(BaseRecord, NameDescriptionMixin, JobStatusMixin, DateTimeMixin):
    __tablename__ = "experiments"


class ExperimentResultRecord(BaseRecord):
    __tablename__ = "experiment-results"

    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiments.id"), unique=True)
    metrics: Mapped[dict[str, Any]]  # TODO: This will almost certainly change
