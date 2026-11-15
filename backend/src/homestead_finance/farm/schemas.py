from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from homestead_finance.core.provenance import EnteredVia


class FarmRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str
    created_at: datetime
    entered_by: str | None
    entered_via: EnteredVia
