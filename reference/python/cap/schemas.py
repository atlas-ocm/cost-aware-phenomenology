"""Schema loading and validation for CAP."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

# reference/python/cap/schemas.py -> reference/python/cap -> reference/python -> reference -> CAP
ROOT = Path(__file__).resolve().parent.parent.parent.parent
SPEC_DIR = ROOT / "spec"


def load_schema(name: str) -> dict[str, Any]:
    """Load a schema by name from the spec/ directory."""
    schema_path = SPEC_DIR / f"{name}.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


def load_com_log_schema() -> dict[str, Any]:
    return load_schema("com_log_schema")


def load_operator_alphabet() -> dict[str, Any]:
    return load_schema("operator_alphabet")


def validate_com_log(com_log: dict[str, Any]) -> list[str]:
    """Validate a COM-Log dict. Returns list of error messages, empty if valid."""
    schema = load_com_log_schema()
    validator = jsonschema.Draft202012Validator(schema)
    errors: list[str] = []
    for err in validator.iter_errors(com_log):
        path = ".".join(str(p) for p in err.absolute_path)
        errors.append(f"{path}: {err.message}" if path else err.message)
    return errors
