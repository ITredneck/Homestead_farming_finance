from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from homestead_finance.core.context import ReadSession
from homestead_finance.core.identity import IDENTITY_RESPONSES, require_actor
from homestead_finance.farm import service
from homestead_finance.farm.schemas import FarmRead

router = APIRouter(
    prefix="/api/farm",
    tags=["farm"],
    dependencies=[Depends(require_actor)],
    responses=IDENTITY_RESPONSES,
)


@router.get("")
def read_farm(session: ReadSession) -> FarmRead:
    farm = service.get_farm(session)
    if farm is None:  # pragma: no cover - created at startup
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No farm yet")
    return FarmRead.model_validate(farm)
