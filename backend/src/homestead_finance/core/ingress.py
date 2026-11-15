"""Only the Home Assistant ingress gateway may talk to the app.

The check uses the direct TCP peer address. Uvicorn runs without proxy headers, so a
forged ``X-Forwarded-For`` cannot change it.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from ipaddress import IPv4Network, IPv6Address, IPv6Network, ip_address, ip_network

from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class IngressGatewayMiddleware:
    def __init__(self, app: ASGIApp, trusted: Iterable[str], *, enabled: bool = True) -> None:
        self.app = app
        self.enabled = enabled
        self.networks: tuple[IPv4Network | IPv6Network, ...] = tuple(
            ip_network(entry, strict=False) for entry in trusted
        )

    def is_trusted(self, host: str | None) -> bool:
        if host is None:
            return False
        try:
            address = ip_address(host)
        except ValueError:
            return False
        if isinstance(address, IPv6Address) and address.ipv4_mapped is not None:
            address = address.ipv4_mapped
        return any(address in network for network in self.networks)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self.enabled or scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return
        client: tuple[str, int] | None = scope.get("client")
        host = client[0] if client else None
        if self.is_trusted(host):
            await self.app(scope, receive, send)
            return
        logger.warning("Rejected a connection from %s: only the ingress gateway may connect", host)
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1008})
            return
        response = PlainTextResponse("Forbidden: open the app from Home Assistant.", 403)
        await response(scope, receive, send)
