from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from mzai.backend.records.experiments import ExperimentRecord, ExperimentResultRecord
from mzai.backend.repositories.base import BaseRepository


class ExperimentRepository(BaseRepository[ExperimentRecord]):
    def __init__(self, session: Session):
        super().__init__(ExperimentRecord, session)

    def create(self, name: str, description: str) -> ExperimentRecord:
        experiment = ExperimentRecord(name=name, description=description)
        self.session.add(experiment)
        self.session.commit()
        self.session.refresh(experiment)
        return experiment


class ExperimentResultRepository(BaseRepository[ExperimentResultRecord]):
    def __init__(self, session: Session):
        super().__init__(ExperimentResultRecord, session)

    def create(self, experiment_id: UUID, metrics: dict[str, Any]) -> ExperimentResultRecord:
        result = ExperimentResultRecord(experiment_id=experiment_id, metrics=metrics)
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
        return result

    def get_by_experiment_id(self, experiment_id: UUID) -> ExperimentResultRecord | None:
        return (
            self.session.query(ExperimentResultRecord)
            .where(ExperimentResultRecord.experiment_id == experiment_id)
            .first()
        )
