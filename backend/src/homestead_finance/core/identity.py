"""Who is calling: the Home Assistant user, from the headers ingress adds.

The Supervisor strips any incoming copies of these headers and sets its own, so they
can be trusted because only the ingress gateway may connect (see ``ingress.py``).
Name and display name are not guaranteed; only the user id is required.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Any, Final

from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel

from homestead_finance.core.context import AppSettings
from homestead_finance.core.provenance import Actor, EnteredVia

HEADER_USER_ID: Final = "x-remote-user-id"
HEADER_USER_NAME: Final = "x-remote-user-name"
HEADER_USER_DISPLAY_NAME: Final = "x-remote-user-display-name"
HEADER_INGRESS_PATH: Final = "x-ingress-path"


class ErrorDetail(BaseModel):
    detail: str


#: Documents (in OpenAPI) the 401 that every endpoint needing a user can return.
IDENTITY_RESPONSES: Final[dict[int | str, dict[str, Any]]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": ErrorDetail,
        "description": "No Home Assistant user on the request",
    },
}

#: Stands in for the HA user in dev mode when no identity headers are sent.
DEV_ACTOR: Final = Actor(
    user_id="dev-user", name="dev", display_name="Dev User", via=EnteredVia.APP
)


def actor_from_headers(headers: Mapping[str, str]) -> Actor | None:
    user_id = _clean(headers.get(HEADER_USER_ID))
    if user_id is None:
        return None
    return Actor(
        user_id=user_id,
        name=_clean(headers.get(HEADER_USER_NAME)),
        display_name=_clean(headers.get(HEADER_USER_DISPLAY_NAME)),
        via=EnteredVia.APP,
    )


def require_actor(request: Request, settings: AppSettings) -> Actor:
    actor = actor_from_headers(request.headers)
    if actor is not None:
        return actor
    if settings.dev_mode:
        return DEV_ACTOR
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No Home Assistant user on this request. Open the app from Home Assistant.",
    )


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


CurrentActor = Annotated[Actor, Depends(require_actor)]
