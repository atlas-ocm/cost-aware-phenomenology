#!/usr/bin/env python3
"""Validate the Memory Dreaming worked example against its schema.

Exists so that `check_repo.ps1` can exercise the schema-as-contract on the
worked example directly, not only via pytest collection.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = ROOT / "spec" / "memory_dreaming" / "run.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "memory_dreaming" / "run_example.json"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator.check_schema(schema)
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(example),
        key=lambda e: list(e.path),
    )

    if errors:
        print(f"memory_dreaming example failed schema validation ({len(errors)}):")
        for err in errors:
            location = "/".join(str(p) for p in err.path) or "<root>"
            print(f"  - {location}: {err.message}")
        return 1

    print(
        f"memory_dreaming example OK ({EXAMPLE_PATH.name}) against "
        f"{SCHEMA_PATH.name}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
