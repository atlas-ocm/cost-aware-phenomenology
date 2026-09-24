"""Tests for the Transition Execution Record schema.

Covers the worked example plus the schema-level invariants of an
EXECUTED-transition record: a postcondition defined before execution,
provenance that requires a stored receipt and hashed inputs, checks that
must agree with their exit codes, and measured costs kept apart from
estimates. Each invariant has a negative test that confirms the schema
rejects the violation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "transition_execution.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "transition_execution_record_example.json"


def _load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_example():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8-sig"))


def _validator():
    return jsonschema.Draft202012Validator(_load_schema())


def test_schema_is_valid_draft_2020_12():
    jsonschema.Draft202012Validator.check_schema(_load_schema())


def test_schema_id_is_the_expected_urn():
    assert _load_schema()["$id"] == "urn:cap:schema:transition-execution:v0.1"


def test_worked_example_passes():
    errors = sorted(_validator().iter_errors(_load_example()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_example_input_sha256_matches_referenced_file():
    case = _load_example()
    entry = case["execution"]["inputs"][0]
    target = ROOT / entry["ref"]
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    assert entry["sha256"] == digest


# -- before: postcondition defined before execution --


def test_defined_before_execution_must_be_true():
    case = _load_example()
    case["postcondition"]["defined_before_execution"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "postcondition.defined_before_execution must be const true"


def test_empty_criteria_rejected():
    case = _load_example()
    case["postcondition"]["criteria"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "postcondition.criteria minItems:1"


# -- during: actor identity --


def test_identity_independently_verified_is_required():
    case = _load_example()
    del case["execution"]["actor"]["identity_independently_verified"]
    errors = list(_validator().iter_errors(case))
    assert errors, "execution.actor.identity_independently_verified is required"


def test_malformed_sha256_rejected():
    case = _load_example()
    case["execution"]["inputs"][0]["sha256"] = "not-a-sha256"
    errors = list(_validator().iter_errors(case))
    assert errors, "execution.inputs[].sha256 must be 64 lowercase hex characters"


# -- after: checks agree with their exit codes --


def test_passing_check_with_nonzero_exit_code_rejected():
    case = _load_example()
    case["checks"][0]["exit_code"] = 1
    errors = list(_validator().iter_errors(case))
    assert errors, "a check with status pass must have exit_code 0"


def test_unknown_check_status_rejected():
    case = _load_example()
    case["checks"][0]["status"] = "skipped"
    errors = list(_validator().iter_errors(case))
    assert errors, "check.status enum must not include 'skipped'"


# -- verdict-driven invariants --


def test_postcondition_met_true_with_failing_check_rejected():
    case = _load_example()
    case["checks"][0]["status"] = "fail"
    case["checks"][0]["exit_code"] = 1
    errors = list(_validator().iter_errors(case))
    assert errors, "postcondition_met=true requires every check status to be pass"


def test_provenance_established_true_without_receipt_ref_rejected():
    case = _load_example()
    del case["execution"]["receipt_ref"]
    errors = list(_validator().iter_errors(case))
    assert errors, "provenance_established=true requires execution.receipt_ref"


def test_provenance_established_true_with_empty_inputs_rejected():
    case = _load_example()
    case["execution"]["inputs"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "provenance_established=true requires execution.inputs minItems:1"


# -- feedback: measured costs apart from estimates --


def test_missing_measured_money_rejected():
    case = _load_example()
    del case["costs"]["measured"]["money"]
    errors = list(_validator().iter_errors(case))
    assert errors, "costs.measured.money is required"


def test_unknown_money_string_rejected():
    case = _load_example()
    case["costs"]["measured"]["money"] = "cheap"
    errors = list(_validator().iter_errors(case))
    assert errors, "costs.measured.money must be 'unknown' or a number"


def test_money_unknown_accepted():
    case = _load_example()
    case["costs"]["measured"]["money"] = "unknown"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_money_number_accepted():
    case = _load_example()
    case["costs"]["measured"]["money"] = 0.42
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


# -- structure guards --


def test_additional_property_at_root_rejected():
    case = _load_example()
    case["unexpected_field"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_check_rejected():
    case = _load_example()
    case["checks"][0]["extra"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unresolvable_candidate_ref_still_passes_schema():
    """Boundary: the schema constrains shape, not resolvability. A
    candidate_ref that points at no file is still schema-valid; resolving
    it is a validator's job, added separately."""
    case = _load_example()
    case["candidate"]["candidate_ref"] = "examples/does_not_exist_candidate.json"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]
