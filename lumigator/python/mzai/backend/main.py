import contextlib
import logging

from fastapi import FastAPI
from sqlalchemy import Engine

from mzai.backend.api.router import api_router
from mzai.backend.api.tags import TAGS_METADATA
from mzai.backend.db import engine
from mzai.backend.records.base import BaseRecord
import logging
import sys


def create_app(engine: Engine) -> FastAPI:
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        # TODO: Remove this once switching to Alembic for migrations
        BaseRecord.metadata.create_all(engine)
        yield

    app = FastAPI(title="Lumigator Backend", lifespan=lifespan, openapi_tags=TAGS_METADATA)

    # TODO: Replace with more robust logging strategy
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    format = "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"  # noqa
    log_formatter = logging.Formatter(format)
    stream_handler.setFormatter(log_formatter)
    root_logger.addHandler(stream_handler)
    logger = logging.getLogger(__name__)
    logger.info("API is starting up")

    app.include_router(api_router)

    return app


app = create_app(engine)
