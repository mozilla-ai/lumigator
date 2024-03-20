from fastapi import FastAPI

from src.api import api_router
from src.settings import settings

app = FastAPI(title="MZAI Platform")


app.include_router(api_router, prefix=settings.API_V1_STR)
