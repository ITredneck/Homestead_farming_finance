from __future__ import annotations

from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from homestead_finance.core.db import Base
from homestead_finance.core.provenance import ProvenanceMixin
from homestead_finance.core.types import UTCDateTime


class SpikeEntry(ProvenanceMixin, Base):
    __tablename__ = "spike_entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    note: Mapped[str] = mapped_column(String(500), default="")
    client_created_at: Mapped[datetime] = mapped_column(UTCDateTime())
    #: How many times this UUID arrived; anything above 1 was a replayed duplicate.
    received_count: Mapped[int] = mapped_column(default=1)
