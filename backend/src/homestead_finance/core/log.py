"""Logging setup, mapping the app's log_level option onto Python and uvicorn levels."""

from __future__ import annotations

import logging

from homestead_finance.core.settings import LogLevel

LOGGER_NAME = "homestead_finance"

_PYTHON_LEVELS: dict[LogLevel, int] = {
    "trace": logging.DEBUG,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "notice": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "fatal": logging.CRITICAL,
}

_UVICORN_LEVELS: dict[LogLevel, str] = {
    "trace": "trace",
    "debug": "debug",
    "info": "info",
    "notice": "info",
    "warning": "warning",
    "error": "error",
    "fatal": "critical",
}


def configure_logging(level: LogLevel) -> None:
    """Send app logs to stderr at the configured level (no-op if logging is set up)."""
    logging.basicConfig(format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    logging.getLogger(LOGGER_NAME).setLevel(_PYTHON_LEVELS[level])


def uvicorn_log_level(level: LogLevel) -> str:
    return _UVICORN_LEVELS[level]
