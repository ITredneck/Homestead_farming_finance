"""Baseline: the farm table.

Revision ID: 0001
Revises:
Create Date: 2026-11-14
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "farm",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("uuid", sa.Uuid(), nullable=False),
        sa.Column("entered_by", sa.String(length=64), nullable=True),
        sa.Column("entered_via", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("uuid", name=op.f("uq_farm_uuid")),
        sa.CheckConstraint(
            "entered_via IN ('app', 'ai', 'system')", name=op.f("ck_farm_entered_via")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_farm")),
    )


def downgrade() -> None:
    op.drop_table("farm")
