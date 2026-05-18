"""Tests for the Latent Cause Reconstruction case schema.

Covers:
- the schema itself is valid Draft 2020-12
- the worked example passes
- every existing case in Patch/latent_cause_reconstruction_cases/ passes
- doc-level invariants are enforced:
    * verdict=reject implies final_reading is one of the three known *_rejected
      readings (trigger_as_cause, moralizing_fantasy, emotional_trigger_overweight)
    * trigger_status=trigger_collapsed_into_cause implies verdict=reject
    * cause_status in {invalid_cause_requires_fantasy, trigger_misclassified_as_cause}
      implies verdict=reject
    * repair_order in {invalid_moralizing_repair, invalid_symptom_first_repair}
      implies verdict=reject
- additionalProperties:false on ground_truth and the case root
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
CAP_ROOT = REPO_ROOT / "CAP"
SCHEMA_PATH = CAP_ROOT / "spec" / "latent_cause_reconstruction.schema.json"
EXAMPLE_PATH = CAP_ROOT / "examples" / "latent_cause_reconstruction_case_example.json"
CASES_DIR = REPO_ROOT / "Patch" / "latent_cause_reconstruction_cases"


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
    if CASES_DIR.exists():
        return sorted(CASES_DIR.glob("lcr_*.json"))
    return []


@pytest.mark.parametrize("case_path", _collect_case_paths(), ids=lambda p: p.name)
def test_existing_case_passes_schema(case_path):
    case = json.loads(case_path.read_text(encoding="utf-8-sig"))
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_reject_verdict_requires_rejected_reading():
    case = _load_example()
    case["ground_truth"]["verdict"] = "reject"
    case["ground_truth"]["final_reading"] = "latent_resource_leakage_detected"
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=reject must require a *_rejected final_reading"


def test_trigger_collapsed_requires_reject_verdict():
    case = _load_example()
    case["ground_truth"]["verdict"] = "supportive"
    case["ground_truth"]["trigger_status"] = "trigger_collapsed_into_cause"
    errors = list(_validator().iter_errors(case))
    assert errors, "trigger_status=trigger_collapsed_into_cause must require verdict=reject"


def test_invalid_cause_status_requires_reject_verdict():
    case = _load_example()
    case["ground_truth"]["verdict"] = "supportive"
    case["ground_truth"]["cause_status"] = "invalid_cause_requires_fantasy"
    errors = list(_validator().iter_errors(case))
    assert errors, "cause_status=invalid_cause_requires_fantasy must require verdict=reject"


def test_trigger_misclassified_requires_reject_verdict():
    case = _load_example()
    case["ground_truth"]["verdict"] = "supportive"
    case["ground_truth"]["cause_status"] = "trigger_misclassified_as_cause"
    errors = list(_validator().iter_errors(case))
    assert errors, "cause_status=trigger_misclassified_as_cause must require verdict=reject"


def test_invalid_moralizing_repair_requires_reject_verdict():
    case = _load_example()
    case["ground_truth"]["verdict"] = "supportive"
    case["ground_truth"]["repair_order"] = "invalid_moralizing_repair"
    errors = list(_validator().iter_errors(case))
    assert errors, "repair_order=invalid_moralizing_repair must require verdict=reject"


def test_invalid_symptom_first_repair_requires_reject_verdict():
    case = _load_example()
    case["ground_truth"]["verdict"] = "supportive"
    case["ground_truth"]["repair_order"] = "invalid_symptom_first_repair"
    errors = list(_validator().iter_errors(case))
    assert errors, "repair_order=invalid_symptom_first_repair must require verdict=reject"


def test_unknown_operator_rejected():
    case = _load_example()
    case["operators"] = ["NotAnOperator"]
    errors = list(_validator().iter_errors(case))
    assert errors, "operators must be from the closed A-Reconstruction alphabet"


def test_unknown_final_reading_rejected():
    case = _load_example()
    case["ground_truth"]["final_reading"] = "totally_made_up_reading"
    errors = list(_validator().iter_errors(case))
    assert errors, "final_reading must be from the enum"


def test_unknown_anti_banality_guard_rejected():
    case = _load_example()
    case["ground_truth"]["anti_banality_guard"] = "not_universal_advice"
    errors = list(_validator().iter_errors(case))
    assert errors, "anti_banality_guard must be from the enum"


def test_observed_rupture_requires_damage_vector():
    case = _load_example()
    del case["observed_rupture"]["damage_vector"]
    errors = list(_validator().iter_errors(case))
    assert errors, "observed_rupture must require damage_vector"


def test_candidate_causes_min_items():
    case = _load_example()
    case["candidate_causes"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "candidate_causes must have minItems:1"


def test_family_locked_to_latent_cause_reconstruction():
    case = _load_example()
    case["family"] = "memory_dreaming"
    errors = list(_validator().iter_errors(case))
    assert errors, "family must be const latent_cause_reconstruction"


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
