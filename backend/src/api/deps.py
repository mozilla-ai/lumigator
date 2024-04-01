from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from ray.job_submission import JobSubmissionClient
from sqlalchemy.orm import Session

from src.db import session_manager
from src.repositories.finetuning import FinetuningJobRepository
from src.services.finetuning import FinetuningService
from src.utils import get_ray_job_client

RayJobClientDep = Annotated[JobSubmissionClient, Depends(get_ray_job_client)]


def get_db_session() -> Generator[Session, None, None]:
    with session_manager.session() as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db_session)]


def get_finetuning_service(session: DBSessionDep, ray_client: RayJobClientDep) -> FinetuningService:
    job_repo = FinetuningJobRepository(session)
    return FinetuningService(job_repo, ray_client)


FinetuningServiceDep = Annotated[FinetuningService, Depends(get_finetuning_service)]
