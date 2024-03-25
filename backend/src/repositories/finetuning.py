from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.finetuning import FinetuningJob
from src.schemas.extras import JobStatus


class FinetuningJobRepository:
    def __init__(self, session: Session):
        self.session = session

    def count(self) -> int:
        stmt = select(func.count()).select_from(FinetuningJob)
        return self.session.scalar(stmt)

    def create(self, name: str, submission_id: str) -> FinetuningJob:
        job = FinetuningJob(name=name, submission_id=submission_id, status=JobStatus.CREATED)
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def get(self, job_id: UUID) -> FinetuningJob | None:
        return self.session.query(FinetuningJob).where(FinetuningJob.id == job_id).first()

    def list(self, skip: int = 0, limit: int = 100) -> list[FinetuningJob]:
        stmt = select(FinetuningJob).offset(skip).limit(limit)
        return self.session.scalars(stmt)
