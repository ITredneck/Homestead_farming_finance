from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import Engine, select, text
from sqlalchemy.exc import IntegrityError, StatementError

from homestead_finance.core import migrate
from homestead_finance.core.db import create_db_engine, create_session_factories, quick_check
from homestead_finance.core.provenance import SYSTEM_ACTOR, stamp
from homestead_finance.farm.models import Farm


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture
def engine(db_path: Path) -> Iterator[Engine]:
    engine = create_db_engine(f"sqlite:///{db_path.as_posix()}")
    migrate.upgrade(engine)
    yield engine
    engine.dispose()


def new_farm(name: str) -> Farm:
    farm = Farm(name=name)
    stamp(farm, SYSTEM_ACTOR)
    return farm


def test_pragmas_are_set_on_every_connection(engine: Engine) -> None:
    with engine.connect() as connection:
        values = {
            pragma: connection.exec_driver_sql(f"PRAGMA {pragma}").scalar()
            for pragma in ("journal_mode", "synchronous", "foreign_keys", "busy_timeout")
        }

    assert values == {
        "journal_mode": "wal",
        "synchronous": 2,
        "foreign_keys": 1,
        "busy_timeout": 5000,
    }


def test_rollback_discards_changes(engine: Engine) -> None:
    sessions = create_session_factories(engine)
    with sessions.write() as session:
        session.add(new_farm("Kept"))
        session.commit()
        session.add(new_farm("Discarded"))
        session.flush()
        session.rollback()

    with sessions.read() as session:
        assert session.scalars(select(Farm.name)).all() == ["Kept"]


def test_savepoint_rolls_back_inside_a_transaction(engine: Engine) -> None:
    sessions = create_session_factories(engine)
    with sessions.write() as session:
        session.add(new_farm("Outer"))
        nested = session.begin_nested()
        session.add(new_farm("Inner"))
        session.flush()
        nested.rollback()
        session.commit()

    with sessions.read() as session:
        assert session.scalars(select(Farm.name)).all() == ["Outer"]


def test_write_sessions_take_the_write_lock_up_front(engine: Engine, db_path: Path) -> None:
    sessions = create_session_factories(engine)
    with sessions.write() as session:
        session.execute(text("SELECT 1"))  # starts the transaction: BEGIN IMMEDIATE

        other = sqlite3.connect(db_path, timeout=0, isolation_level=None)
        try:
            with pytest.raises(sqlite3.OperationalError, match="locked"):
                other.execute("BEGIN IMMEDIATE")
        finally:
            other.close()


def test_read_sessions_do_not_block_writers(engine: Engine, db_path: Path) -> None:
    sessions = create_session_factories(engine)
    with sessions.read() as session:
        session.execute(text("SELECT 1"))  # BEGIN DEFERRED: no write lock

        other = sqlite3.connect(db_path, timeout=0, isolation_level=None)
        try:
            other.execute("BEGIN IMMEDIATE")
            other.execute("ROLLBACK")
        finally:
            other.close()


def test_datetimes_round_trip_as_utc(engine: Engine) -> None:
    sessions = create_session_factories(engine)
    local = datetime(2026, 5, 1, 9, 30, tzinfo=timezone(timedelta(hours=-5)))
    with sessions.write() as session:
        farm = new_farm("Clock")
        farm.created_at = local
        session.add(farm)
        session.commit()

    with sessions.read() as session:
        stored = session.scalars(select(Farm.created_at)).one()

    assert stored == local
    assert stored.tzinfo == UTC


def test_naive_datetimes_are_rejected(engine: Engine) -> None:
    sessions = create_session_factories(engine)
    with sessions.write() as session:
        farm = new_farm("Naive")
        farm.created_at = datetime(2026, 5, 1, 9, 30)  # noqa: DTZ001
        session.add(farm)
        with pytest.raises(StatementError, match="naive datetimes"):
            session.commit()


def test_entered_via_is_checked_by_the_database(engine: Engine) -> None:
    with engine.connect() as connection, pytest.raises(IntegrityError, match="CHECK constraint"):
        connection.exec_driver_sql(
            "INSERT INTO farm (name, uuid, entered_via, created_at, updated_at) "
            "VALUES ('x', 'abc', 'phone', '2026-01-01', '2026-01-01')"
        )


def test_quick_check_reports_ok(engine: Engine) -> None:
    assert quick_check(engine) == "ok"
