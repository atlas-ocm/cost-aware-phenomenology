"""Tests for the Observability Protocol schema."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "observability_protocol.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "observability_event_example.json"


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


def test_obs_01_provenance_minimum_one():
    case = _load_example()
    case["provenance"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "OBS-01: provenance minItems:1"


def test_obs_02_release_gate_decision_requires_audit_log_ref():
    case = _load_example()
    del case["audit_log_ref"]
    errors = list(_validator().iter_errors(case))
    assert errors, "OBS-02: release_gate_decision requires audit_log_ref"


def test_obs_02_authorization_event_requires_audit_log_ref():
    case = _load_example()
    case["event_kind"] = "authorization_event"
    del case["audit_log_ref"]
    errors = list(_validator().iter_errors(case))
    assert errors, "OBS-02: authorization_event requires audit_log_ref"


def test_obs_02_anchor_decay_transition_requires_audit_log_ref():
    case = _load_example()
    case["event_kind"] = "anchor_decay_transition"
    del case["audit_log_ref"]
    errors = list(_validator().iter_errors(case))
    assert errors, "OBS-02: anchor_decay_transition requires audit_log_ref"


def test_obs_03_silent_forbidden_for_canonical_affecting():
    case = _load_example()
    case["export_level"] = "silent"
    errors = list(_validator().iter_errors(case))
    assert errors, "OBS-03: silent export forbidden for release_gate_decision"


def test_obs_03_silent_allowed_for_non_canonical():
    case = _load_example()
    case["event_kind"] = "mirror_observation"
    case["export_level"] = "silent"
    case.pop("audit_log_ref", None)
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_obs_04_emitter_id_required():
    case = _load_example()
    del case["emitter"]["id"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_obs_05_scope_additional_property_rejected():
    case = _load_example()
    case["scope"]["mood"] = "calm"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_obs_06_unknown_event_kind_rejected():
    case = _load_example()
    case["event_kind"] = "vibe_check"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_obs_07_conclusion_field_in_payload_rejected():
    case = _load_example()
    case["payload"]["conclusion"] = "it's all fine"
    errors = list(_validator().iter_errors(case))
    assert errors, "OBS-07: payload.conclusion is rejected"


def test_unknown_emitter_kind_rejected():
    case = _load_example()
    case["emitter"]["kind"] = "spirit"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_export_level_rejected():
    case = _load_example()
    case["export_level"] = "loud"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_at_root_rejected():
    case = _load_example()
    case["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_non_canonical_event_does_not_require_audit_log_ref():
    case = _load_example()
    case["event_kind"] = "mirror_observation"
    case.pop("audit_log_ref", None)
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]
