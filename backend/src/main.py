from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.router import api_router
from src.db import session_manager
from src.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    session_manager.initialize()
    yield
    session_manager.close()


app = FastAPI(title="Platform Backend", lifespan=lifespan)


app.include_router(api_router, prefix=settings.API_V1_STR)
