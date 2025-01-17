from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.records.experiments import ExperimentRecord
from backend.repositories.base import BaseRepository


class ExperimentRepository(BaseRepository[ExperimentRecord]):
    def __init__(self, session: Session):
        super().__init__(ExperimentRecord, session)

    def get_jobs_by_experiment_id(self, experiment_id: UUID) -> list[ExperimentRecord]:
        return (
            self.session.query(ExperimentRecord)
            .where(ExperimentRecord.id == experiment_id)
            .order_by(desc(ExperimentRecord.created_at))
            .limit(2)
            .all()
        )
