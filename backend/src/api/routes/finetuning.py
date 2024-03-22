from uuid import UUID

from fastapi import APIRouter

from src.api.deps import FinetuningJobRepositoryDep, RayClientDep
from src.schemas.finetuning import FinetuningJobCreate, FinetuningJobResponse, ListFinetuningJobs

router = APIRouter()


@router.post("/jobs", response_model=FinetuningJobResponse)
async def create_finetuning_job(
    repo: FinetuningJobRepositoryDep,
    ray_client: RayClientDep,
    request: FinetuningJobCreate,
):
    submission_id = ray_client.submit_job(entrypoint="echo 'Hello from platform-backend!'")
    job = await repo.create(name=request.name, submission_id=submission_id)
    return job


@router.get("/jobs/{job_id}", response_model=FinetuningJobResponse)
async def get_finetuning_job(repo: FinetuningJobRepositoryDep, job_id: UUID):
    pass


@router.get("/jobs/{job_id}/logs", response_model=FinetuningJobResponse)
async def get_finetuning_job_logs(repo: FinetuningJobRepositoryDep, job_id: UUID):
    pass


@router.get("/jobs", response_model=ListFinetuningJobs)
async def list_finetuning_jobs(repo: FinetuningJobRepositoryDep, skip: int, limit: int):
    pass
