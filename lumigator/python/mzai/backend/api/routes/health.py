from fastapi import APIRouter

from mzai.backend.settings import settings
from mzai.schemas.extras import HealthResponse

router = APIRouter()


@router.get("/")
async def get_health() -> HealthResponse:
    return HealthResponse(deployment_type=settings.DEPLOYMENT_TYPE, status="OK")
