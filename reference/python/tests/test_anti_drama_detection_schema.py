"""Tests for the Anti-drama Detection schema."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "anti_drama_detection.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "anti_drama_event_example.json"


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


def test_ad_01_drama_demands_budget_routes_to_freeze_or_hold_or_human():
    case = _load_example()
    case["recommended_action"] = "proceed"
    errors = list(_validator().iter_errors(case))
    assert errors, "AD-01: drama_demands_budget_increase must route to freeze_budget / hold / escalate_to_human"


def test_ad_01_freeze_budget_action_is_valid():
    case = _load_example()
    case["recommended_action"] = "freeze_budget"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_ad_02_drama_overrides_evidence_requires_contradicting_refs():
    case = _load_example()
    case["verdict"] = "drama_overrides_evidence"
    case["recommended_action"] = "require_evidence_for_claim"
    case.pop("contradicting_evidence_refs", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "AD-02: drama_overrides_evidence requires contradicting_evidence_refs minItems:1"


def test_ad_02_drama_overrides_with_contradicting_refs_is_valid():
    case = _load_example()
    case["verdict"] = "drama_overrides_evidence"
    case["recommended_action"] = "require_evidence_for_claim"
    case["contradicting_evidence_refs"] = ["mirror_frame:contradicts_claim"]
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_ad_03_non_no_drama_requires_evidence_refs():
    case = _load_example()
    case["verdict"] = "narrative_pressure_detected"
    case["recommended_action"] = "downweight_emotional_signal"
    case["evidence_refs"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "AD-03: non-no_drama verdicts require evidence_refs minItems:1"


def test_ad_03_non_no_drama_requires_drama_signals():
    case = _load_example()
    case["verdict"] = "narrative_pressure_detected"
    case["recommended_action"] = "downweight_emotional_signal"
    case["drama_signals"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "AD-03: non-no_drama verdicts require at least one drama signal"


def test_no_drama_with_empty_signals_is_valid():
    case = _load_example()
    case["verdict"] = "no_drama"
    case["recommended_action"] = "proceed"
    case["drama_signals"] = []
    case["evidence_refs"] = []
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_ad_04_no_release_or_canonicalize_field():
    case = _load_example()
    case["release_decision"] = "pass"
    errors = list(_validator().iter_errors(case))
    assert errors, "AD-04: anti-drama event must not carry a release decision"


def test_unknown_drama_signal_rejected():
    case = _load_example()
    case["drama_signals"] = ["passion"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_verdict_rejected():
    case = _load_example()
    case["verdict"] = "calm"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_recommended_action_rejected():
    case = _load_example()
    case["recommended_action"] = "meditate"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_emitter_id_required():
    case = _load_example()
    del case["emitter"]["id"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_rejected():
    case = _load_example()
    case["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_drama_inflation_verdict_routes_to_downweight_or_evidence():
    case = _load_example()
    case["verdict"] = "drama_inflation"
    case["recommended_action"] = "require_evidence_for_claim"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_narrative_pressure_with_proceed_is_valid_if_evidence_present():
    case = _load_example()
    case["verdict"] = "narrative_pressure_detected"
    case["recommended_action"] = "proceed"
    case["drama_signals"] = ["emphasis_inflation"]
    case["evidence_refs"] = ["session:turn_x"]
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]
