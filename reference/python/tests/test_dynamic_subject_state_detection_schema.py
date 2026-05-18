"""Tests for the Dynamic Subject-State Detection schema.

Covers the worked example plus the doc-level invariants DSSD-01..DSSD-10
from 02_subsystems/dynamic_subject_state_detection.md. Each invariant
has a negative test that confirms the schema rejects the violation.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "dynamic_subject_state_detection.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "subject_state_frame_example.json"


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


# -- DSSD-01: state is per-frame, not per-actor --


def test_dssd_01_frame_has_required_detected_state():
    case = _load_example()
    del case["frame"]["detected_state"]
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-01: frame.detected_state is required"


def test_dssd_01_policy_require_mirror_for_state_claims_locked_to_true():
    case = _load_example()
    case["policy"]["require_mirror_for_state_claims"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-01: policy.require_mirror_for_state_claims must be const true"


# -- DSSD-02: confidence is not authority --


def test_dssd_02_policy_allow_model_as_release_authority_locked_to_false():
    case = _load_example()
    case["policy"]["allow_model_as_release_authority"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-02: policy.allow_model_as_release_authority must be const false"


# -- DSSD-03: tool actor cannot be release_authority_required --


def test_dssd_03_tool_actor_cannot_be_release_authority():
    case = _load_example()
    case["input"]["actor_kind"] = "tool"
    case["frame"]["actor_kind"] = "tool"
    case["frame"]["detected_state"] = "release_authority_required"
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-03: actor_kind=tool cannot be classified as release_authority_required"


# -- DSSD-04: policy requires independent verifier for code seal --


def test_dssd_04_policy_require_independent_verifier_locked_to_true():
    case = _load_example()
    case["policy"]["require_independent_verifier_for_code_seal"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-04: policy.require_independent_verifier_for_code_seal must be const true"


# -- DSSD-05: bounded subject canonicalization must escalate --


def test_dssd_05_bounded_with_canonicalization_attempt_must_escalate_release_gate():
    case = _load_example()
    case["frame"]["detected_state"] = "bounded_subject_state"
    case["frame"]["risk_signals"] = ["canonicalization_attempt"]
    case["frame"]["required_escalation"] = "mirror_refresh"
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-05: bounded + canonicalization_attempt must escalate to release_gate or human_authorization"


def test_dssd_05_bounded_with_canonicalization_and_release_gate_is_valid():
    case = _load_example()
    case["frame"]["detected_state"] = "bounded_subject_state"
    case["frame"]["risk_signals"] = ["canonicalization_attempt"]
    case["frame"]["required_escalation"] = "release_gate"
    case["frame"].pop("audit_log_ref", None)
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_dssd_05_policy_require_release_gate_for_canonicalization_locked_to_true():
    case = _load_example()
    case["policy"]["require_release_gate_for_canonicalization"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-05: policy.require_release_gate_for_canonicalization must be const true"


# -- DSSD-06: irreversible attempt forces human_authorization escalation --


def test_dssd_06_irreversible_attempt_forces_human_authorization():
    case = _load_example()
    case["frame"]["risk_signals"] = ["irreversible_action_attempt"]
    case["frame"]["required_escalation"] = "verifier"
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-06: irreversible_action_attempt forces required_escalation=human_authorization"


def test_dssd_06_policy_require_human_for_irreversible_locked_to_true():
    case = _load_example()
    case["policy"]["require_human_for_irreversible"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-06: policy.require_human_for_irreversible must be const true"


# -- DSSD-07: pseudo_subject_state requires guardrail escalation --


def test_dssd_07_pseudo_subject_requires_guardrail_escalation():
    case = _load_example()
    case["frame"]["detected_state"] = "pseudo_subject_state"
    case["frame"]["required_escalation"] = "context_hygiene"
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-07: pseudo_subject_state requires escalation in {verifier, release_gate, human_authorization}"


def test_dssd_07_pseudo_subject_without_escalation_rejected():
    case = _load_example()
    case["frame"]["detected_state"] = "pseudo_subject_state"
    case["frame"].pop("required_escalation", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-07: pseudo_subject_state requires required_escalation"


def test_dssd_07_policy_allow_self_approval_locked_to_false():
    case = _load_example()
    case["policy"]["allow_self_approval"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-07: policy.allow_self_approval must be const false"


# -- DSSD-08: looping_system_state requires context_hygiene escalation --


def test_dssd_08_looping_system_requires_context_hygiene():
    case = _load_example()
    case["frame"]["detected_state"] = "looping_system_state"
    case["frame"]["required_escalation"] = "verifier"
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-08: looping_system_state requires required_escalation=context_hygiene"


def test_dssd_08_policy_require_anti_loop_locked_to_true():
    case = _load_example()
    case["policy"]["require_anti_loop_on_looping_system"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-08: policy.require_anti_loop_on_looping_system must be const true"


# -- DSSD-09: sphere_probe forbids release-class actions --


def test_dssd_09_sphere_probe_requires_release_forbidden():
    case = _load_example()
    case["frame"]["detected_state"] = "sphere_probe_state"
    case["frame"]["forbidden_next_actions"] = ["increase_scope"]
    case["frame"].pop("audit_log_ref", None)
    case["frame"].pop("required_escalation", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-09: sphere_probe_state must forbid release | canonicalize_memory | git_seal | external_publication"


def test_dssd_09_sphere_probe_with_release_forbidden_is_valid():
    case = _load_example()
    case["frame"]["detected_state"] = "sphere_probe_state"
    case["frame"]["forbidden_next_actions"] = [
        "release",
        "git_seal",
        "canonicalize_memory"
    ]
    case["frame"].pop("audit_log_ref", None)
    case["frame"].pop("required_escalation", None)
    case["frame"]["risk_signals"] = []
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


# -- DSSD-10: high-risk states require audit_log_ref --


def test_dssd_10_pseudo_subject_requires_audit_log_ref():
    case = _load_example()
    del case["frame"]["audit_log_ref"]
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-10: pseudo_subject_state requires audit_log_ref"


def test_dssd_10_release_authority_required_state_requires_audit_log_ref():
    case = _load_example()
    case["frame"]["detected_state"] = "release_authority_required"
    case["frame"]["required_escalation"] = "release_gate"
    case["frame"].pop("audit_log_ref", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-10: release_authority_required requires audit_log_ref"


def test_dssd_10_human_subject_required_state_requires_audit_log_ref():
    case = _load_example()
    case["frame"]["detected_state"] = "human_subject_required"
    case["frame"]["required_escalation"] = "human_authorization"
    case["frame"].pop("audit_log_ref", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "DSSD-10: human_subject_required requires audit_log_ref"


def test_dssd_10_object_state_does_not_require_audit_log_ref():
    case = _load_example()
    case["frame"]["detected_state"] = "object_state"
    case["frame"]["risk_signals"] = []
    case["frame"].pop("audit_log_ref", None)
    case["frame"].pop("required_escalation", None)
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


# -- Enum + structure guards --


def test_unknown_detected_state_rejected():
    case = _load_example()
    case["frame"]["detected_state"] = "enlightened_state"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_actor_kind_rejected():
    case = _load_example()
    case["frame"]["actor_kind"] = "ghost"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_risk_signal_rejected():
    case = _load_example()
    case["frame"]["risk_signals"] = ["bad_vibes"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_capability_signal_rejected():
    case = _load_example()
    case["frame"]["capability_signals"] = ["wisdom"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_required_escalation_rejected():
    case = _load_example()
    case["frame"]["required_escalation"] = "vibe_check"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_behavior_kind_rejected():
    case = _load_example()
    case["input"]["observed_behavior"][0]["kind"] = "meditates"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_axis_scores_must_be_in_unit_interval():
    case = _load_example()
    case["frame"]["axis_scores"]["goal_ownership"] = 1.5
    errors = list(_validator().iter_errors(case))
    assert errors


def test_all_eight_axes_required():
    case = _load_example()
    del case["frame"]["axis_scores"]["context_hygiene"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_at_root_rejected():
    case = _load_example()
    case["unexpected_field"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_frame_rejected():
    case = _load_example()
    case["frame"]["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_confidence_must_be_in_unit_interval():
    case = _load_example()
    case["frame"]["confidence"] = 1.5
    errors = list(_validator().iter_errors(case))
    assert errors


def test_bounded_subject_with_clean_state_is_valid():
    case = _load_example()
    case["frame"]["detected_state"] = "bounded_subject_state"
    case["frame"]["risk_signals"] = []
    case["frame"]["capability_signals"] = ["boundary_awareness", "evidence_separation"]
    case["frame"]["forbidden_next_actions"] = ["git_seal", "canonicalize_memory"]
    case["frame"].pop("audit_log_ref", None)
    case["frame"].pop("required_escalation", None)
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]
