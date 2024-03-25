from typing import Annotated

from fastapi import Depends

from src.db import session_manager
from src.repositories.finetuning import FinetuningJobRepository
from src.services.finetuning import FinetuningService
from src.utils import get_ray_client


def get_finetuning_service():
    with session_manager.session() as session:
        job_repo = FinetuningJobRepository(session)
        ray_client = get_ray_client()
        yield FinetuningService(job_repo, ray_client)


FinetuningServiceDep = Annotated[FinetuningService, Depends(get_finetuning_service)]
