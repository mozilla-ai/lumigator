from contextlib import asynccontextmanager

import uvicorn
from app.core.db import initialize_db, session_manager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_db()
    yield
    await session_manager.close()


app = FastAPI(title="MZAI Platform", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Welcome to the MZAI Platform!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
