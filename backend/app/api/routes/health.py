from fastapi import APIRouter

from app.core.settings import settings
from app.schemas.extras import Health

router = APIRouter()


@router.get("/")
async def get_health() -> Health:
    return Health(environment=settings.ENVIRONMENT, status="Healthy")
