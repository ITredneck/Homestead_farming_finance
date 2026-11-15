from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from homestead_finance.core.settings import Settings
from homestead_finance.main import create_app
from tests.support import GATEWAY


@pytest.fixture(autouse=True)
def _isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep the developer's HF_* variables and any real options.json out of tests."""
    for name in [name for name in os.environ if name.startswith("HF_")]:
        monkeypatch.delenv(name)
    monkeypatch.setenv("HF_OPTIONS_FILE", str(tmp_path / "no-options.json"))


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(data_dir=tmp_path / "data", version="1.2.3")


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """A client that connects from the ingress gateway's address."""
    with TestClient(app, client=GATEWAY) as test_client:
        yield test_client
