import contextlib

from fastapi import FastAPI
from sqlalchemy import Engine

from src.api.router import api_router
from src.api.tags import TAGS_METADATA
from src.db import BaseRecord, engine


def create_app(engine: Engine) -> FastAPI:
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        # TODO: Remove this once switching to Alembic for migrations
        BaseRecord.metadata.create_all(engine)
        yield

    app = FastAPI(title="Platform Backend", lifespan=lifespan, openapi_tags=TAGS_METADATA)
    app.include_router(api_router)
    return app


app = create_app(engine)
