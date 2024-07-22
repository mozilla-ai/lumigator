from collections.abc import Generator
from typing import Annotated

import boto3
from fastapi import Depends
from mypy_boto3_s3.client import S3Client
from ray.dashboard.modules.serve.sdk import ServeSubmissionClient
from ray.job_submission import JobSubmissionClient
from sqlalchemy.orm import Session

from mzai.backend.db import session_manager
from mzai.backend.repositories.datasets import DatasetRepository
from mzai.backend.repositories.experiments import ExperimentRepository, ExperimentResultRepository
from mzai.backend.repositories.finetuning import FinetuningJobRepository
from mzai.backend.repositories.groundtruth import GroundTruthDeploymentRepository
from mzai.backend.services.datasets import DatasetService
from mzai.backend.services.experiments import ExperimentService
from mzai.backend.services.finetuning import FinetuningService
from mzai.backend.services.groundtruth import GroundTruthService
from mzai.backend.settings import settings


def get_db_session() -> Generator[Session, None, None]:
    with session_manager.session() as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db_session)]


def get_s3_client() -> Generator[S3Client, None, None]:
    return boto3.client("s3", endpoint_url=settings.S3_ENDPOINT_URL)


S3ClientDep = Annotated[S3Client, Depends(get_s3_client)]


def get_dataset_service(session: DBSessionDep, s3_client: S3ClientDep) -> DatasetService:
    dataset_repo = DatasetRepository(session)
    return DatasetService(dataset_repo, s3_client)


DatasetServiceDep = Annotated[DatasetService, Depends(get_dataset_service)]


def get_finetuning_service(session: DBSessionDep) -> FinetuningService:
    job_repo = FinetuningJobRepository(session)
    ray_client = JobSubmissionClient(settings.RAY_DASHBOARD_URL)
    return FinetuningService(job_repo, ray_client)


FinetuningServiceDep = Annotated[FinetuningService, Depends(get_finetuning_service)]


def get_experiment_service(
    session: DBSessionDep, dataset_service: DatasetServiceDep
) -> ExperimentService:
    experiment_repo = ExperimentRepository(session)
    result_repo = ExperimentResultRepository(session)
    ray_client = JobSubmissionClient(settings.RAY_DASHBOARD_URL)
    return ExperimentService(experiment_repo, result_repo, ray_client, dataset_service)


ExperimentServiceDep = Annotated[ExperimentService, Depends(get_experiment_service)]


def get_ground_truth_service(session: DBSessionDep) -> GroundTruthService:
    deployment_repo = GroundTruthDeploymentRepository(session)
    ray_serve_client = ServeSubmissionClient(settings.RAY_DASHBOARD_URL)
    return GroundTruthService(deployment_repo, ray_serve_client)


GroundTruthServiceDep = Annotated[GroundTruthService, Depends(get_ground_truth_service)]
