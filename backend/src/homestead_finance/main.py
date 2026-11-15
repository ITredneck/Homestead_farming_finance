"""The FastAPI app factory."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import APIRoute

from homestead_finance.core import migrate
from homestead_finance.core.api import router as system_router
from homestead_finance.core.context import AppContext
from homestead_finance.core.db import create_db_engine, create_session_factories, quick_check
from homestead_finance.core.ingress import IngressGatewayMiddleware
from homestead_finance.core.log import configure_logging
from homestead_finance.core.settings import Settings
from homestead_finance.core.static import SPAStaticFiles
from homestead_finance.farm.router import router as farm_router
from homestead_finance.farm.service import ensure_farm
from homestead_finance.spike.router import router as spike_router

logger = logging.getLogger(__name__)

#: OpenAPI document version. Fixed so the generated client only changes with the API;
#: the app's release version is reported by /api/health instead.
API_VERSION = "1"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        context = start(settings)
        app.state.context = context
        try:
            yield
        finally:
            context.engine.dispose()

    app = FastAPI(
        title="Homestead Finance",
        version=API_VERSION,
        lifespan=lifespan,
        openapi_url="/api/openapi.json",
        # The docs page loads the schema from an absolute URL, which breaks under ingress.
        docs_url="/api/docs" if settings.dev_mode else None,
        redoc_url=None,
        generate_unique_id_function=_operation_id,
    )
    app.state.settings = settings
    app.add_middleware(
        IngressGatewayMiddleware, trusted=settings.trusted_proxies, enabled=not settings.dev_mode
    )
    app.include_router(system_router)
    app.include_router(farm_router)
    app.include_router(spike_router)
    if settings.static_dir is not None and settings.static_dir.is_dir():
        app.mount("/", SPAStaticFiles(directory=settings.static_dir), name="frontend")
    elif settings.static_dir is not None:
        logger.warning("Frontend folder %s not found; serving the API only", settings.static_dir)
    return app


def start(settings: Settings) -> AppContext:
    """Open the database, check it, migrate it and make sure the farm row exists."""
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    engine = create_db_engine(settings.database_url)
    database_check = quick_check(engine)
    if database_check != "ok":
        logger.error("Database integrity check failed: %s", database_check)
    migrate.upgrade(engine)
    schema_revision = migrate.current_revision(engine)
    sessions = create_session_factories(engine)
    with sessions.write() as session:
        ensure_farm(session)
    logger.info(
        "Homestead Finance %s started (schema %s, database %s)",
        settings.version,
        schema_revision,
        database_check,
    )
    return AppContext(
        settings=settings,
        engine=engine,
        sessions=sessions,
        database_check=database_check,
        schema_revision=schema_revision,
    )


def _operation_id(route: APIRoute) -> str:
    tag = str(route.tags[0]) if route.tags else "api"
    return f"{tag}_{route.name}"
