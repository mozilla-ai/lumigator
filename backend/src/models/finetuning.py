import uuid
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from src.db import BaseSQLModel
from src.schemas.extras import JobStatus


class FinetuningJob(BaseSQLModel):
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid.uuid4)
    name: Mapped[str]
    submission_id: Mapped[str]
    status: Mapped[JobStatus]
