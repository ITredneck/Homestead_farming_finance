"""Run the app: ``python -m homestead_finance [--dev] [--reload]``."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import uvicorn

from homestead_finance.core.log import uvicorn_log_level
from homestead_finance.core.settings import Settings


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m homestead_finance")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="local development: no gateway check, a stub user, data in ./.data, localhost only",
    )
    parser.add_argument("--reload", action="store_true", help="restart when code changes")
    parser.add_argument("--host", help="address to listen on")
    parser.add_argument("--port", type=int, help="port to listen on")
    args = parser.parse_args(argv)

    if args.dev:
        # Environment variables, so the reloader's worker process sees them too.
        os.environ.setdefault("HF_DEV_MODE", "true")
        os.environ.setdefault("HF_DATA_DIR", str(Path.cwd() / ".data"))
    settings = Settings()
    host = args.host or ("127.0.0.1" if settings.dev_mode else settings.host)

    uvicorn.run(
        "homestead_finance.main:create_app",
        factory=True,
        host=host,
        port=args.port or settings.port,
        reload=args.reload,
        # The gateway check must see the real peer address, never X-Forwarded-For.
        proxy_headers=False,
        server_header=False,
        log_level=uvicorn_log_level(settings.log_level),
    )


if __name__ == "__main__":
    main()
