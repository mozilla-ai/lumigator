from fastapi import APIRouter

from mzai.backend.settings import settings
from mzai.schemas.extras import HealthResponse
from mzai.backend.api.deps import GroundTruthServiceDep

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello World"}