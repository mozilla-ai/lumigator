from uuid import UUID

from fastapi import BackgroundTasks

from mzai.backend.repositories.finetuning import FinetuningJobRepository
from mzai.backend.services.finetuning import FinetuningService
from mzai.schemas.finetuning import (
    FinetuningJobCreate,
    FinetuningJobResponse,
    FinetuningLogsResponse,
)


class FakeFinetuningService(FinetuningService):
    """Fake finetuning service that elides interactions with Ray."""

    def __init__(self, job_repo: FinetuningJobRepository):
        super().__init__(job_repo, ray_client=None)

    def create_job(self, request: FinetuningJobCreate) -> FinetuningJobResponse:
        return self.job_repo.create(name=request.name, description=request.description)

    def get_job_logs(self, job_id: UUID) -> FinetuningLogsResponse:
        record = self._get_job_record(job_id)
        return FinetuningLogsResponse(
            id=record.id, status=record.status, logs=["Fake logs from Ray."]
        )
