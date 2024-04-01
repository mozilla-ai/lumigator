from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from src.records.finetuning import FinetuningJobRecord
from src.schemas.extras import JobStatus


class FinetuningJobRepository:
    def __init__(self, session: Session):
        self.session = session

    def count(self) -> int:
        return self.session.query(FinetuningJobRecord).count()

    def create(self, name: str, description: str, submission_id: str) -> FinetuningJobRecord:
        job = FinetuningJobRecord(
            name=name,
            description=description,
            submission_id=submission_id,
            status=JobStatus.IN_PROGRESS,
        )
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def get(self, job_id: UUID) -> FinetuningJobRecord | None:
        return self.session.get(FinetuningJobRecord, job_id)

    def list(self, skip: int = 0, limit: int = 100) -> list[FinetuningJobRecord]:
        return self.session.query(FinetuningJobRecord).offset(skip).limit(limit).all()

    def update(self, job_id: UUID, updates: dict[str, Any]) -> FinetuningJobRecord | None:
        job = self.get(job_id)
        if job is None:
            return None
        for key, value in updates.items():
            setattr(job, key, value)
        self.session.commit()
        self.session.refresh(job)
        return job
