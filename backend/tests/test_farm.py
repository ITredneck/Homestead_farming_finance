from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from homestead_finance.core.settings import Settings
from homestead_finance.farm.models import Farm
from homestead_finance.main import create_app, start
from tests.support import GATEWAY, USER_HEADERS


def test_first_start_creates_one_system_farm(client: TestClient) -> None:
    farm = client.get("/api/farm", headers=USER_HEADERS).json()

    assert farm["name"] == "My homestead"
    assert farm["entered_via"] == "system"
    assert farm["entered_by"] is None


def test_farm_survives_restarts(settings: Settings) -> None:
    with TestClient(create_app(settings), client=GATEWAY) as first:
        before = first.get("/api/farm", headers=USER_HEADERS).json()
    with TestClient(create_app(settings), client=GATEWAY) as second:
        after = second.get("/api/farm", headers=USER_HEADERS).json()

    assert after == before


def test_starting_twice_keeps_a_single_farm(settings: Settings) -> None:
    start(settings).engine.dispose()
    context = start(settings)
    with context.sessions.read() as session:
        count = session.scalar(select(func.count()).select_from(Farm))
    context.engine.dispose()

    assert count == 1


def test_farm_needs_a_user(client: TestClient) -> None:
    assert client.get("/api/farm").status_code == 401
