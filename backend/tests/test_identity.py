from __future__ import annotations

import logging

import pytest
from fastapi.testclient import TestClient

from homestead_finance.core.settings import Settings
from homestead_finance.main import create_app
from tests.support import GATEWAY, USER_HEADERS


def test_me_returns_the_home_assistant_user(client: TestClient) -> None:
    headers = {**USER_HEADERS, "X-Ingress-Path": "/api/hassio_ingress/abc123"}

    response = client.get("/api/me", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "user_id": USER_HEADERS["X-Remote-User-Id"],
        "name": "farmer",
        "display_name": "Farmer Jo",
        "ingress_path": "/api/hassio_ingress/abc123",
    }


def test_name_and_display_name_are_optional(client: TestClient) -> None:
    response = client.get("/api/me", headers={"X-Remote-User-Id": "abc"})

    assert response.status_code == 200
    assert response.json()["name"] is None
    assert response.json()["display_name"] is None


@pytest.mark.parametrize("headers", [{}, {"X-Remote-User-Id": "   "}])
def test_requests_without_a_user_are_refused(client: TestClient, headers: dict[str, str]) -> None:
    assert client.get("/api/me", headers=headers).status_code == 401


def test_dev_mode_uses_a_stub_user(settings: Settings) -> None:
    app = create_app(settings.model_copy(update={"dev_mode": True}))
    with TestClient(app, client=GATEWAY) as test_client:
        assert test_client.get("/api/me").json()["user_id"] == "dev-user"
        assert test_client.get("/api/me", headers=USER_HEADERS).json()["name"] == "farmer"


def test_header_names_are_logged_but_never_values(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.DEBUG, logger="homestead_finance"):
        client.get("/api/me", headers=USER_HEADERS)

    logged = caplog.text
    assert "x-remote-user-id" in logged
    assert "x-remote-user-display-name" in logged
    for value in USER_HEADERS.values():
        assert value not in logged
