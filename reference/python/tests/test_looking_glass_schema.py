"""Tests for the Looking-Glass / Adjoint Layer case schema.

Covers:
- the schema itself is valid Draft 2020-12
- the worked example passes
- every existing case in Patch/adjoint_looking_glass_layer_cases/ and
  Patch/adjoint_looking_glass_layer_holdout_cases/ passes
- doc-level invariants are enforced:
    * verdict=reject implies final_reading is one of the two known *_rejected
      readings and claim_status is one of the two blocked_* statuses
    * claim_status=blocked_* implies verdict=reject
    * verdict=supportive implies claim_status starts with allowed_
    * a final_reading of *_rejected requires AntiMagicGuard in operators
- additionalProperties:false on ground_truth and the case root
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
CAP_ROOT = REPO_ROOT / "CAP"
SCHEMA_PATH = CAP_ROOT / "spec" / "looking_glass.schema.json"
EXAMPLE_PATH = CAP_ROOT / "examples" / "looking_glass_case_example.json"
MAIN_CASES_DIR = REPO_ROOT / "Patch" / "adjoint_looking_glass_layer_cases"
HOLDOUT_CASES_DIR = REPO_ROOT / "Patch" / "adjoint_looking_glass_layer_holdout_cases"


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


def _collect_case_paths():
    paths = []
    if MAIN_CASES_DIR.exists():
        paths.extend(sorted(MAIN_CASES_DIR.glob("alg_*.json")))
    if HOLDOUT_CASES_DIR.exists():
        paths.extend(sorted(HOLDOUT_CASES_DIR.glob("alg_*.json")))
    return paths


@pytest.mark.parametrize("case_path", _collect_case_paths(), ids=lambda p: p.name)
def test_existing_case_passes_schema(case_path):
    case = json.loads(case_path.read_text(encoding="utf-8-sig"))
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_reject_verdict_requires_rejected_reading():
    case = _load_example()
    case["ground_truth"]["verdict"] = "reject"
    case["ground_truth"]["final_reading"] = "bounded_retrodiction_and_repair_path_allowed"
    case["ground_truth"]["claim_status"] = "allowed_bounded_repair"
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=reject must require a *_rejected final_reading"


def test_reject_verdict_requires_blocked_claim_status():
    case = _load_example()
    case["ground_truth"]["verdict"] = "reject"
    case["ground_truth"]["final_reading"] = "literal_undo_history_rejected"
    case["ground_truth"]["claim_status"] = "allowed_bounded_repair"
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=reject must require a blocked_* claim_status"


def test_blocked_claim_status_requires_reject_verdict():
    case = _load_example()
    case["ground_truth"]["verdict"] = "supportive"
    case["ground_truth"]["claim_status"] = "blocked_l5_breach_fantasy"
    case["ground_truth"]["final_reading"] = "bounded_retrodiction_and_repair_path_allowed"
    errors = list(_validator().iter_errors(case))
    assert errors, "claim_status=blocked_* must require verdict=reject"


def test_supportive_verdict_rejects_blocked_claim_status():
    case = _load_example()
    case["ground_truth"]["verdict"] = "supportive"
    case["ground_truth"]["claim_status"] = "blocked_no_cost_macro_reverse"
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=supportive must not pair with blocked_* claim_status"


def test_rejected_reading_requires_anti_magic_guard_operator():
    case = _load_example()
    case["ground_truth"]["verdict"] = "reject"
    case["ground_truth"]["final_reading"] = "literal_undo_history_rejected"
    case["ground_truth"]["claim_status"] = "blocked_l5_breach_fantasy"
    case["operators"] = ["Retrodict", "RepairPlan"]
    errors = list(_validator().iter_errors(case))
    assert errors, "*_rejected reading must require AntiMagicGuard in operators"


def test_unknown_operator_rejected():
    case = _load_example()
    case["operators"] = ["NotAnOperator"]
    errors = list(_validator().iter_errors(case))
    assert errors, "operators must be from the closed Looking-Glass alphabet"


def test_unknown_final_reading_rejected():
    case = _load_example()
    case["ground_truth"]["final_reading"] = "totally_made_up_reading"
    errors = list(_validator().iter_errors(case))
    assert errors, "final_reading must be from the enum"


def test_unknown_claim_status_rejected():
    case = _load_example()
    case["ground_truth"]["claim_status"] = "allowed_anything_goes"
    errors = list(_validator().iter_errors(case))
    assert errors, "claim_status must be from the enum"


def test_additional_property_at_root_rejected():
    case = _load_example()
    case["unexpected_field"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors, "additionalProperties:false should reject unknown root fields"


def test_additional_property_in_ground_truth_rejected():
    case = _load_example()
    case["ground_truth"]["extra_field"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors, "additionalProperties:false should reject unknown ground_truth fields"


def test_observed_outcome_severity_required():
    case = _load_example()
    del case["observed_outcome"]["severity"]
    errors = list(_validator().iter_errors(case))
    assert errors, "observed_outcome.severity is required"


def test_family_locked_to_looking_glass_family_or_holdout():
    case = _load_example()
    case["family"] = "memory_dreaming"
    errors = list(_validator().iter_errors(case))
    assert errors, "family must be from the looking_glass family set"
