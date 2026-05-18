"""Tests for the Cycle State Machine schema."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "cycle_state_machine.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "cycle_node_example.json"


def _load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_example():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8-sig"))


def _validator():
    return jsonschema.Draft202012Validator(_load_schema())


def test_schema_is_valid_draft_2020_12():
    jsonschema.Draft202012Validator.check_schema(_load_schema())


def test_worked_example_passes():
    errors = sorted(_validator().iter_errors(_load_example()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_csm_04_hold_requires_hold_reason():
    case = _load_example()
    del case["transition"]["hold_reason"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_csm_05_reopen_requires_audit_log_ref():
    case = _load_example()
    case["transition"]["kind"] = "reopen"
    case["transition"]["from_state"] = "closed"
    case["transition"]["to_state"] = "reopened"
    errors = list(_validator().iter_errors(case))
    assert errors, "CSM-05: reopen requires audit_log_ref"


def test_csm_05_reopen_with_audit_log_ref_is_valid():
    case = _load_example()
    case["transition"]["kind"] = "reopen"
    case["transition"]["from_state"] = "closed"
    case["transition"]["to_state"] = "reopened"
    case["transition"]["audit_log_ref"] = "com_log/2026-05-18/reopen/node_x"
    case["transition"].pop("hold_reason", None)
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_csm_02_close_only_from_active():
    case = _load_example()
    case["transition"]["kind"] = "close"
    case["transition"]["from_state"] = "pending"
    case["transition"]["to_state"] = "closed"
    case["transition"].pop("hold_reason", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "CSM-02: close must transition from active"


def test_csm_03_resume_forbidden_from_quarantined():
    case = _load_example()
    case["transition"]["kind"] = "resume"
    case["transition"]["from_state"] = "quarantined"
    case["transition"]["to_state"] = "active"
    case["transition"].pop("hold_reason", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "CSM-03: quarantined cannot resume directly"


def test_csm_06_drop_only_from_pending_or_on_hold():
    case = _load_example()
    case["transition"]["kind"] = "drop"
    case["transition"]["from_state"] = "closed"
    case["transition"]["to_state"] = "dropped"
    case["transition"].pop("hold_reason", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "CSM-06: drop must originate from pending or on_hold"


def test_unknown_state_rejected():
    case = _load_example()
    case["node"]["current_state"] = "limbo"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_transition_kind_rejected():
    case = _load_example()
    case["transition"]["kind"] = "vanish"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_node_kind_rejected():
    case = _load_example()
    case["node"]["kind"] = "vibe"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_rejected():
    case = _load_example()
    case["extra"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_resolve_only_from_closed():
    case = _load_example()
    case["transition"]["kind"] = "resolve"
    case["transition"]["from_state"] = "active"
    case["transition"]["to_state"] = "resolved"
    case["transition"].pop("hold_reason", None)
    errors = list(_validator().iter_errors(case))
    assert errors


def test_schedule_only_from_pending():
    case = _load_example()
    case["transition"]["kind"] = "schedule"
    case["transition"]["from_state"] = "on_hold"
    case["transition"]["to_state"] = "active"
    case["transition"].pop("hold_reason", None)
    errors = list(_validator().iter_errors(case))
    assert errors
