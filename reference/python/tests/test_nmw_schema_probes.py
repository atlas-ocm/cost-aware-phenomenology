"""Pytest wrapper: run the NO_MAP_NO_WORK v0.2.1 schema probe suite.

Executes the standalone regression probe suite
(`nmw_schema_probe_suite.py`) against the canonical CAP-Guardrails schema
and fails on any reported gap. The probe suite remains directly
executable on its own; this wrapper only wires it into pytest collection.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parents[2]
PROBE_SUITE = TESTS_DIR / "nmw_schema_probe_suite.py"
GUARDRAILS_SCHEMA = ROOT / "spec" / "cap_guardrails.schema.json"


def test_nmw_schema_probe_suite_reports_no_gaps():
    result = subprocess.run(
        [sys.executable, str(PROBE_SUITE), str(GUARDRAILS_SCHEMA)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "nmw_schema_probe_suite reported gap(s) against "
        f"{GUARDRAILS_SCHEMA.name}:\n{result.stdout}\n{result.stderr}"
    )
