import contextlib
from collections.abc import Generator
from typing import Any

from sqlalchemy import JSON, Connection, Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from mzai.backend.settings import settings


class BaseRecord(DeclarativeBase):
    """Base class for declarative SQLAlchemy mappings.

    Commonly, these mappings are referred to as "models".
    However, "model" is an incredibly overloaded term on the platform,
    so we're using the term "record" instead to indicate that instances of these classes
    generally correspond to single records (i.e., rows) in a DB table.
    """

    # Additional mappings from Python type to SQLAlchemy type
    type_annotation_map = {dict[str, Any]: JSON}


class DatabaseSessionManager:
    """Connection/session manager for SQLAlchemy database engines.

    Connections and sessions are obtained by the `connect` and `session` methods,
    which establish SQL transactions and handles rollbacks in case of exceptions.
    """

    def __init__(self, engine: Engine):
        self._engine = engine
        self._sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    @contextlib.contextmanager
    def connect(self) -> Generator[Connection, None, None]:
        """Yield a transactional connection, rolling back on errors."""
        with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise

    @contextlib.contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Yield a transactional session, rolling back on errors."""
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, echo=True)
session_manager = DatabaseSessionManager(engine)
