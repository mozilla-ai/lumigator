from fastapi import APIRouter

from src.schemas.extras import Health

router = APIRouter()


@router.get("/")
async def get_health() -> Health:
    return Health(status="Ok")
