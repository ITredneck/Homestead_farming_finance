"""Who entered a record and how: shared by every table.

M2 (#20) builds the shared idempotent-create helper on top of this.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Enum, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from homestead_finance.core.types import UTCDateTime, utcnow


class EnteredVia(StrEnum):
    APP = "app"
    AI = "ai"
    SYSTEM = "system"


@dataclass(frozen=True, slots=True)
class Actor:
    """Who is making a change, and through which channel.

    ``user_id`` is the Home Assistant user id. Records store the id rather than the
    name, because names can change (showing names is #120).
    """

    user_id: str | None
    name: str | None
    display_name: str | None
    via: EnteredVia


SYSTEM_ACTOR = Actor(
    user_id=None, name=None, display_name="Homestead Finance", via=EnteredVia.SYSTEM
)

_ENTERED_VIA_VALUES = ", ".join(f"'{member.value}'" for member in EnteredVia)


def _enum_values(members: type[EnteredVia]) -> list[str]:
    """Store enum values ("app"), not member names ("APP")."""
    return [member.value for member in members]


class ProvenanceMixin:
    """Columns every record carries: a client UUID plus who, how and when."""

    uuid: Mapped[UUID] = mapped_column(Uuid(), unique=True, default=uuid4)
    entered_by: Mapped[str | None] = mapped_column(String(64))
    entered_via: Mapped[EnteredVia] = mapped_column(
        Enum(
            EnteredVia,
            native_enum=False,
            create_constraint=False,
            length=16,
            values_callable=_enum_values,
        ),
        CheckConstraint(f"entered_via IN ({_ENTERED_VIA_VALUES})", name="entered_via"),
    )
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)


def stamp(record: ProvenanceMixin, actor: Actor) -> None:
    """Record who is creating ``record`` and how."""
    record.entered_by = actor.user_id
    record.entered_via = actor.via
