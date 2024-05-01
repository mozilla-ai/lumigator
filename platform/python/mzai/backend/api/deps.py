from collections.abc import Generator
from typing import Annotated

import boto3
from fastapi import Depends, Header
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


def valid_content_length(content_length: int = Header(..., lt=settings.MAX_UPLOAD_SIZE)):
    return content_length


ContentLengthDep = Annotated[int, Depends(valid_content_length)]


def get_db_session() -> Generator[Session, None, None]:
    with session_manager.session() as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db_session)]


def get_dataset_service(session: DBSessionDep) -> DatasetService:
    dataset_repo = DatasetRepository(session)
    s3_client = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    return DatasetService(dataset_repo, s3_client)


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
