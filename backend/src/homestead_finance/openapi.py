"""Write the OpenAPI schema: ``python -m homestead_finance.openapi [output.json]``.

The frontend generates its typed API client from this file (``pnpm gen:api``).
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from homestead_finance.core.settings import Settings
from homestead_finance.main import create_app


def render() -> str:
    with tempfile.TemporaryDirectory() as data_dir:
        # Building the schema doesn't start the app, so nothing touches the data folder.
        app = create_app(Settings(data_dir=Path(data_dir), static_dir=None))
        return json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    text = render()
    if args:
        Path(args[0]).write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
