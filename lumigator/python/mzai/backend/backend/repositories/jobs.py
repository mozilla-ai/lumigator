from uuid import UUID

from sqlalchemy.orm import Session

from backend.records.jobs import JobRecord, JobResultRecord
from backend.repositories.base import BaseRepository


class JobRepository(BaseRepository[JobRecord]):
    def __init__(self, session: Session):
        super().__init__(JobRecord, session)


class JobResultRepository(BaseRepository[JobResultRecord]):
    def __init__(self, session: Session):
        super().__init__(JobResultRecord, session)

    def get_by_job_id(self, job_id: UUID) -> JobResultRecord | None:
        return (
            self.session.query(JobResultRecord)
            .where(JobResultRecord.job_id == job_id)
            .first()
        )
