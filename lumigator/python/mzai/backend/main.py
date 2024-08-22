import contextlib

from fastapi import FastAPI
from sqlalchemy import Engine

from mzai.backend.api.router import api_router
from mzai.backend.api.tags import TAGS_METADATA
from mzai.backend.db import engine
from mzai.backend.records.base import BaseRecord

from loguru import logger
import sys
import os


def create_app(engine: Engine) -> FastAPI:
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        # TODO: Remove this once switching to Alembic for migrations
        BaseRecord.metadata.create_all(engine)
        yield

    app = FastAPI(title="Lumigator Backend", lifespan=lifespan, openapi_tags=TAGS_METADATA)

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
