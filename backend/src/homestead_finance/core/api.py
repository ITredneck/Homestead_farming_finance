"""System endpoints: health and the current user."""

from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

from homestead_finance.core.context import Context
from homestead_finance.core.identity import HEADER_INGRESS_PATH, IDENTITY_RESPONSES, CurrentActor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["system"])


class Health(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    schema_revision: str | None
    database: str


class Me(BaseModel):
    user_id: str | None
    name: str | None
    display_name: str | None
    ingress_path: str | None


@router.get("/health")
def health(context: Context) -> Health:
    """Liveness and database state. Used by the Supervisor watchdog; needs no user."""
    return Health(
        status="ok" if context.database_check == "ok" else "degraded",
        version=context.settings.version,
        schema_revision=context.schema_revision,
        database=context.database_check,
    )


@router.get("/me", responses=IDENTITY_RESPONSES)
def me(request: Request, actor: CurrentActor) -> Me:
    """The Home Assistant user making this request."""
    # Header names only, never values: confirms what ingress sends on a real install.
    logger.debug("Request header names: %s", ", ".join(sorted(request.headers.keys())))
    return Me(
        user_id=actor.user_id,
        name=actor.name,
        display_name=actor.display_name,
        ingress_path=request.headers.get(HEADER_INGRESS_PATH),
    )
