from __future__ import annotations

import json

from homestead_finance.openapi import render


def test_schema_is_deterministic() -> None:
    assert render() == render()


def test_schema_lists_the_api() -> None:
    schema = json.loads(render())

    assert schema["info"]["version"] == "1"
    assert {"/api/health", "/api/me", "/api/farm", "/api/spike/entries"} <= set(schema["paths"])
    assert schema["paths"]["/api/health"]["get"]["operationId"] == "system_health"
