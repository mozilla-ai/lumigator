from uuid import UUID

from sqlalchemy.orm import Session

from backend.records.jobs import JobRecord, JobResultRecord
from backend.repositories.base import BaseRepository


class JobRepository(BaseRepository[JobRecord]):
    def __init__(self, session: Session):
        super().__init__(JobRecord, session)

    def get_by_experiment_id(self, experiment_id: UUID) -> list[JobRecord]:
        return self.session.query(JobRecord).where(JobRecord.experiment_id == experiment_id).all()


class JobResultRepository(BaseRepository[JobResultRecord]):
    def __init__(self, session: Session):
        super().__init__(JobResultRecord, session)

    def get_by_job_id(self, job_id: UUID) -> JobResultRecord | None:
        return self.session.query(JobResultRecord).where(JobResultRecord.job_id == job_id).first()



    def get_jobs_by_experiment_id(self, experiment_id: UUID) -> list[ExperimentRecord]:
        return (
            self.session.query(ExperimentRecord)
            .where(ExperimentRecord.id == experiment_id)
            .order_by(desc(ExperimentRecord.created_at))
            .limit(2)
            .all()
        )


