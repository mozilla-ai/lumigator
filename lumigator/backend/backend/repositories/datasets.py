from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.records.datasets import DatasetRecord
from backend.repositories.base import BaseRepository


class DatasetRepository(BaseRepository[DatasetRecord]):
    def __init__(self, session: Session):
        super().__init__(DatasetRecord, session)

    def get_by_job_id(self, job_id: UUID) -> DatasetRecord | None:
        statement = select(DatasetRecord).filter_by(run_id=job_id)
        return self.session.scalar(statement)
