from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from arsis.core.config import get_settings


def create_database_engine() -> Engine:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False, "timeout": 30},
        pool_pre_ping=True,
    )

    @event.listens_for(engine, "connect")
    def configure_sqlite(
        dbapi_connection: Any,
        _connection_record: Any,
    ) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    return engine


@lru_cache
def get_database_engine() -> Engine:
    """Return the process-wide SQLAlchemy engine."""

    return create_database_engine()


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_database_engine(),
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )


def get_database_session() -> Iterator[Session]:
    """Yield a request session without committing service transactions implicitly."""

    with get_session_factory()() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            if session.in_transaction():
                session.rollback()


@contextmanager
def transaction(session: Session) -> Iterator[Session]:
    """Delimit a service transaction; nested implicit transactions are rejected."""

    if session.in_transaction():
        raise RuntimeError("La sessione ha già una transazione attiva")
    with session.begin():
        yield session


def dispose_database_engine() -> None:
    """Close pooled connections, notably before replacing the database file."""

    if get_database_engine.cache_info().currsize:
        get_database_engine().dispose()
    get_session_factory.cache_clear()
    get_database_engine.cache_clear()


def database_is_ready(engine: Engine) -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:  # pragma: no cover - driver errors vary
        return False
