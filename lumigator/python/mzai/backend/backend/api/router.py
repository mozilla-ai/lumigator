from fastapi import APIRouter

from backend.api.routes import (
    completions,
    datasets,
    experiments,
    experiments_new,
    health,
    jobs,
    models,
)
from backend.api.tags import Tags

API_V1_PREFIX = "/api/v1"

api_router = APIRouter(prefix=API_V1_PREFIX)
api_router.include_router(health.router, prefix="/health", tags=[Tags.HEALTH])
api_router.include_router(datasets.router, prefix="/datasets", tags=[Tags.DATASETS])
api_router.include_router(jobs.router, prefix="/jobs", tags=[Tags.JOBS])
api_router.include_router(experiments.router, prefix="/experiments", tags=[Tags.EXPERIMENTS])
api_router.include_router(completions.router, prefix="/completions", tags=[Tags.COMPLETIONS])
api_router.include_router(models.router, prefix="/models", tags=[Tags.MODELS])
api_router.include_router(
    experiments_new.router, prefix="/experiments_new", tags=[Tags.EXPERIMENTS_NEW]
)
