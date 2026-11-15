"""Farm service: the only code that writes farm rows."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from homestead_finance.core.provenance import SYSTEM_ACTOR, Actor, stamp
from homestead_finance.farm.models import Farm

#: Placeholder until first-run setup (#22) asks for the real name.
DEFAULT_FARM_NAME = "My homestead"


def get_farm(session: Session) -> Farm | None:
    return session.scalars(select(Farm).order_by(Farm.id).limit(1)).first()


def ensure_farm(session: Session, actor: Actor = SYSTEM_ACTOR) -> Farm:
    """Return the install's farm, creating it on first start. Safe to call repeatedly."""
    farm = get_farm(session)
    if farm is not None:
        return farm
    farm = Farm(name=DEFAULT_FARM_NAME)
    stamp(farm, actor)
    session.add(farm)
    session.commit()
    return farm
