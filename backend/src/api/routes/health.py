from fastapi import APIRouter

from src.schemas.extras import Health
from src.settings import settings

router = APIRouter()


@router.get("/")
async def get_health() -> Health:
    return Health(deployment=settings.DEPLOYMENT_TYPE, status="Ok")
