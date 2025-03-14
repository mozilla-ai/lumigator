import os
from collections.abc import Generator
from typing import Annotated

import boto3
from fastapi import BackgroundTasks, Depends
from lumigator_schemas.redactor import Redactor
from mypy_boto3_s3.client import S3Client
from ray.job_submission import JobSubmissionClient
from s3fs import S3FileSystem
from sqlalchemy.orm import Session

from backend.db import session_manager
from backend.repositories.datasets import DatasetRepository
from backend.repositories.jobs import JobRepository, JobResultRepository
from backend.repositories.secrets import SecretRepository
from backend.services.datasets import DatasetService
from backend.services.experiments import ExperimentService
from backend.services.jobs import JobService
from backend.services.secrets import SecretService
from backend.services.workflows import WorkflowService
from backend.settings import settings
from backend.tracking import TrackingClientManager, tracking_client_manager


def get_db_session() -> Generator[Session, None, None]:
    with session_manager.session() as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db_session)]


def get_tracking_client() -> Generator[TrackingClientManager, None, None]:
    with tracking_client_manager.connect() as client:
        yield client


TrackingClientDep = Annotated[TrackingClientManager, Depends(get_tracking_client)]


def get_s3_client() -> S3Client:
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    aws_default_region = os.environ.get("AWS_DEFAULT_REGION")

    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_default_region,
    )


S3ClientDep = Annotated[S3Client, Depends(get_s3_client)]


def get_s3_filesystem() -> S3FileSystem:
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    aws_default_region = os.environ.get("AWS_DEFAULT_REGION")

    # Pass the session to S3FileSystem
    return S3FileSystem(
        key=aws_access_key_id,
        secret=aws_secret_access_key,
        endpoint_url=settings.S3_ENDPOINT_URL,
        client_kwargs={"region_name": aws_default_region},
    )


S3FileSystemDep = Annotated[S3FileSystem, Depends(get_s3_filesystem)]


def get_dataset_service(
    session: DBSessionDep, s3_client: S3ClientDep, s3_filesystem: S3FileSystemDep
) -> DatasetService:
    dataset_repo = DatasetRepository(session)
    return DatasetService(dataset_repo, s3_client, s3_filesystem)


DatasetServiceDep = Annotated[DatasetService, Depends(get_dataset_service)]


def get_secret_service(session: DBSessionDep) -> SecretService:
    secret_repo = SecretRepository(session)
    return SecretService(settings.LUMIGATOR_SECRET_KEY, secret_repo)


SecretServiceDep = Annotated[SecretService, Depends(get_secret_service)]


def get_job_service(
    session: DBSessionDep,
    dataset_service: DatasetServiceDep,
    secret_service: SecretServiceDep,
    background_tasks: BackgroundTasks,
) -> JobService:
    job_repo = JobRepository(session)
    result_repo = JobResultRepository(session)
    ray_client = JobSubmissionClient(settings.RAY_DASHBOARD_URL)
    return JobService(job_repo, result_repo, ray_client, dataset_service, secret_service, background_tasks)


JobServiceDep = Annotated[JobService, Depends(get_job_service)]


def get_experiment_service(
    session: DBSessionDep,
    tracking_client: TrackingClientDep,
    job_service: JobServiceDep,
    dataset_service: DatasetServiceDep,
) -> ExperimentService:
    job_repo = JobRepository(session)
    return ExperimentService(job_repo, job_service, dataset_service, tracking_client)


def get_workflow_service(
    session: DBSessionDep,
    tracking_client: TrackingClientDep,
    job_service: JobServiceDep,
    dataset_service: DatasetServiceDep,
    secret_service: SecretServiceDep,
    background_tasks: BackgroundTasks,
) -> WorkflowService:
    job_repo = JobRepository(session)
    return WorkflowService(
        job_repo=job_repo,
        job_service=job_service,
        dataset_service=dataset_service,
        secret_checker=secret_service,
        background_tasks=background_tasks,
        tracking_client=tracking_client,
    )


ExperimentServiceDep = Annotated[ExperimentService, Depends(get_experiment_service)]


WorkflowServiceDep = Annotated[WorkflowService, Depends(get_workflow_service)]


def get_redactor() -> Redactor:
    return Redactor(settings.sensitive_patterns)


RedactorDep = Annotated[Redactor, Depends(get_redactor)]
