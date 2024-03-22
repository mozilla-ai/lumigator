from fastapi import APIRouter

from src.api.routes import health
from src.models import finetuning

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(finetuning.router, prefix="/finetuning", tags=["finetuning"])
