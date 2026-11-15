"""Spike service: the only code that writes spike entries.

Callers pass a write session (BEGIN IMMEDIATE), so concurrent replays of the same
UUID are serialized: the second one sees the first one's row and counts a duplicate.
"""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from homestead_finance.core.provenance import Actor, stamp
from homestead_finance.spike.models import SpikeEntry
from homestead_finance.spike.schemas import SpikeEntryIn, SpikeEntryRead, SpikeSummary

RECENT_LIMIT = 20


def record_entry(session: Session, data: SpikeEntryIn, actor: Actor) -> tuple[SpikeEntry, bool]:
    """Store an entry once per UUID. Returns the entry and whether it was new."""
    existing = session.scalars(select(SpikeEntry).where(SpikeEntry.uuid == data.uuid)).first()
    if existing is not None:
        existing.received_count += 1
        session.commit()
        return existing, False
    entry = SpikeEntry(
        uuid=data.uuid,
        note=data.note,
        client_created_at=data.client_created_at,
        received_count=1,
    )
    stamp(entry, actor)
    session.add(entry)
    session.commit()
    return entry, True


def summary(session: Session) -> SpikeSummary:
    total = session.scalar(select(func.count()).select_from(SpikeEntry)) or 0
    duplicates = session.scalar(select(func.sum(SpikeEntry.received_count - 1))) or 0
    recent = session.scalars(
        select(SpikeEntry).order_by(SpikeEntry.id.desc()).limit(RECENT_LIMIT)
    ).all()
    return SpikeSummary(
        total=total,
        duplicates_received=duplicates,
        recent=[SpikeEntryRead.model_validate(entry) for entry in recent],
    )


def reset(session: Session) -> None:
    session.execute(delete(SpikeEntry))
    session.commit()
