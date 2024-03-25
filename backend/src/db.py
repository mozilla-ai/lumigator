import contextlib
from collections.abc import Iterator
from typing import Any

from loguru import logger
from sqlalchemy import Connection, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.models.base import BaseSQLModel
from src.settings import settings


class DatabaseSessionManager:
    """Connection/session manager for SQLAlchemy databases.

    The manager binds to a DB engine specified by the `SQLALCHEMY_DATABASE_URL` in the app settings.
    Connections and sessions can be obtained by the `connect` and `session` methods,
    which handles rollbacks in case of errors while the connections are open.
    """

    def __init__(self, host: str, engine_kwargs: dict[str, Any]):
        logger.info(f"Creating DB engine for {host}")
        self._engine = create_engine(host, **engine_kwargs)
        self._sessionmaker = sessionmaker(autocommit=False, bind=self._engine)

    def initialize(self):
        # TODO: This creates tables in the DB for all subclasses of BaseSQL
        # We will get rid of this when switching to Alembic for migrations
        BaseSQLModel.metadata.create_all(bind=self._engine)

    def close(self):
        self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.contextmanager
    def connect(self) -> Iterator[Connection]:
        with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise

    @contextlib.contextmanager
    def session(self) -> Iterator[Session]:
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


session_manager = DatabaseSessionManager(
    str(settings.SQLALCHEMY_DATABASE_URL),
    engine_kwargs={"echo": True},
)
