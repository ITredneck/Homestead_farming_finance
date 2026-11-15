from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Engine, inspect

from homestead_finance.core import migrate
from homestead_finance.core.db import create_db_engine
from homestead_finance.models import metadata


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    engine = create_db_engine(f"sqlite:///{(tmp_path / 'migrations.db').as_posix()}")
    yield engine
    engine.dispose()


def tables(engine: Engine) -> set[str]:
    return set(inspect(engine).get_table_names()) - {"alembic_version"}


def test_upgrade_creates_every_table(engine: Engine) -> None:
    migrate.upgrade(engine)

    assert tables(engine) == set(metadata.tables)
    assert migrate.current_revision(engine) == "0002"


def test_downgrade_then_upgrade_again(engine: Engine) -> None:
    migrate.upgrade(engine)
    migrate.downgrade(engine, "base")
    assert tables(engine) == set()

    migrate.upgrade(engine)
    assert tables(engine) == set(metadata.tables)


def test_models_match_the_migrations(engine: Engine) -> None:
    migrate.upgrade(engine)

    with engine.connect() as connection:
        context = MigrationContext.configure(connection, opts={"compare_type": True})
        differences = compare_metadata(context, metadata)

    assert differences == []
