"""Tests for the Adjustment Layer schema.

Covers the worked example plus the doc-level invariants ADJ-01..ADJ-10
from 02_subsystems/adjustment_dynamics.md (extended CandidateTransition
contract). Each invariant has a negative test that confirms the schema
rejects the violation.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "adjustment_layer.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "adjustment_candidate_transition_example.json"


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


# -- ADJ-01: mirror_frame_id required --


def test_adj_01_mirror_frame_id_required():
    case = _load_example()
    del case["input"]["mirror_frame_id"]
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-01: input.mirror_frame_id is required"


def test_adj_01_policy_require_mirror_frame_locked_to_true():
    case = _load_example()
    case["policy"]["require_mirror_frame"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-01: policy.require_mirror_frame must be const true"


# -- ADJ-02: cause remains hypothesis unless confirmed --


def test_adj_02_policy_allow_unverified_cause_as_fact_locked_to_false():
    case = _load_example()
    case["policy"]["allow_unverified_cause_as_fact"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-02: policy.allow_unverified_cause_as_fact must be const false"


def test_adj_02_cause_status_enum_does_not_include_fact():
    case = _load_example()
    case["input"]["inferred_cause"]["status"] = "fact"
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-02: cause_status enum must not include 'fact'"


# -- ADJ-03: desired state explicit with success criteria --


def test_adj_03_desired_state_required():
    case = _load_example()
    del case["input"]["desired_state"]
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-03: input.desired_state is required"


def test_adj_03_desired_state_success_criteria_minimum_one():
    case = _load_example()
    case["input"]["desired_state"]["success_criteria"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-03: desired_state.success_criteria minItems:1"


def test_adj_03_policy_require_explicit_desired_state_locked_to_true():
    case = _load_example()
    case["policy"]["require_explicit_desired_state"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-03: policy.require_explicit_desired_state must be const true"


# -- ADJ-04: minimal sufficient route --


def test_adj_04_route_minimum_one_step():
    case = _load_example()
    case["candidate"]["route"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-04: candidate.route minItems:1"


def test_adj_04_policy_prefer_minimal_route_locked_to_true():
    case = _load_example()
    case["policy"]["prefer_minimal_route"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-04: policy.prefer_minimal_route must be const true"


# -- ADJ-05: route must respect boundaries --


def test_adj_05_policy_allow_boundary_violation_locked_to_false():
    case = _load_example()
    case["policy"]["allow_boundary_violation"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-05: policy.allow_boundary_violation must be const false"


# -- ADJ-06: anchor conflict requires reconcile/retcon/rollback path --


def test_adj_06_repair_mode_with_conflicting_anchor_is_rejected():
    case = _load_example()
    case["candidate"]["mode"] = "repair"
    case["candidate"]["affected_anchors"] = [
        {
            "id": "anchor_x",
            "level": "L1-C",
            "status": "conflicting"
        }
    ]
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-06: mode=repair with conflicting anchor must be rejected"


def test_adj_06_reconcile_mode_with_conflicting_anchor_is_valid():
    case = _load_example()
    case["candidate"]["mode"] = "reconcile"
    case["candidate"]["affected_anchors"] = [
        {
            "id": "anchor_x",
            "level": "L1-C",
            "status": "conflicting"
        }
    ]
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_adj_06_route_requires_reconcile_verdict_forces_compatible_mode():
    case = _load_example()
    case["verdict"]["verdict"] = "route_requires_reconcile"
    case["candidate"]["mode"] = "repair"
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-06: verdict=route_requires_reconcile must force mode in {reconcile, retcon, rollback, quarantine}"


# -- ADJ-07: irreversible step requires human authorization --


def test_adj_07_irreversible_step_requires_human_authorization():
    case = _load_example()
    case["candidate"]["route"][1]["reversibility"] = "irreversible"
    case["candidate"]["requires_human_authorization"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-07: irreversible step forces requires_human_authorization=true"


def test_adj_07_irreversible_with_human_authorization_is_valid():
    case = _load_example()
    case["candidate"]["route"][1]["reversibility"] = "irreversible"
    case["candidate"]["requires_human_authorization"] = True
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_adj_07_policy_require_human_for_irreversible_locked_to_true():
    case = _load_example()
    case["policy"]["require_human_for_irreversible"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-07: policy.require_human_for_irreversible must be const true"


# -- ADJ-08: loop retry requires new evidence --


def test_adj_08_route_requires_evidence_demands_new_evidence_refs():
    case = _load_example()
    case["verdict"]["verdict"] = "route_requires_evidence"
    case["verdict"]["new_evidence_refs"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-08: verdict=route_requires_evidence must require new_evidence_refs minItems:1"


def test_adj_08_policy_forbid_loop_retry_without_new_evidence_locked_to_true():
    case = _load_example()
    case["policy"]["forbid_loop_retry_without_new_evidence"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-08: policy.forbid_loop_retry_without_new_evidence must be const true"


# -- ADJ-10: verifier and release gate required by policy --


def test_adj_10_policy_require_verifier_for_code_change_locked_to_true():
    case = _load_example()
    case["policy"]["require_verifier_for_code_or_memory_change"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-10: policy.require_verifier_for_code_or_memory_change must be const true"


def test_adj_10_policy_require_release_gate_for_canonical_change_locked_to_true():
    case = _load_example()
    case["policy"]["require_release_gate_for_canonical_change"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-10: policy.require_release_gate_for_canonical_change must be const true"


def test_adj_10_candidate_requires_verifier_field_present():
    case = _load_example()
    del case["candidate"]["requires_verifier"]
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-10: candidate.requires_verifier is required"


def test_adj_10_candidate_requires_release_gate_field_present():
    case = _load_example()
    del case["candidate"]["requires_release_gate"]
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-10: candidate.requires_release_gate is required"


# -- Verdict-driven mode consistency --


def test_rollback_recommended_forces_mode_rollback():
    case = _load_example()
    case["verdict"]["verdict"] = "rollback_recommended"
    case["candidate"]["mode"] = "repair"
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=rollback_recommended must force mode=rollback"


def test_hold_insufficient_state_forces_mode_hold():
    case = _load_example()
    case["verdict"]["verdict"] = "hold_insufficient_state"
    case["candidate"]["mode"] = "repair"
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=hold_insufficient_state must force mode=hold"


def test_human_decision_required_forces_requires_human_authorization():
    case = _load_example()
    case["verdict"]["verdict"] = "human_decision_required"
    case["candidate"]["requires_human_authorization"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=human_decision_required must force requires_human_authorization=true"


# -- Enum + structure guards --


def test_unknown_mode_rejected():
    case = _load_example()
    case["candidate"]["mode"] = "fix_everything"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_verdict_rejected():
    case = _load_example()
    case["verdict"]["verdict"] = "done"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_cause_source_rejected():
    case = _load_example()
    case["input"]["inferred_cause"]["source"] = "intuition"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_desired_state_kind_rejected():
    case = _load_example()
    case["input"]["desired_state"]["kind"] = "fix_vibes"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_anchor_level_rejected():
    case = _load_example()
    case["input"]["anchors"][0]["level"] = "L99"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_step_mutability_rejected():
    case = _load_example()
    case["candidate"]["route"][0]["mutability"] = "destroy"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_reversibility_rejected():
    case = _load_example()
    case["candidate"]["route"][0]["reversibility"] = "maybe"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_boundary_kind_rejected():
    case = _load_example()
    case["input"]["boundaries"][0]["kind"] = "vibes"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_evidence_kind_rejected():
    case = _load_example()
    case["candidate"]["expected_evidence_after_apply"][0]["kind"] = "model_assertion"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_risk_scores_must_be_in_unit_interval():
    case = _load_example()
    case["candidate"]["risk"]["boundary_risk"] = 1.5
    errors = list(_validator().iter_errors(case))
    assert errors


def test_all_six_risk_axes_required():
    case = _load_example()
    del case["candidate"]["risk"]["contamination_risk"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_all_five_cost_axes_required():
    case = _load_example()
    del case["candidate"]["cost"]["semantic_cost"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_at_root_rejected():
    case = _load_example()
    case["unexpected_field"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_candidate_rejected():
    case = _load_example()
    case["candidate"]["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_route_step_rejected():
    case = _load_example()
    case["candidate"]["route"][0]["extra"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_no_executor_field_on_candidate():
    """ADJ-09: candidate must not carry executor mutation; the schema
    has no applied_diff / executor_action field at all. Verify by
    attempting to add one and confirming additionalProperties rejects."""
    case = _load_example()
    case["candidate"]["applied_diff"] = "<patch>"
    errors = list(_validator().iter_errors(case))
    assert errors, "ADJ-09: candidate must not carry executor mutation fields"


def test_hold_verdict_with_mode_hold_is_valid():
    case = _load_example()
    case["verdict"]["verdict"] = "hold_insufficient_state"
    case["candidate"]["mode"] = "hold"
    case["candidate"]["route"] = [
        {
            "order": 1,
            "action": "Pause and request additional Mirror evidence",
            "mutability": "read_only",
            "reversibility": "reversible",
            "reason": "Insufficient evidence to choose a route"
        }
    ]
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]
