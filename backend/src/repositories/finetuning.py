from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.finetuning import FinetuningJob
from src.schemas.extras import JobStatus


class FinetuningJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count(self) -> int:
        stmt = select(func.count()).select_from(FinetuningJob)
        return await self.session.scalar(stmt)

    async def create(self, name: str, submission_id: str) -> FinetuningJob:
        job = FinetuningJob(name=name, submission_id=submission_id, status=JobStatus.CREATED)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get(self, job_id: UUID) -> FinetuningJob | None:
        stmt = select(FinetuningJob).where(FinetuningJob.id == job_id)
        return await self.session.scalar(stmt)

    async def list(self, skip: int = 0, limit: int = 100) -> list[FinetuningJob]:
        stmt = select(FinetuningJob).offset(skip).limit(limit)
        return await self.session.scalars(stmt)
