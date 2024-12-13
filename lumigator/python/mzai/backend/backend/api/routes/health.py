from fastapi import APIRouter
from lumigator_schemas.extras import HealthResponse

from backend.settings import settings

router = APIRouter()


@router.get("/")
def get_health() -> HealthResponse:
    return HealthResponse(deployment_type=settings.DEPLOYMENT_TYPE, status="OK")

