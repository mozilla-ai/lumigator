from fastapi import APIRouter, status

from mzai.backend.api.deps import GroundTruthServiceDep
from mzai.schemas.extras import ListingResponse
from mzai.schemas.groundtruth import (
    GroundTruthDeploymentCreate,
    GroundTruthDeploymentResponse,
    GroundTruthDeploymentUpdate,
    GroundTruthDeploymentLogsResponse,
)

router = APIRouter()

# TODO remove
@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.post("/deployments", status_code=status.HTTP_201_CREATED)
def create_groundtruth_deployment(
    service: GroundTruthServiceDep,
    request: GroundTruthDeploymentCreate,
) -> GroundTruthDeploymentResponse:
    return service.create_deployment(request)

@router.get("/deployments")
def list_groundtruth_deployments(
    service: GroundTruthServiceDep
) -> ListingResponse[GroundTruthDeploymentResponse]:
    return service.list_deployments()