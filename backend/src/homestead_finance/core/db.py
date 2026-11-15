"""SQLite engine, sessions and the declarative base.

SQLAlchemy emits BEGIN itself instead of the sqlite3 driver (the documented SQLite
recipe), so transactions, SAVEPOINTs and DDL behave correctly. Write sessions use
``BEGIN IMMEDIATE``: in WAL mode a read-then-write transaction that started as
DEFERRED can fail at once with "database is locked", while IMMEDIATE takes the
write lock up front and waits for it (``busy_timeout``).
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Final, Literal

from sqlalchemy import URL, Engine, MetaData, create_engine, event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry

NAMING_CONVENTION: Final = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


#: Execution option read by the BEGIN hook.
BEGIN_MODE_OPTION: Final = "homestead_begin_mode"
BeginMode = Literal["DEFERRED", "IMMEDIATE"]
_BEGIN_STATEMENTS: Final[dict[BeginMode, str]] = {
    "DEFERRED": "BEGIN DEFERRED",
    "IMMEDIATE": "BEGIN IMMEDIATE",
}

#: Applied to every new connection. synchronous=FULL: an entry the server has
#: acknowledged is gone from the client's outbox, so it must survive a power cut.
PRAGMAS: Final = (
    "PRAGMA journal_mode=WAL",
    "PRAGMA synchronous=FULL",
    "PRAGMA foreign_keys=ON",
    "PRAGMA busy_timeout=5000",
)


def create_db_engine(url: URL | str) -> Engine:
    # Legacy transaction control is what the BEGIN hook below relies on
    # (sqlite3's default through Python 3.15). Revisit for Python 3.16.
    engine = create_engine(url, connect_args={"autocommit": sqlite3.LEGACY_TRANSACTION_CONTROL})
    event.listen(engine, "connect", _on_connect)
    event.listen(engine, "begin", _on_begin)
    return engine


def _on_connect(dbapi_connection: sqlite3.Connection, _record: ConnectionPoolEntry) -> None:
    # Stop sqlite3 from emitting BEGIN; SQLAlchemy does it in _on_begin.
    dbapi_connection.isolation_level = None
    cursor = dbapi_connection.cursor()
    try:
        for pragma in PRAGMAS:
            cursor.execute(pragma)
    finally:
        cursor.close()


def _on_begin(connection: Connection) -> None:
    mode: BeginMode = connection.get_execution_options().get(BEGIN_MODE_OPTION, "DEFERRED")
    connection.exec_driver_sql(_BEGIN_STATEMENTS[mode])


@dataclass(frozen=True)
class SessionFactories:
    """Read sessions start DEFERRED transactions; write sessions start IMMEDIATE ones."""

    read: sessionmaker[Session]
    write: sessionmaker[Session]


def create_session_factories(engine: Engine) -> SessionFactories:
    writer = engine.execution_options(**{BEGIN_MODE_OPTION: "IMMEDIATE"})
    return SessionFactories(
        read=sessionmaker(engine, expire_on_commit=False),
        write=sessionmaker(writer, expire_on_commit=False),
    )


def quick_check(engine: Engine) -> str:
    """Run ``PRAGMA quick_check``; returns "ok" or the problems SQLite reports."""
    with engine.connect() as connection:
        rows = [str(row) for row in connection.exec_driver_sql("PRAGMA quick_check").scalars()]
    return "ok" if rows == ["ok"] else "; ".join(rows)
