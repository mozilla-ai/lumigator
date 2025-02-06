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
from backend.services.completions import LiteLLMCompletionService as CompletionService
from backend.services.datasets import DatasetService
from backend.services.experiments import ExperimentService
from backend.services.jobs import JobService
from backend.services.workflows import WorkflowService
from backend.settings import settings
from backend.tracking import tracking_client_manager


def get_db_session() -> Generator[Session, None, None]:
    with session_manager.session() as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db_session)]


def get_tracking_client() -> Generator[Session, None, None]:
    with tracking_client_manager.connect() as client:
        yield client


TrackingClientDep = Annotated[Session, Depends(get_tracking_client)]


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


def get_experiment_service(
    session: DBSessionDep,
    tracking_client: TrackingClientDep,
    job_service: JobServiceDep,
    dataset_service: DatasetServiceDep,
) -> ExperimentService:
    job_repo = JobRepository(session)
    return ExperimentService(job_repo, job_service, dataset_service, tracking_client)


ExperimentServiceDep = Annotated[ExperimentService, Depends(get_experiment_service)]


def get_workflow_service(
    session: DBSessionDep,
    tracking_client: TrackingClientDep,
    job_service: JobServiceDep,
    dataset_service: DatasetServiceDep,
) -> WorkflowService:
    job_repo = JobRepository(session)
    return WorkflowService(job_repo, job_service, dataset_service, tracking_client=tracking_client)


WorkflowServiceDep = Annotated[WorkflowService, Depends(get_workflow_service)]


def get_completion_service() -> CompletionService:
    return CompletionService()


CompletionServiceDep = Annotated[CompletionService, Depends(get_workflow_service)]
