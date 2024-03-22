from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.deps import FinetuningJobRepositoryDep, RayClientDep
from src.schemas.finetuning import (
    FinetuningJobCreate,
    FinetuningJobResponse,
    FinetuningLogsResponse,
    ListFinetuningJobs,
)

router = APIRouter()


@router.post("/jobs", response_model=FinetuningJobResponse)
async def create_finetuning_job(
    repo: FinetuningJobRepositoryDep,
    ray_client: RayClientDep,
    request: FinetuningJobCreate,
):
    submission_id = ray_client.submit_job(entrypoint="echo 'Hello from Ray!'")
    job = await repo.create(name=request.name, submission_id=submission_id)
    return job


@router.get("/jobs/{job_id}", response_model=FinetuningJobResponse)
async def get_finetuning_job(repo: FinetuningJobRepositoryDep, job_id: UUID):
    job = await repo.get(job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Finetuning job {job_id} not found")
    return job


@router.get("/jobs/{job_id}/logs", response_model=FinetuningLogsResponse)
async def get_finetuning_job_logs(
    repo: FinetuningJobRepositoryDep,
    ray_client: RayClientDep,
    job_id: UUID,
):
    job = await repo.get(job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Finetuning job {job_id} not found")
    logs = ray_client.get_job_logs(job.submission_id)
    return FinetuningLogsResponse(id=job.id, status=job.status, logs=logs.strip().split("\n"))


@router.get("/jobs", response_model=ListFinetuningJobs)
async def list_finetuning_jobs(repo: FinetuningJobRepositoryDep, skip: int = 0, limit: int = 100):
    count = await repo.count()
    jobs = await repo.list(skip, limit)
    return ListFinetuningJobs(count=count, jobs=jobs)
