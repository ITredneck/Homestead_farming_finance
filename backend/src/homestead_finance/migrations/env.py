"""Alembic environment. The app passes an open connection in ``config.attributes``.

For local work you can also point the Alembic CLI at a database, e.g.
``uv run alembic -x url=sqlite:///.data/homestead_finance.db revision --autogenerate``.
"""

from __future__ import annotations

from alembic import context
from sqlalchemy.engine import Connection

from homestead_finance.core.db import create_db_engine
from homestead_finance.models import metadata as target_metadata


def _run(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,  # SQLite can't ALTER most things; batch mode rebuilds tables
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connection: Connection | None = context.config.attributes.get("connection")
    if connection is not None:
        _run(connection)
        return
    url = context.get_x_argument(as_dictionary=True).get("url")
    if not url:
        msg = "Pass a database URL with -x url=sqlite:///path/to/homestead_finance.db"
        raise SystemExit(msg)
    with create_db_engine(url).begin() as new_connection:
        _run(new_connection)


if context.is_offline_mode():
    msg = "Offline (SQL script) migrations are not supported."
    raise SystemExit(msg)
run_migrations_online()
