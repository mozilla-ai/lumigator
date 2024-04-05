from fastapi import APIRouter

from mzai.schemas.extras import HealthResponse
from mzai.backend.settings import settings

router = APIRouter()


@router.get("/")
async def get_health() -> HealthResponse:
    return HealthResponse(deployment_type=settings.DEPLOYMENT_TYPE, status="OK")
