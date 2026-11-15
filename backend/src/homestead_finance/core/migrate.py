"""Runs the Alembic migrations that ship inside the package."""

from __future__ import annotations

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Engine

from homestead_finance.core.db import BEGIN_MODE_OPTION

SCRIPT_LOCATION = "homestead_finance:migrations"


def alembic_config() -> Config:
    config = Config()
    config.set_main_option("script_location", SCRIPT_LOCATION)
    return config


def upgrade(engine: Engine, revision: str = "head") -> None:
    _run(engine, "upgrade", revision)


def downgrade(engine: Engine, revision: str) -> None:
    _run(engine, "downgrade", revision)


def current_revision(engine: Engine) -> str | None:
    with engine.connect() as connection:
        return MigrationContext.configure(connection).get_current_revision()


def _run(engine: Engine, direction: str, revision: str) -> None:
    config = alembic_config()
    writer = engine.execution_options(**{BEGIN_MODE_OPTION: "IMMEDIATE"})
    with writer.begin() as connection:
        config.attributes["connection"] = connection
        if direction == "upgrade":
            command.upgrade(config, revision)
        else:
            command.downgrade(config, revision)
