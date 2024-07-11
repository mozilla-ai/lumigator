import contextlib

from fastapi import FastAPI
from sqlalchemy import Engine

from mzai.backend.api.router import api_router
from mzai.backend.api.tags import TAGS_METADATA
from mzai.backend.db import engine
from mzai.backend.records.base import BaseRecord


def create_app(engine: Engine) -> FastAPI:
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        # TODO: Remove this once switching to Alembic for migrations
        BaseRecord.metadata.create_all(engine)
        yield

<<<<<<< HEAD
    app = FastAPI(title="Lumigator Backend", lifespan=lifespan, openapi_tags=TAGS_METADATA)
=======
    app = FastAPI(title="lumigator Backend", lifespan=lifespan, openapi_tags=TAGS_METADATA)
>>>>>>> 3748955 (renaming to Lumigator)
    app.include_router(api_router)
    return app


app = create_app(engine)
