from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from homestead_finance.core.context import ReadSession, WriteSession
from homestead_finance.core.identity import IDENTITY_RESPONSES, CurrentActor, require_actor
from homestead_finance.spike import service
from homestead_finance.spike.schemas import SpikeEntryAck, SpikeEntryIn, SpikeSummary

router = APIRouter(
    prefix="/api/spike",
    tags=["spike"],
    dependencies=[Depends(require_actor)],
    responses=IDENTITY_RESPONSES,
)


@router.post(
    "/entries",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_200_OK: {"model": SpikeEntryAck, "description": "Already stored"}},
)
def post_entry(
    data: SpikeEntryIn, response: Response, session: WriteSession, actor: CurrentActor
) -> SpikeEntryAck:
    entry, created = service.record_entry(session, data, actor)
    if not created:
        response.status_code = status.HTTP_200_OK
    return SpikeEntryAck(
        uuid=entry.uuid,
        status="created" if created else "duplicate",
        received_count=entry.received_count,
    )


@router.get("/summary")
def get_summary(session: ReadSession) -> SpikeSummary:
    return service.summary(session)


@router.delete("/entries", status_code=status.HTTP_204_NO_CONTENT)
def delete_entries(session: WriteSession) -> None:
    service.reset(session)
