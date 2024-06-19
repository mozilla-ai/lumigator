from fastapi import APIRouter

from mzai.backend.api.routes import datasets, events, experiments, finetuning, health
from mzai.backend.api.tags import Tags

API_V1_PREFIX = "/api/v1"

api_router = APIRouter(prefix=API_V1_PREFIX)
api_router.include_router(health.router, prefix="/health", tags=[Tags.HEALTH])
api_router.include_router(datasets.router, prefix="/datasets", tags=[Tags.DATASETS])
api_router.include_router(finetuning.router, prefix="/finetuning", tags=[Tags.FINETUNING])
api_router.include_router(experiments.router, prefix="/experiments", tags=[Tags.EXPERIMENTS])
api_router.include_router(events.router, prefix="/events", tags=[Tags.EVENTS])
api_router.include_router(events.router, prefix="/ground-truth", tags=[Tags.EVENTS])
