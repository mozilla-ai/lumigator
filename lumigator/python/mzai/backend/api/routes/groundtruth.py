from fastapi import APIRouter, status

from mzai.backend.api.deps import GroundTruthServiceDep
from mzai.schemas.extras import ListingResponse
from mzai.schemas.groundtruth import (
    GroundTruthDeploymentQueryResponse,
    GroundTruthDeploymentResponse,
    GroundTruthQueryRequest,
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


@router.post("/deployments/{deployment_id}")
def send_model_request(
    service: GroundTruthServiceDep, request: GroundTruthQueryRequest
) -> GroundTruthDeploymentQueryResponse:
    return service.run_inference(request)
