import uuid

from sqlalchemy.orm import Mapped, mapped_column

from src.db import BaseSQLModel
from src.models.common import DateTimeMappings
from src.schemas.extras import JobStatus


class FinetuningJob(BaseSQLModel, DateTimeMappings):
    __tablename__ = "finetuning-jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    submission_id: Mapped[str]
    status: Mapped[JobStatus]
