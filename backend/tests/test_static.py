from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from homestead_finance.core.settings import Settings
from homestead_finance.main import create_app
from tests.support import GATEWAY


@pytest.fixture
def frontend(tmp_path: Path) -> Path:
    root = tmp_path / "frontend"
    (root / "assets").mkdir(parents=True)
    (root / "index.html").write_text("<!doctype html><title>Homestead</title>", encoding="utf-8")
    (root / "assets" / "index-abc123.js").write_text("console.log(1)", encoding="utf-8")
    return root


@pytest.fixture
def site(settings: Settings, frontend: Path) -> Iterator[TestClient]:
    app = create_app(settings.model_copy(update={"static_dir": frontend}))
    with TestClient(app, client=GATEWAY) as test_client:
        yield test_client


def test_root_serves_index_and_revalidates(site: TestClient) -> None:
    response = site.get("/")

    assert response.status_code == 200
    assert "<title>Homestead</title>" in response.text
    assert response.headers["cache-control"] == "no-cache"


def test_hashed_assets_are_cached_for_a_year(site: TestClient) -> None:
    response = site.get("/assets/index-abc123.js")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=31536000, immutable"


@pytest.mark.parametrize("path", ["/missing.js", "/assets", "/assets/"])
def test_unknown_paths_and_folders_are_404_not_redirects(site: TestClient, path: str) -> None:
    response = site.get(path, follow_redirects=False)

    assert response.status_code == 404


def test_api_still_works_with_the_frontend_mounted(site: TestClient) -> None:
    assert site.get("/api/health").status_code == 200


def test_api_only_when_frontend_folder_is_missing(settings: Settings, tmp_path: Path) -> None:
    app = create_app(settings.model_copy(update={"static_dir": tmp_path / "nope"}))
    with TestClient(app, client=GATEWAY) as test_client:
        assert test_client.get("/").status_code == 404
        assert test_client.get("/api/health").status_code == 200
