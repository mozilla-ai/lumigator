from fastapi import APIRouter

from app.schemas.extras import Health
from core.settings import settings

router = APIRouter()


@router.get("/")
async def get_health() -> Health:
    return Health(environment=settings.ENVIRONMENT, status="healthy")
