import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from mzai.backend.db import BaseRecord
from mzai.backend.records.mixins import DateTimeMixin, NameDescriptionMixin
from mzai.schemas.extras import JobStatus


class ExperimentRecord(BaseRecord, NameDescriptionMixin, DateTimeMixin):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    status: Mapped[JobStatus]


class ExperimentResultRecord(BaseRecord):
    __tablename__ = "experiment-results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiments.id"))
    metrics: Mapped[dict[str, float]]
