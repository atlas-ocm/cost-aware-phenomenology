"""Tests for the Release Gate schema.

Covers the worked example plus the doc-level invariants RG-01..RG-10 from
02_subsystems/release_gate.md. Each invariant is exercised as a negative
test that confirms the schema rejects the violation.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "release_gate.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "release_gate_result_example.json"


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


# -- RG-01: candidate cannot release itself --


def test_rg_01_release_gate_cannot_be_author():
    case = _load_example()
    case["candidate"]["author_role"] = "release_gate"
    errors = list(_validator().iter_errors(case))
    assert errors, "RG-01: author_role must not equal release_gate"


def test_rg_01_pass_requires_verifier_verdict_on_candidate():
    case = _load_example()
    del case["candidate"]["verifier_verdict"]
    errors = list(_validator().iter_errors(case))
    assert errors, "RG-01: verdict=pass requires verifier_verdict on candidate"


def test_rg_01_policy_locks_allow_model_self_approval_to_false():
    case = _load_example()
    case["policy"]["allow_model_self_approval"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "RG-01 reified: allow_model_self_approval must be const false"


# -- RG-04: missing evidence cannot produce pass --


def test_rg_04_pass_requires_non_empty_evidence():
    case = _load_example()
    case["candidate"]["evidence"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "RG-04: verdict=pass requires evidence minItems:1"


# -- RG-05: anchor conflict with pass requires reconcile_anchors action --


def test_rg_05_anchor_conflict_with_pass_requires_reconcile_action():
    case = _load_example()
    case["result"]["anchor_conflicts"] = [
        {
            "anchor_id": "anchor_x",
            "anchor_level": "L1-C",
            "reason": "candidate contradicts canonical policy line"
        }
    ]
    case["result"]["recommended_next_action"] = "release"
    errors = list(_validator().iter_errors(case))
    assert errors, "RG-05: pass with anchor_conflicts must set recommended_next_action=reconcile_anchors"


def test_rg_05_anchor_conflict_with_reconcile_action_is_valid():
    case = _load_example()
    case["result"]["anchor_conflicts"] = [
        {
            "anchor_id": "anchor_x",
            "anchor_level": "L1-C",
            "reason": "candidate contradicts canonical policy line",
            "reconcile_path_available": True
        }
    ]
    case["result"]["recommended_next_action"] = "reconcile_anchors"
    errors = list(_validator().iter_errors(case))
    assert not errors, [e.message for e in errors]


# -- RG-06: irreversible + pass requires authorizations --


def test_rg_06_irreversible_pass_requires_authorizations():
    case = _load_example()
    case["result"]["reversible"] = False
    case["result"]["required_authorizations"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "RG-06: reversible=false + pass requires required_authorizations minItems:1"


def test_rg_06_irreversible_pass_with_authorization_is_valid():
    case = _load_example()
    case["result"]["reversible"] = False
    case["result"]["required_authorizations"] = ["human_operator_approval:2026-05-18"]
    errors = list(_validator().iter_errors(case))
    assert not errors, [e.message for e in errors]


# -- RG-08: pass requires audit_log_ref --


def test_rg_08_pass_requires_audit_log_ref():
    case = _load_example()
    del case["result"]["audit_log_ref"]
    errors = list(_validator().iter_errors(case))
    assert errors, "RG-08: verdict=pass requires audit_log_ref"


# -- RG-09: verifier role must not be author --


def test_rg_09_verifier_role_cannot_be_author():
    case = _load_example()
    case["candidate"]["verifier_verdict"]["role"] = "author"
    errors = list(_validator().iter_errors(case))
    assert errors, "RG-09: verifier role must not equal author"


# -- RG-10: boundary violation dominates quality --


def test_rg_10_boundary_violation_forces_blocked():
    case = _load_example()
    case["result"]["boundary_violations"] = [
        {
            "boundary": "repo_identity",
            "reason": "candidate targets a different repo than the verified one"
        }
    ]
    case["result"]["verdict"] = "pass"
    errors = list(_validator().iter_errors(case))
    assert errors, "RG-10: any boundary_violation forces verdict=blocked"


def test_rg_10_boundary_violation_with_blocked_is_valid():
    case = _load_example()
    case["result"]["verdict"] = "blocked"
    case["result"]["boundary_violations"] = [
        {
            "boundary": "repo_identity",
            "reason": "candidate targets a different repo than the verified one"
        }
    ]
    case["result"]["recommended_next_action"] = "block"
    case["result"]["confidence"] = 1.0
    case["result"]["reasons"] = ["repo identity boundary violated"]
    case["result"].pop("audit_log_ref", None)
    errors = list(_validator().iter_errors(case))
    assert not errors, [e.message for e in errors]


# -- Verdict / target / role enums --


def test_unknown_verdict_rejected():
    case = _load_example()
    case["result"]["verdict"] = "maybe"
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict must be from the canonical enum"


def test_legacy_release_alias_not_accepted_at_schema_level():
    """The doc maps `release == pass` as a verbal equivalence; the schema
    itself only accepts the canonical lowercase enum. Proxy code that
    emits `release` must translate at the boundary."""
    case = _load_example()
    case["result"]["verdict"] = "release"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_target_rejected():
    case = _load_example()
    case["candidate"]["target"] = "rogue_target"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_evidence_kind_rejected():
    case = _load_example()
    case["candidate"]["evidence"][0]["kind"] = "model_self_statement"
    errors = list(_validator().iter_errors(case))
    assert errors, "RG-02 reified: evidence_kind must be from the closed enum (no bare model statements)"


def test_additional_property_at_root_rejected():
    case = _load_example()
    case["unexpected_field"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_result_rejected():
    case = _load_example()
    case["result"]["extra"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_confidence_must_be_in_unit_interval():
    case = _load_example()
    case["result"]["confidence"] = 1.5
    errors = list(_validator().iter_errors(case))
    assert errors


def test_needs_fix_does_not_require_audit_log_ref():
    case = _load_example()
    case["result"]["verdict"] = "needs_fix"
    case["result"].pop("audit_log_ref", None)
    case["result"]["recommended_next_action"] = "revise"
    errors = list(_validator().iter_errors(case))
    assert not errors, [e.message for e in errors]


def test_blocked_does_not_require_audit_log_ref():
    case = _load_example()
    case["result"]["verdict"] = "blocked"
    case["result"].pop("audit_log_ref", None)
    case["result"]["recommended_next_action"] = "block"
    errors = list(_validator().iter_errors(case))
    assert not errors, [e.message for e in errors]
