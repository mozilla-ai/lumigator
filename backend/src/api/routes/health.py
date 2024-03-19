from fastapi import APIRouter

from src.app.schemas.extras import Health
from src.core.settings import settings

router = APIRouter()


@router.get("/")
async def get_health() -> Health:
    return Health(environment=settings.ENVIRONMENT, status="healthy")
