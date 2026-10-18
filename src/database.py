import sqlite3
from collections.abc import Sequence

from sqlalchemy import Connection, Select, create_engine, event, exc
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry

from src import settings
from src.exceptions import AlreadyExists

# Default pool (QueuePool): every session gets its own SQLite connection.
# Never StaticPool here: it shares one connection between all request
# threads, and concurrent requests then crash the process.
engine = create_engine(
    settings.app.database_url,
    echo=settings.app.debug,  # log SQL only in debug
    # Pooled connections move between threads, one session at a time
    connect_args={"check_same_thread": False},
)


# SQLite allows one writer at a time. A default (deferred) transaction takes
# the write lock only at its first write and fails at once with "database is
# locked" if another writer holds it. BEGIN IMMEDIATE takes the lock up front,
# so concurrent writers wait for it (up to the connection timeout, 5 s).
# Recipe: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
# WAL makes each commit short (no rewrite of the main file), so under load the
# waiters get the lock within that timeout. Measured in issue #29 / the PR.
@event.listens_for(engine, "connect")
def _configure_sqlite(
    dbapi_connection: sqlite3.Connection, _record: ConnectionPoolEntry
) -> None:
    dbapi_connection.isolation_level = None  # we emit BEGIN ourselves
    dbapi_connection.execute("PRAGMA journal_mode=WAL")


@event.listens_for(engine, "begin")
def _begin_immediate(conn: Connection) -> None:
    conn.exec_driver_sql("BEGIN IMMEDIATE")


SessionLocal = sessionmaker(bind=engine, autoflush=False)


def create_session() -> Session:
    return SessionLocal()


def fetch_one[T](stmt: Select[T]) -> T | None:
    with create_session() as session:
        item = session.scalars(stmt).first()
    return item


def fetch_all[T](stmt: Select[T]) -> Sequence[T]:
    with create_session() as session:
        items = session.scalars(stmt).all()
    return items


def upd_one[T](item: T) -> T:
    with create_session() as session:
        try:
            session.add(item)
            session.commit()
            session.refresh(item)
        except exc.IntegrityError:
            session.rollback()
            raise AlreadyExists

    return item
