"""App settings from environment variables (HF_*) and the app options in options.json."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Annotated, Any, Literal, cast

from pydantic import Field, field_validator
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    NoDecode,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from sqlalchemy import URL

LogLevel = Literal["trace", "debug", "info", "notice", "warning", "error", "fatal"]

#: The Home Assistant ingress gateway (the Supervisor) on the internal hassio network.
INGRESS_GATEWAY = "172.30.32.2"

#: Option keys from homestead_finance/config.yaml that map onto settings fields.
APP_OPTION_KEYS = frozenset({"log_level"})


class Settings(BaseSettings):
    """Runtime settings.

    Priority, highest first: constructor arguments, ``HF_*`` environment variables,
    then the app options the Supervisor writes to ``options.json``.
    """

    model_config = SettingsConfigDict(env_prefix="HF_", extra="ignore")

    data_dir: Path = Path("/data")
    dev_mode: bool = False
    log_level: LogLevel = "info"
    trusted_proxies: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [INGRESS_GATEWAY]
    )
    static_dir: Path | None = None
    version: str = "dev"
    # The app must listen on the hassio network; the ingress gateway check guards it.
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8099

    @field_validator("trusted_proxies", mode="before")
    @classmethod
    def _split_comma_separated(cls, value: object) -> object:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @property
    def database_path(self) -> Path:
        return self.data_dir / "homestead_finance.db"

    @property
    def database_url(self) -> URL:
        return URL.create("sqlite", database=str(self.database_path))

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings, env_settings, AppOptionsSource(settings_cls))


def options_path() -> Path:
    """Where the Supervisor writes the app options (``HF_OPTIONS_FILE`` overrides it)."""
    explicit = os.environ.get("HF_OPTIONS_FILE")
    if explicit:
        return Path(explicit)
    return Path(os.environ.get("HF_DATA_DIR", "/data")) / "options.json"


class AppOptionsSource(PydanticBaseSettingsSource):
    """Reads the known app options from options.json; unknown keys are ignored."""

    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        super().__init__(settings_cls)
        self._options = _read_options(options_path())

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        return self._options.get(field_name), field_name, False

    def __call__(self) -> dict[str, Any]:
        return dict(self._options)


def _read_options(path: Path) -> dict[str, Any]:
    try:
        raw: object = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    if not isinstance(raw, dict):
        return {}
    options = cast(dict[str, Any], raw)
    return {key: value for key, value in options.items() if key in APP_OPTION_KEYS}
