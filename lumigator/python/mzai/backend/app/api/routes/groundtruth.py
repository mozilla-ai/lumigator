# from mzai.schemas.extras import ListingResponse
# from mzai.schemas.groundtruth import (
#     GroundTruthDeploymentCreate,
#     GroundTruthDeploymentQueryResponse,
#     GroundTruthDeploymentResponse,
#     GroundTruthQueryRequest,
# )
import datetime
from enum import Enum
from typing import Generic, TypeVar
from uuid import UUID

from fastapi import APIRouter, status
from loguru import logger
from pydantic import BaseModel

from app.api.deps import GroundTruthServiceDep

ItemType = TypeVar("ItemType")


# from mzai.schemas.deployments import DeploymentStatus
class DeploymentStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


class GroundTruthDeploymentCreate(BaseModel):
    num_gpus: float | None = None
    num_cpus: float | None = None
    num_replicas: int | None = None


class GroundTruthDeploymentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class GroundTruthDeploymentResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: DeploymentStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None


class GroundTruthDeploymentLogsResponse(BaseModel):
    id: UUID
    status: DeploymentStatus
    logs: list[str]


class GroundTruthQueryRequest(BaseModel):
    text: str


class GroundTruthDeploymentQueryResponse(BaseModel):
    deployment_response: dict[str, str]


class ListingResponse(BaseModel, Generic[ItemType]):
    total: int
    items: list[ItemType]


router = APIRouter()


@router.post("/deployments", status_code=status.HTTP_201_CREATED)
def create_groundtruth_deployment(
    service: GroundTruthServiceDep, request: GroundTruthDeploymentCreate
) -> GroundTruthDeploymentResponse:
    logger.info("Creating new deployment")
    return service.create_deployment(request)


@router.get("/deployments")
def list_groundtruth_deployments(
    service: GroundTruthServiceDep,
) -> ListingResponse[GroundTruthDeploymentResponse]:
    return service.list_deployments()


@router.post("/deployments/{deployment_id}")
def send_model_request(
    service: GroundTruthServiceDep, request: GroundTruthQueryRequest
) -> GroundTruthDeploymentQueryResponse:
    logger.info("Processing model inference request")
    return service.run_inference(request)


@router.delete("/deployments/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deployment(service: GroundTruthServiceDep, deployment_id: UUID) -> None:
    service.delete_deployment(deployment_id)
