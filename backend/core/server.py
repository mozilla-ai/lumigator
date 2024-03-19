from fastapi import FastAPI

from api import api_router
from core.settings import settings

app = FastAPI(title="MZAI Platform")


@app.get("/")
async def root():
    return {"message": "Welcome to the MZAI Platform!"}


app.include_router(api_router, prefix=settings.API_V1_STR)
