from __future__ import annotations

import json
from pathlib import Path

import pytest

from homestead_finance.core.settings import INGRESS_GATEWAY, LOOPBACK, Settings


def write_options(path: Path, options: dict[str, object]) -> None:
    path.write_text(json.dumps(options), encoding="utf-8")


def test_defaults_match_the_app_container() -> None:
    settings = Settings()

    assert settings.data_dir == Path("/data")
    # The gateway, plus loopback for the container's own Docker HEALTHCHECK.
    assert settings.trusted_proxies == [INGRESS_GATEWAY, LOOPBACK]
    assert settings.port == 8099
    assert settings.dev_mode is False
    assert settings.database_path == Path("/data/homestead_finance.db")


def test_environment_overrides_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HF_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("HF_DEV_MODE", "true")
    monkeypatch.setenv("HF_TRUSTED_PROXIES", "127.0.0.1, 10.0.0.0/8")

    settings = Settings()

    assert settings.data_dir == tmp_path
    assert settings.dev_mode is True
    assert settings.trusted_proxies == ["127.0.0.1", "10.0.0.0/8"]


def test_app_options_are_read(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    options = tmp_path / "options.json"
    write_options(options, {"log_level": "debug"})
    monkeypatch.setenv("HF_OPTIONS_FILE", str(options))

    assert Settings().log_level == "debug"


def test_environment_beats_app_options(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    options = tmp_path / "options.json"
    write_options(options, {"log_level": "debug"})
    monkeypatch.setenv("HF_OPTIONS_FILE", str(options))
    monkeypatch.setenv("HF_LOG_LEVEL", "error")

    assert Settings().log_level == "error"


def test_unknown_app_options_cannot_override_settings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    options = tmp_path / "options.json"
    write_options(options, {"data_dir": "/elsewhere", "dev_mode": True, "something": 1})
    monkeypatch.setenv("HF_OPTIONS_FILE", str(options))

    settings = Settings()

    assert settings.data_dir == Path("/data")
    assert settings.dev_mode is False


def test_options_file_defaults_to_the_data_folder(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("HF_OPTIONS_FILE")
    monkeypatch.setenv("HF_DATA_DIR", str(tmp_path))
    write_options(tmp_path / "options.json", {"log_level": "warning"})

    assert Settings().log_level == "warning"
