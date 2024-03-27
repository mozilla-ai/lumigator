from uuid import UUID

from fastapi import HTTPException, status
from ray.job_submission import JobSubmissionClient

from src.records.finetuning import FinetuningJobRecord
from src.repositories.finetuning import FinetuningJobRepository
from src.schemas.extras import ListingResponse
from src.schemas.finetuning import (
    FinetuningJobCreate,
    FinetuningJobResponse,
    FinetuningLogsResponse,
)


class FinetuningService:
    def __init__(self, job_repo: FinetuningJobRepository, ray_client: JobSubmissionClient):
        self.job_repo = job_repo
        self.ray_client = ray_client

    def _get_db_record(self, job_id: UUID) -> FinetuningJobRecord:
        record = self.job_repo.get(job_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Finetuning job {job_id} not found.")
        return record

    def create_job(self, request: FinetuningJobCreate) -> FinetuningJobResponse:
        # TODO: Dummy submission logic that needs to be updated for real
        submission_id = self.ray_client.submit_job(
            entrypoint="echo 'Hello from Ray!'",
        )
        record = self.job_repo.create(name=request.name, submission_id=submission_id)
        return FinetuningJobResponse.model_validate(record)

    def get_job(self, job_id: UUID) -> FinetuningJobResponse:
        record = self._get_db_record(job_id)
        return FinetuningJobResponse.model_validate(record)

    def get_job_logs(self, job_id: UUID) -> FinetuningLogsResponse:
        record = self._get_db_record(job_id)
        logs = self.ray_client.get_job_logs(record.submission_id)
        return FinetuningLogsResponse(
            id=record.id,
            status=record.status,
            logs=logs.strip().split("\n"),
        )

    def list_jobs(self, skip: int = 0, limit: int = 100) -> ListingResponse[FinetuningJobResponse]:
        total = self.job_repo.count()
        records = self.job_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[FinetuningJobResponse.model_validate(x) for x in records],
        )
