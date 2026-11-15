"""THROWAWAY: table for the M1 offline spike (#12). Dropped again in M2 (#119).

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-14
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "spike_entry",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=False),
        sa.Column("client_created_at", sa.DateTime(), nullable=False),
        sa.Column("received_count", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.Uuid(), nullable=False),
        sa.Column("entered_by", sa.String(length=64), nullable=True),
        sa.Column("entered_via", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("uuid", name=op.f("uq_spike_entry_uuid")),
        sa.CheckConstraint(
            "entered_via IN ('app', 'ai', 'system')", name=op.f("ck_spike_entry_entered_via")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_spike_entry")),
    )


def downgrade() -> None:
    op.drop_table("spike_entry")
