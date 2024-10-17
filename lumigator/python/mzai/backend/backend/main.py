import contextlib
import os
import sys

from fastapi import FastAPI
from loguru import logger
from sqlalchemy import Engine

from backend.api.router import api_router
from backend.api.tags import TAGS_METADATA
from backend.db import engine
from backend.records.base import BaseRecord

LUMIGATOR_APP_TAGS = {
    "title": "Lumigator Backend",
    "description": "Backend server",
    "version": "0.0.1",
    "openapi_tags": TAGS_METADATA,
}


def create_app(engine: Engine) -> FastAPI:
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        # TODO: Remove this once switching to Alembic for migrations
        BaseRecord.metadata.create_all(engine)
        yield

    app = FastAPI(**(LUMIGATOR_APP_TAGS | {"lifespan": lifespan}))

    main_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.remove()
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:"
            "<cyan>{function}</cyan>:"
            "<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level=main_log_level,
        colorize=True,
    )

    app.include_router(api_router)

    @app.get("/")
    def get_root():
        return {"Hello": "Lumigator!🐊"}

    return app


app = create_app(engine)
