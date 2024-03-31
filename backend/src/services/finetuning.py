from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from ray.job_submission import JobSubmissionClient

from src.records.finetuning import FinetuningJobRecord
from src.repositories.finetuning import FinetuningJobRepository
from src.schemas.extras import JobStatus, ListingResponse
from src.schemas.finetuning import (
    FinetuningJobCreate,
    FinetuningJobResponse,
    FinetuningJobUpdate,
    FinetuningLogsResponse,
)


class FinetuningService:
    def __init__(self, job_repo: FinetuningJobRepository, ray_client: JobSubmissionClient):
        self.job_repo = job_repo
        self.ray_client = ray_client

    def _raise_job_not_found(self, job_id: UUID):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Finetuning job {job_id} not found.")

    def _get_job_record(self, job_id: UUID) -> FinetuningJobRecord:
        record = self.job_repo.get(job_id)
        if record is None:
            self._raise_job_not_found(job_id)
        return record

    def _update_job_record(self, job_id: UUID, updates: dict[str, Any]) -> FinetuningJobRecord:
        record = self.job_repo.update(job_id, updates)
        if record is None:
            self._raise_job_not_found(job_id)
        return record

    def create_job(self, request: FinetuningJobCreate) -> FinetuningJobResponse:
        # TODO: Dummy submission logic that needs to be updated for real
        submission_id = self.ray_client.submit_job(
            entrypoint="echo 'Hello from Ray!'",
        )
        record = self.job_repo.create(
            name=request.name,
            description=request.description,
            submission_id=submission_id,
        )
        return FinetuningJobResponse.model_validate(record)

    def get_job(self, job_id: UUID) -> FinetuningJobResponse:
        record = self._get_job_record(job_id)
        return FinetuningJobResponse.model_validate(record)

    def get_job_logs(self, job_id: UUID) -> FinetuningLogsResponse:
        record = self._get_job_record(job_id)
        logs = self.ray_client.get_job_logs(record.submission_id)
        return FinetuningLogsResponse(
            id=record.id,
            status=record.status,
            logs=logs.strip().split("\n"),
        )

    def get_job_submission_id(self, job_id: UUID) -> str:
        record = self._get_job_record(job_id)
        return record.submission_id

    def list_jobs(self, skip: int = 0, limit: int = 100) -> ListingResponse[FinetuningJobResponse]:
        total = self.job_repo.count()
        records = self.job_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[FinetuningJobResponse.model_validate(x) for x in records],
        )

    def update_job(self, job_id: UUID, request: FinetuningJobUpdate) -> FinetuningJobResponse:
        updates = request.model_dump(exclude_unset=True)
        record = self._update_job_record(job_id, updates)
        return FinetuningJobResponse.model_validate(record)

    def update_job_status(self, job_id: UUID, status: JobStatus) -> FinetuningJobResponse:
        updates = {"status": status}
        record = self._update_job_record(job_id, updates)
        return FinetuningJobResponse.model_validate(record)
