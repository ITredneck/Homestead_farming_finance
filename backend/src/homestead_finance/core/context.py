"""Per-app state and the FastAPI dependencies that read it."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from homestead_finance.core.db import SessionFactories
from homestead_finance.core.settings import Settings


@dataclass(frozen=True)
class AppContext:
    """Everything the app sets up at startup."""

    settings: Settings
    engine: Engine
    sessions: SessionFactories
    database_check: str
    schema_revision: str | None


def get_settings(request: Request) -> Settings:
    settings: object = request.app.state.settings
    if not isinstance(settings, Settings):  # pragma: no cover - set by create_app
        msg = "settings missing from app state"
        raise TypeError(msg)
    return settings


def get_context(request: Request) -> AppContext:
    context: object = getattr(request.app.state, "context", None)
    if not isinstance(context, AppContext):  # pragma: no cover - set by the lifespan
        msg = "the app has not finished starting"
        raise TypeError(msg)
    return context


def read_session(request: Request) -> Iterator[Session]:
    with get_context(request).sessions.read() as session:
        yield session


def write_session(request: Request) -> Iterator[Session]:
    with get_context(request).sessions.write() as session:
        yield session


AppSettings = Annotated[Settings, Depends(get_settings)]
Context = Annotated[AppContext, Depends(get_context)]
ReadSession = Annotated[Session, Depends(read_session)]
WriteSession = Annotated[Session, Depends(write_session)]
