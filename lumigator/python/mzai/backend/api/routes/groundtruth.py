from fastapi import APIRouter, status
from uuid import UUID

from mzai.backend.api.deps import GroundTruthServiceDep
from mzai.schemas.extras import ListingResponse
from mzai.schemas.groundtruth import (
    GroundTruthDeploymentCreate,
    GroundTruthDeploymentQueryResponse,
    GroundTruthDeploymentResponse,
    GroundTruthQueryRequest,
)

router = APIRouter()


@router.post("/deployments", status_code=status.HTTP_201_CREATED)
def create_groundtruth_deployment(
    service: GroundTruthServiceDep, request: GroundTruthDeploymentCreate
) -> GroundTruthDeploymentResponse:
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
    return service.run_inference(request)


@router.delete("/deployments/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deployment(service: GroundTruthServiceDep, deployment_id: UUID) -> None:
    service.delete_deployment(deployment_id)
