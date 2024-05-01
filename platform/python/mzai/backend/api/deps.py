from collections.abc import Generator
from typing import Annotated, Any

import boto3
from fastapi import Depends
from ray.job_submission import JobSubmissionClient
from sqlalchemy.orm import Session

from mzai.backend.db import session_manager
from mzai.backend.repositories.datasets import DatasetRepository
from mzai.backend.repositories.experiments import ExperimentRepository, ExperimentResultRepository
from mzai.backend.repositories.finetuning import FinetuningJobRepository
from mzai.backend.services.datasets import DatasetService
from mzai.backend.services.experiments import ExperimentService
from mzai.backend.services.finetuning import FinetuningService
from mzai.backend.settings import settings


def get_db_session() -> Generator[Session, None, None]:
    with session_manager.session() as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db_session)]


def get_s3_client() -> Generator[Any, None, None]:
    return boto3


def get_dataset_service(session: DBSessionDep) -> DatasetService:
    dataset_repo = DatasetRepository(session)
    s3_client = boto3.client
    pass


def get_finetuning_service(session: DBSessionDep) -> FinetuningService:
    job_repo = FinetuningJobRepository(session)
    ray_client = JobSubmissionClient(settings.RAY_DASHBOARD_URL)
    return FinetuningService(job_repo, ray_client)


def get_experiment_service(session: DBSessionDep) -> ExperimentService:
    experiment_repo = ExperimentRepository(session)
    result_repo = ExperimentResultRepository(session)
    ray_client = JobSubmissionClient(settings.RAY_DASHBOARD_URL)
    return ExperimentService(experiment_repo, result_repo, ray_client)


DatasetServiceDep = Annotated[DatasetService, Depends(get_dataset_service)]
FinetuningServiceDep = Annotated[FinetuningService, Depends(get_finetuning_service)]
ExperimentServiceDep = Annotated[ExperimentService, Depends(get_experiment_service)]
