from uuid import UUID

from sqlalchemy.orm import Session

from mzai.backend.records.experiments import ExperimentRecord, ExperimentResultRecord
from mzai.backend.repositories.base import BaseRepository


class ExperimentRepository(BaseRepository[ExperimentRecord]):
    def __init__(self, session: Session):
        super().__init__(ExperimentRecord, session)


class ExperimentResultRepository(BaseRepository[ExperimentResultRecord]):
    def __init__(self, session: Session):
        super().__init__(ExperimentResultRecord, session)

    def get_by_experiment_id(self, experiment_id: UUID) -> ExperimentResultRecord | None:
        return (
            self.session.query(ExperimentResultRecord)
            .where(ExperimentResultRecord.experiment_id == experiment_id)
            .first()
        )
