import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from loguru import logger

from backend.api.router import api_router
from backend.api.tags import TAGS_METADATA

LUMIGATOR_APP_TAGS = {
    "title": "Lumigator Backend",
    "description": "Backend server",
    "version": "0.0.1",
    "openapi_tags": TAGS_METADATA,
}


def _init_db():
    logger.info("Initializing database via Alembic")
    backend_root = Path(Path(Path(__file__).resolve()).parent).parent
    alembic_cfg = Config(str(backend_root / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")


def _configure_logger():
    main_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.remove()
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:"
            "<cyan>{function}</cyan>:"
            "<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level=main_log_level,
        colorize=True,
    )

def create_app() -> FastAPI:
    _configure_logger()

    _init_db()

    app = FastAPI(**LUMIGATOR_APP_TAGS)

    app.include_router(api_router)

    @app.get("/")
    def get_root():
        return {"Hello": "Lumigator!🐊"}

    return app

app = create_app()
