from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_reports_version_schema_and_database(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "1.2.3",
        "schema_revision": "0002",
        "database": "ok",
    }


def test_health_needs_no_user(client: TestClient) -> None:
    # The Supervisor watchdog calls it without ingress identity headers.
    assert client.get("/api/health").status_code == 200
