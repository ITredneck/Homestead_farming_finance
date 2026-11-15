from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class SpikeEntryIn(BaseModel):
    uuid: UUID
    note: str = Field(default="", max_length=500)
    client_created_at: AwareDatetime


class SpikeEntryAck(BaseModel):
    uuid: UUID
    status: Literal["created", "duplicate"]
    received_count: int


class SpikeEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    note: str
    client_created_at: datetime
    created_at: datetime
    received_count: int
    entered_by: str | None


class SpikeSummary(BaseModel):
    total: int
    duplicates_received: int
    recent: list[SpikeEntryRead]
