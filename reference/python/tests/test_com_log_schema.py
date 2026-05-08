"""Tests for COM-Log schema validation."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.validator import validate


def test_minimal_valid_com_log():
    com_log = {
        "domain": "Work",
        "node": "Free edits / Boundary",
        "current_status": ["Open", "Leaking"],
        "recommended_operator": {"operator": "Fixation", "risk_weight_percent": 20},
        "target_status": ["Closed"],
        "next_physical_step": "Send written rule: edits only via new payment",
    }
    result = validate(com_log)
    assert result["valid"], result["errors"]


def test_missing_required_fields():
    com_log = {"domain": "Work"}
    result = validate(com_log)
    assert not result["valid"]


def test_unknown_operator():
    com_log = {
        "domain": "Work",
        "node": "Test",
        "current_status": ["Open"],
        "recommended_operator": {"operator": "InvalidOp", "risk_weight_percent": 20},
        "target_status": ["Closed"],
        "next_physical_step": "Test step",
    }
    result = validate(com_log)
    assert not result["valid"]


def test_breach_requires_recovery_gate():
    com_log = {
        "domain": "Work",
        "node": "Test",
        "current_status": ["Open"],
        "recommended_operator": {"operator": "Fixation", "risk_weight_percent": 20},
        "target_status": ["Closed"],
        "next_physical_step": "Test step",
        "telemetry_state": "Breach",
        "budget_gate": "Allowed",
    }
    result = validate(com_log)
    assert not result["valid"]
    assert any("Recovery-Only" in e for e in result["errors"])
