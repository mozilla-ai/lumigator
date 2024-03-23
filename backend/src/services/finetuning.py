from uuid import UUID

from fastapi import HTTPException, status
from ray.job_submission import JobSubmissionClient

from src.models.finetuning import FinetuningJob
from src.repositories.finetuning import FinetuningJobRepository
from src.schemas.extras import ItemsList
from src.schemas.finetuning import (
    FinetuningJobCreate,
    FinetuningJobResponse,
    FinetuningLogsResponse,
)


class FinetuningService:
    def __init__(self, job_repo: FinetuningJobRepository, ray_client: JobSubmissionClient):
        self.job_repo = job_repo
        self.ray_client = ray_client

    async def _get_db_job(self, job_id: UUID) -> FinetuningJob:
        db_job = await self.job_repo.get(job_id)
        if db_job is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Finetuning job {job_id} not found.")
        return db_job

    async def create_job(self, request: FinetuningJobCreate) -> FinetuningJobResponse:
        submission_id = self.ray_client.submit_job(entrypoint="echo 'Hello from Ray!'")
        db_job = await self.job_repo.create(name=request.name, submission_id=submission_id)
        return FinetuningJobResponse.model_validate(db_job)

    async def get_job(self, job_id: UUID) -> FinetuningJobResponse:
        db_job = self._get_db_job(job_id)
        return FinetuningJobResponse.model_validate(db_job)

    async def get_job_logs(self, job_id: UUID) -> FinetuningLogsResponse:
        db_job = await self._get_db_job(job_id)
        # TODO: This call to Ray should be async to avoid blocking the FastAPI thread
        logs = self.ray_client.get_job_logs(db_job.submission_id)
        return FinetuningLogsResponse(
            id=db_job.id,
            status=db_job.status,
            logs=logs.strip().split("\n"),
        )

    async def list_jobs(self, skip: int = 0, limit: int = 100) -> ItemsList[FinetuningJobResponse]:
        total = await self.job_repo.count()
        db_jobs = await self.job_repo.list(skip, limit)
        return ItemsList(
            total=total,
            items=[FinetuningJobResponse.model_validate(x) for x in db_jobs],
        )
