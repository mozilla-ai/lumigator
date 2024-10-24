from fastapi import APIRouter

from backend.api.routes import completions, datasets, health, jobs
from backend.api.tags import Tags

API_V1_PREFIX = "/api/v1"

api_router = APIRouter(prefix=API_V1_PREFIX)
api_router.include_router(health.router, prefix="/health", tags=[Tags.HEALTH])
api_router.include_router(datasets.router, prefix="/datasets", tags=[Tags.DATASETS])
api_router.include_router(jobs.router, prefix="/jobs", tags=[Tags.JOBS])
api_router.include_router(jobs.router, prefix="/experiments", tags=[Tags.EXPERIMENTS])
api_router.include_router(completions.router, prefix="/completions", tags=[Tags.COMPLETIONS])
