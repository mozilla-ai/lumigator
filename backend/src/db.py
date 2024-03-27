import contextlib
from collections.abc import Iterator

from sqlalchemy import Connection, Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.settings import settings


class BaseRecord(DeclarativeBase):
    pass


class DatabaseSessionManager:
    """Connection/session manager for SQLAlchemy database engines.

    Connections and sessions are obtained by the `connect` and `session` methods,
    which establish SQL transactions and handles rollbacks in case of exceptions.
    """

    def __init__(self, engine: Engine):
        self._engine = engine
        self._sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    @contextlib.contextmanager
    def connect(self) -> Iterator[Connection]:
        """Yield a transactional connection, rolling back on errors."""
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


engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, echo=True)
session_manager = DatabaseSessionManager(engine)
