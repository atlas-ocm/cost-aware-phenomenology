"""Verify all schemas in spec/ are valid JSON Schema Draft 2020-12."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parents[3]
SPEC_DIR = ROOT / "spec"


def test_all_schemas_are_valid_draft_2020_12():
    schema_files = sorted(SPEC_DIR.glob("*.json"))
    assert schema_files, f"No schemas found in {SPEC_DIR}"
    for path in schema_files:
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)


def test_schema_ids_are_urns():
    """All schemas must have URN-style $id, not placeholder [org] URLs."""
    for path in sorted(SPEC_DIR.glob("*.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        sid = schema.get("$id", "")
        assert "[org]" not in sid, f"{path.name}: $id still contains [org] placeholder"
        assert sid, f"{path.name}: $id is empty"
