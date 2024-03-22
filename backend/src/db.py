import contextlib
from collections.abc import AsyncIterator
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.settings import settings


class BaseSQL(DeclarativeBase):
    pass


class DatabaseSessionManager:
    """Connection/session manager for SQLAlchemy databases.

    The manager binds to a DB engine specified by the `SQLALCHEMY_DATABASE_URL` in the app settings.
    Async connections and sessions can be obtained by the `connect` and `session` methods,
    which handles rollbacks in case of errors while the connections are open.
    """

    def __init__(self, host: str, engine_kwargs: dict[str, Any]):
        logger.info(f"Creating DB engine for {host}")
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def initialize(self):
        async with self.connect() as connection:
            # TODO: This creates tables in the DB for all subclasses of BaseSQL
            # We will get rid of this when switching to Alembic for migrations
            await connection.run_sync(BaseSQL.metadata.create_all)

    async def close(self):
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


session_manager = DatabaseSessionManager(
    str(settings.SQLALCHEMY_DATABASE_URL),
    engine_kwargs={"echo": True},
)
