"""Serves the built frontend.

``index.html`` is served at the root and revalidated on every load; hashed files in
``assets/`` are cached for a year. Directory URLs return 404 instead of redirecting,
because a redirect would use an absolute URL, which breaks under the ingress path.
"""

from __future__ import annotations

from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

ASSET_CACHE = "public, max-age=31536000, immutable"
PAGE_CACHE = "no-cache"


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        relative = path.replace("\\", "/")
        if relative in ("", "."):
            relative = path = "index.html"
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = (
            ASSET_CACHE if relative.startswith("assets/") else PAGE_CACHE
        )
        return response
