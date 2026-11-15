from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from hypothesis import HealthCheck, given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st

from tests.support import USER_HEADERS


def entry(uuid: UUID, note: str = "") -> dict[str, str]:
    return {
        "uuid": str(uuid),
        "note": note,
        "client_created_at": datetime(2026, 11, 14, 8, 0, tzinfo=UTC).isoformat(),
    }


def post(client: TestClient, uuid: UUID, note: str = "") -> tuple[int, dict[str, object]]:
    response = client.post("/api/spike/entries", json=entry(uuid, note), headers=USER_HEADERS)
    return response.status_code, response.json()


def test_new_entry_is_created(client: TestClient) -> None:
    uuid = uuid4()

    status, body = post(client, uuid, "eggs")

    assert status == 201
    assert body == {"uuid": str(uuid), "status": "created", "received_count": 1}


def test_replayed_entry_is_stored_once(client: TestClient) -> None:
    uuid = uuid4()
    post(client, uuid)

    status, body = post(client, uuid)

    assert status == 200
    assert body["status"] == "duplicate"
    assert body["received_count"] == 2
    summary = client.get("/api/spike/summary", headers=USER_HEADERS).json()
    assert summary["total"] == 1
    assert summary["duplicates_received"] == 1


def test_entered_by_is_filled_from_the_identity(client: TestClient) -> None:
    post(client, uuid4())

    recent = client.get("/api/spike/summary", headers=USER_HEADERS).json()["recent"]

    assert recent[0]["entered_by"] == USER_HEADERS["X-Remote-User-Id"]


def test_entries_need_a_timezone(client: TestClient) -> None:
    body = {**entry(uuid4()), "client_created_at": "2026-11-14T08:00:00"}

    response = client.post("/api/spike/entries", json=body, headers=USER_HEADERS)

    assert response.status_code == 422


def test_entries_need_a_user(client: TestClient) -> None:
    assert client.post("/api/spike/entries", json=entry(uuid4())).status_code == 401


def test_reset_removes_everything(client: TestClient) -> None:
    post(client, uuid4())

    assert client.delete("/api/spike/entries", headers=USER_HEADERS).status_code == 204
    assert client.get("/api/spike/summary", headers=USER_HEADERS).json()["total"] == 0


def test_concurrent_replays_of_one_entry_store_it_once(client: TestClient) -> None:
    uuid = uuid4()

    with ThreadPoolExecutor(max_workers=8) as pool:
        statuses = list(pool.map(lambda _: post(client, uuid)[0], range(16)))

    assert sorted(statuses) == [200] * 15 + [201]
    summary = client.get("/api/spike/summary", headers=USER_HEADERS).json()
    assert summary["total"] == 1
    assert summary["duplicates_received"] == 15


@hypothesis_settings(
    max_examples=25, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(st.lists(st.integers(min_value=0, max_value=5), min_size=1, max_size=20))
def test_any_replay_order_stores_each_entry_exactly_once(
    client: TestClient, picks: list[int]
) -> None:
    client.delete("/api/spike/entries", headers=USER_HEADERS)
    pool = [uuid4() for _ in range(6)]

    for pick in picks:
        post(client, pool[pick])

    summary = client.get("/api/spike/summary", headers=USER_HEADERS).json()
    assert summary["total"] == len(set(picks))
    assert summary["total"] + summary["duplicates_received"] == len(picks)


@pytest.mark.parametrize("note", ["", "a" * 500])
def test_note_length_limits(client: TestClient, note: str) -> None:
    assert post(client, uuid4(), note)[0] == 201
