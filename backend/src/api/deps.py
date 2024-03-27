from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from ray.job_submission import JobSubmissionClient
from sqlalchemy.orm import Session

from src.db import session_manager
from src.repositories.finetuning import FinetuningJobRepository
from src.services.finetuning import FinetuningService
from src.settings import settings


def get_ray_client() -> JobSubmissionClient:
    return JobSubmissionClient(
        f"http://{settings.RAY_HEAD_NODE_HOST}:{settings.RAY_HEAD_NODE_PORT}"
    )


RayClientDep = Annotated[JobSubmissionClient, Depends(get_ray_client)]


def get_db_session() -> Generator[Session, None, None]:
    with session_manager.session() as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db_session)]


def get_finetuning_service(session: DBSessionDep, ray_client: RayClientDep) -> FinetuningService:
    job_repo = FinetuningJobRepository(session)
    return FinetuningService(job_repo, ray_client)


FinetuningServiceDep = Annotated[FinetuningService, Depends(get_finetuning_service)]
