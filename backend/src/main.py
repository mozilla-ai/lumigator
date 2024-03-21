from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import api_router
from src.db import session_manager
from src.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await session_manager.initialize()
    yield
    await session_manager.close()


app = FastAPI(title="Platform Backend", lifepsan=lifespan)


app.include_router(api_router, prefix=settings.API_V1_STR)
