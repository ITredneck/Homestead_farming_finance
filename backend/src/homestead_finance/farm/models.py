from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from homestead_finance.core.db import Base
from homestead_finance.core.provenance import ProvenanceMixin


class Farm(ProvenanceMixin, Base):
    __tablename__ = "farm"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
