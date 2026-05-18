"""Tests for the Role Orchestration schema.

Covers the worked example plus the doc-level invariants RO-01..RO-12
from 02_subsystems/role_orchestration.md. Each invariant has a negative
test that confirms the schema rejects the violation.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "role_orchestration.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "role_orchestration_decision_example.json"


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


# -- RO-01: role cannot expand its own authority (policy lock) --


def test_ro_01_policy_allow_self_approval_locked_to_false():
    case = _load_example()
    case["policy"]["allow_self_approval"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-01: policy.allow_self_approval must be const false"


# -- RO-02: author and final verifier must be separated --


def test_ro_02_handoff_verifier_to_verifier_rejected():
    case = _load_example()
    case["decision"]["handoff"]["from_role"] = "verifier"
    case["decision"]["handoff"]["to_role"] = "verifier"
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-02: handoff from verifier to verifier is rejected"


def test_ro_02_handoff_release_governor_to_release_governor_rejected():
    case = _load_example()
    case["decision"]["handoff"]["from_role"] = "release_governor"
    case["decision"]["handoff"]["to_role"] = "release_governor"
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-02: handoff release_governor->release_governor rejected"


def test_ro_02_policy_require_independent_verifier_locked_to_true():
    case = _load_example()
    case["policy"]["require_independent_verifier"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-02: policy.require_independent_verifier must be const true"


# -- RO-03: verifier is read-only (no mutate, no release) --


def test_ro_03_verifier_profile_cannot_mutate():
    case = _load_example()
    for profile in case["input"]["available_roles"]:
        if profile["role"] == "verifier":
            profile["may_mutate"] = True
            break
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-03: verifier profile cannot have may_mutate=true"


def test_ro_03_verifier_profile_cannot_release():
    case = _load_example()
    for profile in case["input"]["available_roles"]:
        if profile["role"] == "verifier":
            profile["may_release"] = True
            break
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-03: verifier profile cannot have may_release=true"


# -- RO-04: release governor does not authorize physical action --


def test_ro_04_release_governor_cannot_authorize():
    case = _load_example()
    for profile in case["input"]["available_roles"]:
        if profile["role"] == "release_governor":
            profile["may_authorize"] = True
            break
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-04: release_governor profile cannot have may_authorize=true"


# -- RO-05: human authorization required for irreversible / execute --


def test_ro_05_execute_action_requires_executor_to_role():
    case = _load_example()
    case["decision"]["handoff"]["allowed_next_actions"] = ["execute"]
    case["decision"]["handoff"]["to_role"] = "coder"
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-05: execute in allowed_next_actions requires to_role=executor"


def test_ro_05_execute_requires_return_to_human_authority():
    case = _load_example()
    case["decision"]["handoff"]["allowed_next_actions"] = ["execute"]
    case["decision"]["handoff"]["to_role"] = "executor"
    case["decision"]["handoff"]["requires_return_to_role"] = "coder"
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-05: execute requires requires_return_to_role=human_authority"


def test_ro_05_policy_require_human_for_irreversible_locked_to_true():
    case = _load_example()
    case["policy"]["require_human_for_irreversible"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-05: policy.require_human_for_irreversible must be const true"


# -- RO-06: handoff preserves evidence and rejected hypotheses --


def test_ro_06_handoff_evidence_refs_minimum_one():
    case = _load_example()
    case["decision"]["handoff"]["evidence_refs"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-06: handoff.evidence_refs minItems:1"


def test_ro_06_handoff_rejected_hypotheses_required():
    case = _load_example()
    del case["decision"]["handoff"]["rejected_hypotheses"]
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-06: handoff.rejected_hypotheses is a required array"


def test_ro_06_policy_preserve_handoff_evidence_locked_to_true():
    case = _load_example()
    case["policy"]["preserve_handoff_evidence"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-06: policy.preserve_handoff_evidence must be const true"


# -- RO-07: handoff must reference at least one upstream state --


def test_ro_07_handoff_input_state_refs_minimum_one_property():
    case = _load_example()
    case["decision"]["handoff"]["input_state_refs"] = {}
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-07: input_state_refs requires at least one upstream ref"


# -- RO-09: uiux scope must not leak into runtime / governance --


def test_ro_09_uiux_must_forbid_runtime_scope():
    case = _load_example()
    for profile in case["input"]["available_roles"]:
        if profile["role"] == "uiux":
            profile["forbidden_scopes"] = ["governance"]
            break
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-09: uiux must forbid 'runtime' scope"


def test_ro_09_uiux_must_forbid_governance_scope():
    case = _load_example()
    for profile in case["input"]["available_roles"]:
        if profile["role"] == "uiux":
            profile["forbidden_scopes"] = ["runtime"]
            break
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-09: uiux must forbid 'governance' scope"


def test_ro_09_policy_enforce_role_scope_locked_to_true():
    case = _load_example()
    case["policy"]["enforce_role_scope"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-09: policy.enforce_role_scope must be const true"


# -- RO-10: decision is routing, not quality (no truth fields) --


def test_ro_10_decision_has_no_release_pass_field():
    case = _load_example()
    case["decision"]["passes_release"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-10: decision must not carry release/quality verdict fields"


def test_ro_10_decision_has_no_evidence_validated_field():
    case = _load_example()
    case["decision"]["evidence_validated"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-10: decision must not carry evidence_validated field"


# -- RO-11: loop continuation forbidden when loop_signal_count > 0 --


def test_ro_11_continue_current_role_forbidden_with_loop_signals():
    case = _load_example()
    case["input"]["loop_signal_count"] = 2
    case["decision"]["mode"] = "continue_current_role"
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-11: continue_current_role forbidden when loop_signal_count > 0"


def test_ro_11_continue_current_role_allowed_with_no_loop_signals():
    case = _load_example()
    case["input"]["loop_signal_count"] = 0
    case["decision"]["mode"] = "continue_current_role"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_ro_11_policy_interrupt_loops_locked_to_true():
    case = _load_example()
    case["policy"]["interrupt_loops"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-11: policy.interrupt_loops must be const true"


# -- RO-12: role outputs are typed --


def test_ro_12_role_profile_output_contract_minimum_one():
    case = _load_example()
    case["input"]["available_roles"][0]["output_contract"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "RO-12: every role profile must declare at least one output_contract entry"


# -- Enum + structure guards --


def test_unknown_role_rejected():
    case = _load_example()
    case["decision"]["selected_role"] = "supreme_overlord"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_decision_mode_rejected():
    case = _load_example()
    case["decision"]["mode"] = "ignore"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_role_action_rejected():
    case = _load_example()
    case["decision"]["handoff"]["allowed_next_actions"] = ["wish"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_orchestration_mode_rejected():
    case = _load_example()
    case["policy"]["mode"] = "chaos"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_max_autonomy_rejected():
    case = _load_example()
    case["input"]["available_roles"][0]["max_autonomy"] = "godlike"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_scope_rule_rejected():
    case = _load_example()
    case["input"]["available_roles"][0]["forbidden_scopes"] = ["sphere"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_at_root_rejected():
    case = _load_example()
    case["unexpected_field"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_decision_rejected():
    case = _load_example()
    case["decision"]["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_handoff_rejected():
    case = _load_example()
    case["decision"]["handoff"]["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_confidence_must_be_in_unit_interval():
    case = _load_example()
    case["decision"]["confidence"] = 1.5
    errors = list(_validator().iter_errors(case))
    assert errors


def test_available_roles_minimum_one():
    case = _load_example()
    case["input"]["available_roles"] = []
    errors = list(_validator().iter_errors(case))
    assert errors


def test_decision_without_handoff_for_hold_mode_is_valid():
    """hold mode does not require a handoff; the schema allows handoff
    to be omitted on hold."""
    case = _load_example()
    case["decision"].pop("handoff", None)
    case["decision"]["mode"] = "hold"
    case["decision"]["reason"] = "Insufficient state; refresh Mirror before next role"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]
