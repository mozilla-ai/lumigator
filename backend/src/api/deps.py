from typing import Annotated, TypeVar

from fastapi import Depends
from ray.job_submission import JobSubmissionClient

from src.db import session_manager
from src.repositories.finetuning import FinetuningJobRepository
from src.utils import get_ray_client

RepositoryType = TypeVar("RepositoryType")


def ray_client_generator():
    yield get_ray_client()


def repository_generator(repository_cls: type[RepositoryType]):
    async def _yield_repository():
        async with session_manager.session() as session:
            yield repository_cls(session)

    return _yield_repository


RayClientDep = Annotated[JobSubmissionClient, Depends(ray_client_generator)]

FinetuningJobRepositoryDep = Annotated[
    FinetuningJobRepository,
    Depends(repository_generator(FinetuningJobRepository)),
]
