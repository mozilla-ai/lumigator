from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.finetuning import FinetuningJob
from src.schemas.extras import JobStatus


class FinetuningJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count(self) -> int:
        pass

    async def create(self, name: str, submission_id: str):
        job = FinetuningJob(name=name, submission_id=submission_id, status=JobStatus.CREATED)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get(self, job_id: UUID):
        pass

    async def get_logs(self, job_id: UUID):
        pass

    async def list(self, skip: int = 0, limit: int = 100):
        pass
