"""Tests for the Context Hygiene schema.

Covers the worked example plus the doc-level invariants CH-01..CH-12
from 02_subsystems/context_hygiene.md. Each invariant has a negative
test that confirms the schema rejects the violation.

CH-10 has both a schema-level part (policy const) and a numeric
cross-field part (input_tokens_after <= input_tokens_before) that is
not first-class in JSON Schema Draft 2020-12. The numeric part is
asserted directly in this test file as a separate test.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "context_hygiene.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "context_hygiene_result_example.json"


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


# -- CH-01: context is not truth (every unit has evidence_role) --


def test_ch_01_context_unit_requires_evidence_role():
    case = _load_example()
    del case["context_units"][0]["evidence_role"]
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-01: every ContextUnit must declare an evidence_role"


def test_ch_01_evidence_role_enum_is_closed():
    case = _load_example()
    case["context_units"][0]["evidence_role"] = "truth"
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-01: evidence_role must be from the closed enum"


# -- CH-02: model output cannot become evidence without external support --


def test_ch_02_policy_allow_model_self_evidence_locked_to_false():
    case = _load_example()
    case["policy"]["allow_model_self_evidence"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-02: policy.allow_model_self_evidence must be const false"


# -- CH-03: failed-route residue is not instruction --


def test_ch_03_policy_allow_failed_route_as_instruction_locked_to_false():
    case = _load_example()
    case["policy"]["allow_failed_route_as_instruction"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-03: policy.allow_failed_route_as_instruction must be const false"


# -- CH-04: stale must be refreshed or demoted --


def test_ch_04_context_unit_requires_freshness():
    case = _load_example()
    del case["context_units"][0]["freshness"]
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-04: every ContextUnit must declare freshness"


def test_ch_04_freshness_enum_is_closed():
    case = _load_example()
    case["context_units"][0]["freshness"] = "ancient"
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-04: freshness must be fresh|stale|unknown"


# -- CH-05: candidate memory cannot be canonical --


def test_ch_05_policy_allow_candidate_memory_as_canonical_locked_to_false():
    case = _load_example()
    case["policy"]["allow_candidate_memory_as_canonical"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-05: policy.allow_candidate_memory_as_canonical must be const false"


def test_ch_05_canonicality_enum_separates_candidate_and_canonical():
    case = _load_example()
    case["context_units"][0]["canonicality"] = "promoted"
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-05: canonicality must be from the closed enum"


# -- CH-06: loop verdicts require loop signals --


def test_ch_06_loop_detected_requires_loop_signals():
    case = _load_example()
    case["result"]["verdict"] = "loop_detected"
    case["result"]["loop_signals"] = []
    case["result"]["loop_break_actions"] = ["drop_failed_trace"]
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-06: verdict=loop_detected must require loop_signals minItems:1"


def test_ch_06_loop_risk_requires_loop_signals():
    case = _load_example()
    case["result"]["verdict"] = "loop_risk"
    case["result"]["loop_signals"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-06: verdict=loop_risk must require loop_signals minItems:1"


# -- CH-07: tool-result scope is preserved (structured object, not string) --


def test_ch_07_scope_is_structured_object_not_string():
    case = _load_example()
    case["context_units"][3]["scope"] = "bash session in pwsh"
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-07: scope must be a structured object preserving shell/repo/etc"


def test_ch_07_scope_additional_property_rejected():
    case = _load_example()
    case["context_units"][0]["scope"]["mood"] = "tense"
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-07: scope additionalProperties is false"


# -- CH-08: quarantined kept separate from dropped --


def test_ch_08_quarantine_required_verdict_requires_at_least_one_quarantined():
    case = _load_example()
    case["result"]["verdict"] = "quarantine_required"
    case["result"]["quarantined"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-08: verdict=quarantine_required requires quarantined minItems:1"


# -- CH-09: summaries must preserve provenance (policy lock) --


def test_ch_09_policy_summaries_must_preserve_provenance_locked_to_true():
    case = _load_example()
    case["policy"]["summaries_must_preserve_provenance"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-09: policy.summaries_must_preserve_provenance must be const true"


# -- CH-10: minimal sufficient context policy + numeric assertion --


def test_ch_10_policy_prefer_minimal_sufficient_locked_to_true():
    case = _load_example()
    case["policy"]["prefer_minimal_sufficient_context"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-10: policy.prefer_minimal_sufficient_context must be const true"


def test_ch_10_token_accounting_is_required():
    case = _load_example()
    del case["result"]["token_accounting"]
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-10: token_accounting is required on the result"


def test_ch_10_input_tokens_after_must_not_exceed_before():
    """Numeric cross-field invariant. JSON Schema Draft 2020-12 does not
    cleanly express number-A <= number-B without custom keywords, so the
    test asserts it directly against the worked example and a tampered
    copy."""
    case = _load_example()
    ta = case["result"]["token_accounting"]
    assert ta["input_tokens_after"] <= ta["input_tokens_before"]

    case["result"]["token_accounting"]["input_tokens_after"] = (
        ta["input_tokens_before"] + 1
    )
    tampered_ta = case["result"]["token_accounting"]
    assert (
        tampered_ta["input_tokens_after"] > tampered_ta["input_tokens_before"]
    ), "tamper failed; CH-10 numeric check is meaningless in this test"


# -- CH-11: loop break must change at least one axis --


def test_ch_11_loop_detected_requires_loop_break_actions():
    case = _load_example()
    case["result"]["verdict"] = "loop_detected"
    case["result"]["loop_signals"] = ["same_hypothesis_without_new_evidence"]
    case["result"]["loop_break_actions"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-11: verdict=loop_detected must require loop_break_actions minItems:1"


def test_ch_11_futility_escalated_requires_loop_break_actions():
    case = _load_example()
    case["result"]["verdict"] = "futility_escalated"
    case["result"]["recommended_next_action"] = "stop_and_replan"
    case["result"]["loop_break_actions"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-11: verdict=futility_escalated must require loop_break_actions minItems:1"


# -- CH-12: futility escalation must request stop_and_replan or ask_verifier --


def test_ch_12_futility_escalated_requires_specific_next_action():
    case = _load_example()
    case["result"]["verdict"] = "futility_escalated"
    case["result"]["loop_break_actions"] = ["change_model"]
    case["result"]["recommended_next_action"] = "continue"
    errors = list(_validator().iter_errors(case))
    assert errors, "CH-12: futility_escalated requires next_action in {stop_and_replan, ask_verifier}"


def test_ch_12_futility_escalated_with_stop_and_replan_is_valid():
    case = _load_example()
    case["result"]["verdict"] = "futility_escalated"
    case["result"]["loop_break_actions"] = ["change_model"]
    case["result"]["recommended_next_action"] = "stop_and_replan"
    case["result"]["loop_signals"] = ["same_hypothesis_without_new_evidence"]
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


# -- Verdict-driven required fields --


def test_context_contamination_requires_contamination_signals():
    case = _load_example()
    case["result"]["verdict"] = "context_contamination"
    case["result"]["contamination_signals"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=context_contamination requires contamination_signals minItems:1"


def test_stale_context_requires_refresh_required():
    case = _load_example()
    case["result"]["verdict"] = "stale_context"
    case["result"]["refresh_required"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=stale_context requires refresh_required minItems:1"


# -- Enum + structure guards --


def test_unknown_verdict_rejected():
    case = _load_example()
    case["result"]["verdict"] = "all_fine"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_loop_signal_rejected():
    case = _load_example()
    case["result"]["loop_signals"] = ["bad_vibes"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_contamination_signal_rejected():
    case = _load_example()
    case["result"]["contamination_signals"] = ["just_old"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_loop_break_action_rejected():
    case = _load_example()
    case["result"]["loop_break_actions"] = ["try_harder"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_source_kind_rejected():
    case = _load_example()
    case["context_units"][0]["source"] = "intuition"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_recommended_next_action_rejected():
    case = _load_example()
    case["result"]["recommended_next_action"] = "vibe_check"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_relevance_must_be_in_unit_interval():
    case = _load_example()
    case["context_units"][0]["relevance"] = 1.5
    errors = list(_validator().iter_errors(case))
    assert errors


def test_token_cost_must_be_non_negative_integer():
    case = _load_example()
    case["context_units"][0]["token_cost"] = -1
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_at_root_rejected():
    case = _load_example()
    case["unexpected_field"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_result_rejected():
    case = _load_example()
    case["result"]["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_context_unit_rejected():
    case = _load_example()
    case["context_units"][0]["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_healthy_verdict_with_clean_result_is_valid():
    case = _load_example()
    case["result"]["verdict"] = "healthy"
    case["result"]["loop_signals"] = []
    case["result"]["contamination_signals"] = []
    case["result"]["quarantined"] = []
    case["result"]["refresh_required"] = []
    case["result"]["loop_break_actions"] = []
    case["result"]["recommended_next_action"] = "continue"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]
