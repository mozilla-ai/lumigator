import contextlib

from fastapi import FastAPI
from loguru import logger
from sqlalchemy import Engine

from mzai.backend.api.router import api_router
from mzai.backend.api.tags import TAGS_METADATA
from mzai.backend.db import BaseRecord, engine
from mzai.backend.settings import settings


def create_app(engine: Engine) -> FastAPI:
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info(f"Starting platform backend with settings: {settings.model_dump()}")
        # TODO: Remove this once switching to Alembic for migrations
        BaseRecord.metadata.create_all(engine)
        yield

    app = FastAPI(title="Platform Backend", lifespan=lifespan, openapi_tags=TAGS_METADATA)
    app.include_router(api_router)
    return app


app = create_app(engine)
