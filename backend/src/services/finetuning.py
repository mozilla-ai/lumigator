from typing import Any
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException, status
from ray.job_submission import JobSubmissionClient

from src.jobs.entrypoints import FinetuningJobEntrypoint, submit_ray_job
from src.jobs.handlers import FinetuningJobHandler
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

    def create_job(
        self,
        request: FinetuningJobCreate,
        background_tasks: BackgroundTasks,
    ) -> FinetuningJobResponse:
        # Submit job to Ray
        entrypoint = FinetuningJobEntrypoint(config=request.config)
        submission_id = submit_ray_job(self.ray_client, entrypoint)

        # Create DB record of job submission
        record = self.job_repo.create(
            name=request.name,
            description=request.description,
            submission_id=submission_id,
        )

        # Poll for job completion in background
        handler = FinetuningJobHandler(record.id, submission_id)
        background_tasks.add_task(handler.poll)

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
