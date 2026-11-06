"""Write the API's OpenAPI schema to openapi.json, or check that it is current.

    python scripts/openapi.py           # regenerate openapi.json
    python scripts/openapi.py --check   # exit 1 if openapi.json is stale

The schema comes from the app object, so no server and no .env are needed.
oasdiff compares the committed file with main to catch breaking API changes.
"""

import json
import os
import sys
from pathlib import Path

# Settings that don't change the schema; the environment variables win over .env
os.environ["APP_ENVIRONMENT"] = "TESTING"
os.environ.setdefault("APP_CORS_ORIGINS", "[]")
os.environ.setdefault("APP_CORS_HEADERS", "[]")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.main import app

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "openapi.json"


def render() -> str:
    return json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    schema = render()
    if "--check" in sys.argv[1:]:
        current = (
            SCHEMA_PATH.read_text(encoding="utf-8") if SCHEMA_PATH.exists() else ""
        )
        if current != schema:
            print("openapi.json is stale: run `make openapi` and commit it")
            return 1
        return 0
    SCHEMA_PATH.write_text(schema, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
