from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from mzai.backend.records.experiments import ExperimentRecord, ExperimentResultRecord
from mzai.schemas.extras import JobStatus


class ExperimentRepository:
    def __init__(self, session: Session):
        self.session = session

    def count(self) -> int:
        return self.session.query(ExperimentRecord).count()

    def create(self, name: str, description: str) -> ExperimentRecord:
        experiment = ExperimentRecord(
            name=name,
            description=description,
            status=JobStatus.IN_PROGRESS,
        )
        self.session.add(experiment)
        self.session.commit()
        self.session.refresh(experiment)
        return experiment

    def get(self, experiment_id: UUID) -> ExperimentRecord | None:
        return self.session.get(ExperimentRecord, experiment_id)

    def list(self, skip: int = 0, limit: int = 100) -> list[ExperimentRecord]:
        return self.session.query(ExperimentRecord).offset(skip).limit(limit).all()


class ExperimentResultRepository:
    def __init__(self, session: Session):
        self.session = session

    def count(self) -> int:
        return self.session.query(ExperimentResultRecord).count()

    def create(self, experiment_id: UUID, metrics: dict[str, Any]) -> ExperimentResultRecord:
        result = ExperimentResultRecord(experiment_id=experiment_id, metrics=metrics)
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
        return result

    def get(self, result_id: UUID) -> ExperimentResultRecord | None:
        return self.session.get(ExperimentResultRecord, result_id)

    def list(self, skip: int = 0, limit: int = 100) -> list[ExperimentResultRecord]:
        return self.session.query(ExperimentResultRecord).offset(skip).limit(limit).all()
