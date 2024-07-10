from uuid import UUID

from fastapi import APIRouter, status

from mzai.backend.api.deps import GroundTruthServiceDep
from mzai.schemas.extras import ListingResponse
from mzai.schemas.groundtruth import (
    GroundTruthDeploymentResponse,
)

router = APIRouter()


@router.post("/deployments", status_code=status.HTTP_201_CREATED)
def create_groundtruth_deployment(
    service: GroundTruthServiceDep,
) -> GroundTruthDeploymentResponse:
    return service.create_deployment()


@router.get("/deployments")
def list_groundtruth_deployments(
    service: GroundTruthServiceDep,
) -> ListingResponse[GroundTruthDeploymentResponse]:
    return service.list_deployments()


@router.post("/deployments/{deployment_id}/{query}")
def send_model_request(
    service: GroundTruthServiceDep, deployment_id: UUID, query: str
) -> GroundTruthDeploymentResponse:
    return service.run_inference(deployment_id, query)
