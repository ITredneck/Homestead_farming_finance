from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from homestead_finance.core.ingress import IngressGatewayMiddleware
from homestead_finance.core.settings import Settings
from homestead_finance.main import create_app
from tests.support import GATEWAY, OUTSIDER


@pytest.fixture
def outsider(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app, client=OUTSIDER) as test_client:
        yield test_client


def test_gateway_requests_are_allowed(client: TestClient) -> None:
    assert client.get("/api/health").status_code == 200


def test_other_addresses_are_rejected(outsider: TestClient) -> None:
    response = outsider.get("/api/health")

    assert response.status_code == 403


def test_forwarded_for_header_cannot_spoof_the_gateway(outsider: TestClient) -> None:
    response = outsider.get(
        "/api/health", headers={"X-Forwarded-For": GATEWAY[0], "X-Real-IP": GATEWAY[0]}
    )

    assert response.status_code == 403


def test_container_healthcheck_over_loopback_is_allowed(app: FastAPI) -> None:
    # Docker's HEALTHCHECK runs inside the container and connects over loopback.
    with TestClient(app, client=("127.0.0.1", 50000)) as test_client:
        assert test_client.get("/api/health").status_code == 200


def test_dev_mode_allows_any_address(settings: Settings) -> None:
    app = create_app(settings.model_copy(update={"dev_mode": True}))
    with TestClient(app, client=OUTSIDER) as test_client:
        assert test_client.get("/api/health").status_code == 200


@pytest.mark.parametrize(
    ("host", "trusted"),
    [
        ("172.30.32.2", True),
        ("::ffff:172.30.32.2", True),
        ("172.30.32.1", False),
        ("127.0.0.1", False),
        ("testclient", False),
        (None, False),
    ],
)
def test_only_the_gateway_address_is_trusted(host: str | None, trusted: bool) -> None:
    middleware = IngressGatewayMiddleware(FastAPI(), trusted=["172.30.32.2"])

    assert middleware.is_trusted(host) is trusted


def test_networks_can_be_trusted() -> None:
    middleware = IngressGatewayMiddleware(FastAPI(), trusted=["10.0.0.0/8"])

    assert middleware.is_trusted("10.1.2.3")
    assert not middleware.is_trusted("11.0.0.1")
