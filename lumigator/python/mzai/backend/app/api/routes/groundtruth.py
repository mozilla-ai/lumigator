from uuid import UUID

from fastapi import APIRouter, status
from loguru import logger
from schemas.extras import ListingResponse
from schemas.groundtruth import (
    GroundTruthDeploymentCreate,
    GroundTruthDeploymentQueryResponse,
    GroundTruthDeploymentResponse,
    GroundTruthQueryRequest,
)

from app.api.deps import GroundTruthServiceDep

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
