"""Tests for the Cross-Domain Drain schema."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "cross_domain_drain.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "cross_domain_drain_event_example.json"


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


def test_cdd_03_no_drain_requires_non_zero_new_evidence():
    case = _load_example()
    case["event"]["state"] = "no_drain"
    case["event"]["verified_progress"]["new_evidence_count"] = 0
    errors = list(_validator().iter_errors(case))
    assert errors, "CDD-03: no_drain forbids zero new_evidence_count"


def test_cdd_04_context_contamination_cannot_route_to_model_upgrade_only():
    case = _load_example()
    case["event"]["mechanism"] = "context_contamination"
    case["event"]["recommended_action"] = "switch_model_up_for_verification"
    errors = list(_validator().iter_errors(case))
    assert errors, "CDD-04: context_contamination + switch_model_up alone is rejected"


def test_cdd_04_context_contamination_with_clean_context_is_valid():
    case = _load_example()
    case["event"]["mechanism"] = "context_contamination"
    case["event"]["recommended_action"] = "clean_context"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_cdd_05_authority_confusion_requires_human_or_block():
    case = _load_example()
    case["event"]["mechanism"] = "authority_confusion"
    case["event"]["recommended_action"] = "clean_context"
    errors = list(_validator().iter_errors(case))
    assert errors, "CDD-05: authority_confusion requires require_human_decision or block_release"


def test_cdd_06_browser_visibility_gap_requires_mirror_or_freeze():
    case = _load_example()
    case["event"]["mechanism"] = "browser_visibility_gap"
    case["event"]["recommended_action"] = "switch_model_down"
    errors = list(_validator().iter_errors(case))
    assert errors, "CDD-06: browser_visibility_gap requires refresh_mirror or freeze_scope"


def test_cdd_07_memory_pollution_requires_quarantine_or_block():
    case = _load_example()
    case["event"]["mechanism"] = "memory_pollution"
    case["event"]["recommended_action"] = "clean_context"
    errors = list(_validator().iter_errors(case))
    assert errors, "CDD-07: memory_pollution requires quarantine_context or block_release"


def test_cdd_08_emotional_overweight_requires_explicit_goal_or_hold():
    case = _load_example()
    case["event"]["mechanism"] = "emotional_overweight"
    case["event"]["recommended_action"] = "switch_role"
    errors = list(_validator().iter_errors(case))
    assert errors, "CDD-08: emotional_overweight requires require_explicit_goal or hold"


def test_cdd_09_social_noise_capture_requires_scope_freeze_or_role_switch():
    case = _load_example()
    case["event"]["mechanism"] = "social_noise_capture"
    case["event"]["recommended_action"] = "clean_context"
    errors = list(_validator().iter_errors(case))
    assert errors, "CDD-09: social_noise_capture requires freeze_scope or switch_role"


def test_cdd_10_critical_collapse_requires_hold_rollback_or_human():
    case = _load_example()
    case["event"]["state"] = "critical_budget_collapse"
    case["event"]["recommended_action"] = "switch_model_down"
    errors = list(_validator().iter_errors(case))
    assert errors, "CDD-10: critical_budget_collapse requires hold, rollback, or require_human_decision"


def test_unknown_domain_rejected():
    case = _load_example()
    case["event"]["origin_domain"] = "vibes"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_mechanism_rejected():
    case = _load_example()
    case["event"]["mechanism"] = "mood_drift"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_state_rejected():
    case = _load_example()
    case["event"]["state"] = "leaking"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_containment_action_rejected():
    case = _load_example()
    case["event"]["recommended_action"] = "pray"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_observed_symptoms_minimum_one():
    case = _load_example()
    case["event"]["observed_symptoms"] = []
    errors = list(_validator().iter_errors(case))
    assert errors


def test_drain_ratio_must_be_non_negative():
    case = _load_example()
    case["event"]["drain_ratio"] = -1
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_rejected():
    case = _load_example()
    case["event"]["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_estimated_cost_requires_tokens_and_time():
    case = _load_example()
    del case["event"]["estimated_cost"]["tokens"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_verified_progress_requires_uncertainty_reduction():
    case = _load_example()
    del case["event"]["verified_progress"]["uncertainty_reduction"]
    errors = list(_validator().iter_errors(case))
    assert errors
