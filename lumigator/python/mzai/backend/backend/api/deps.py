from collections.abc import Generator
from typing import Annotated

import boto3
from fastapi import Depends
from mypy_boto3_s3.client import S3Client
from ray.job_submission import JobSubmissionClient
from s3fs import S3FileSystem
from sqlalchemy.orm import Session

from backend.db import session_manager
from backend.repositories.datasets import DatasetRepository
from backend.repositories.jobs import JobRepository, JobResultRepository
from backend.services.completions import LiteLLMCompletionService, MistralCompletionService
from backend.services.datasets import DatasetService
from backend.services.jobs import JobService
from backend.settings import settings


def get_db_session() -> Generator[Session, None, None]:
    with session_manager.session() as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db_session)]


def get_s3_client() -> Generator[S3Client, None, None]:
    return boto3.client("s3", endpoint_url=settings.S3_ENDPOINT_URL)


S3ClientDep = Annotated[S3Client, Depends(get_s3_client)]


def get_s3_filesystem() -> Generator[S3FileSystem, None, None]:
    return S3FileSystem()


S3FileSystemDep = Annotated[S3FileSystem, Depends(get_s3_filesystem)]


def get_dataset_service(
    session: DBSessionDep, s3_client: S3ClientDep, s3_filesystem: S3FileSystemDep
) -> DatasetService:
    dataset_repo = DatasetRepository(session)
    return DatasetService(dataset_repo, s3_client, s3_filesystem)


DatasetServiceDep = Annotated[DatasetService, Depends(get_dataset_service)]


def get_job_service(session: DBSessionDep, dataset_service: DatasetServiceDep) -> JobService:
    job_repo = JobRepository(session)
    result_repo = JobResultRepository(session)
    ray_client = JobSubmissionClient(settings.RAY_DASHBOARD_URL)
    return JobService(job_repo, result_repo, ray_client, dataset_service)


JobServiceDep = Annotated[JobService, Depends(get_job_service)]


def get_mistral_completion_service() -> MistralCompletionService:
    return MistralCompletionService()


MistralCompletionServiceDep = Annotated[
    MistralCompletionService, Depends(get_mistral_completion_service)
]


def get_openai_completion_service() -> LiteLLMCompletionService:
    return LiteLLMCompletionService()


LiteLLMCompletionServiceDep = Annotated[
    LiteLLMCompletionService, Depends(get_mistral_completion_service)
]
