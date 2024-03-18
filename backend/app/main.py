from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api import api_router
from app.core.db import init_db, session_manager
from app.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await session_manager.close()


app = FastAPI(title="MZAI Platform", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Welcome to the MZAI Platform!"}


app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
