from fastapi import APIRouter

from mzai.backend.settings import settings
from mzai.schemas.extras import HealthResponse
from mzai.backend.api.deps import GroundTruthServiceDep

router = APIRouter()

@router.post("/ground-truth/jobs")
async def get_health() -> HealthResponse:
    return HealthResponse(deployment_type=settings.DEPLOYMENT_TYPE, status="OK")

