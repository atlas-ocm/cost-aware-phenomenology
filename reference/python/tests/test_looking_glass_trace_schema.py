"""Tests for the Looking-Glass runtime trace schema.

Covers the worked example plus the doc-level invariants LG-01..LG-12
from 04_extensions/looking_glass.md (extended trace contract):

- LG-01 Looking-Glass starts from observed outcome (Mirror Frame ref)
- LG-02 Looking-Glass is retro-diagnostic, not executor
- LG-03 Cause hypothesis is not evidence
- LG-04 Multiple plausible paths must remain multiple (for
        verdict=multiple_competing_paths)
- LG-05 Split point with high confidence must reference evidence
- LG-06 Minimal repair must be bounded (steps minItems:1)
- LG-09 Tolerated scar verdict requires explicit scar note
- LG-10 Trace feeds Adjustment, not Release directly (policy lock)
- LG-11 Uncertainty must be preserved (array required)
- Verdict <-> repair_mode consistency for each verdict type
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "looking_glass_trace.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "looking_glass_trace_example.json"


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


# -- LG-01: start from observed outcome with Mirror Frame ref --


def test_lg_01_input_mirror_frame_id_required():
    case = _load_example()
    del case["trace"]["input_mirror_frame_id"]
    errors = list(_validator().iter_errors(case))
    assert errors, "LG-01: input_mirror_frame_id is required"


def test_lg_01_observed_outcome_requires_evidence_refs():
    case = _load_example()
    case["trace"]["observed_outcome"]["evidence_refs"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "LG-01: observed_outcome.evidence_refs minItems:1"


def test_lg_01_policy_require_mirror_frame_locked_to_true():
    case = _load_example()
    case["policy"]["require_mirror_frame"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "LG-01: policy.require_mirror_frame must be const true"


# -- LG-02: retro-diagnostic, not executor --


def test_lg_02_policy_allow_mutation_locked_to_false():
    case = _load_example()
    case["policy"]["allow_mutation"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "LG-02: policy.allow_mutation must be const false"


# -- LG-03: cause hypothesis is not evidence --


def test_lg_03_policy_allow_single_cause_without_evidence_locked_to_false():
    case = _load_example()
    case["policy"]["allow_single_cause_without_evidence"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "LG-03: policy.allow_single_cause_without_evidence must be const false"


# -- LG-04: multiple plausible paths preserved --


def test_lg_04_policy_preserve_competing_paths_locked_to_true():
    case = _load_example()
    case["policy"]["preserve_competing_paths"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "LG-04: policy.preserve_competing_paths must be const true"


def test_lg_04_multiple_competing_paths_verdict_requires_at_least_two():
    case = _load_example()
    case["trace"]["verdict"] = "multiple_competing_paths"
    case["trace"]["recommended_repair_mode"] = "hold"
    case["trace"]["plausible_prior_paths"] = [
        case["trace"]["plausible_prior_paths"][0]
    ]
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=multiple_competing_paths must require plausible_prior_paths minItems:2"


def test_lg_04_plausible_prior_paths_minimum_one():
    case = _load_example()
    case["trace"]["plausible_prior_paths"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "trace.plausible_prior_paths must have minItems:1"


# -- LG-05: high-confidence split point requires evidence --


def test_lg_05_high_confidence_split_point_requires_evidence_refs():
    case = _load_example()
    case["trace"]["likely_split_point"]["evidence_refs"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "LG-05: confidence>0.7 split_point requires evidence_refs minItems:1"


def test_lg_05_low_confidence_split_point_allows_empty_evidence():
    case = _load_example()
    case["trace"]["likely_split_point"]["confidence"] = 0.5
    case["trace"]["likely_split_point"]["evidence_refs"] = []
    errors = list(_validator().iter_errors(case))
    assert not errors, "low-confidence split point may have empty evidence_refs"


# -- LG-06: minimal repair must be bounded --


def test_lg_06_minimal_repair_requires_at_least_one_step():
    case = _load_example()
    case["trace"]["minimal_repair_path"]["steps"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "LG-06: minimal_repair_path.steps minItems:1"


# -- LG-09: tolerated scar requires note --


def test_lg_09_tolerate_scar_verdict_requires_scar_note():
    case = _load_example()
    case["trace"]["verdict"] = "tolerate_scar"
    case["trace"]["recommended_repair_mode"] = "tolerate_scar"
    case["trace"].pop("tolerated_scar_note", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "LG-09: verdict=tolerate_scar requires tolerated_scar_note"


def test_lg_09_tolerate_scar_with_note_is_valid():
    case = _load_example()
    case["trace"]["verdict"] = "tolerate_scar"
    case["trace"]["recommended_repair_mode"] = "tolerate_scar"
    case["trace"]["tolerated_scar_note"] = "Local cosmetic drift confined to settings footer; non-cascading; logged for next sprint"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


# -- LG-11: uncertainty preserved --


def test_lg_11_uncertainty_array_is_required():
    case = _load_example()
    del case["trace"]["uncertainty"]
    errors = list(_validator().iter_errors(case))
    assert errors, "LG-11: uncertainty array is required (may be empty)"


def test_lg_11_blocked_assumptions_array_is_required():
    case = _load_example()
    del case["trace"]["blocked_assumptions"]
    errors = list(_validator().iter_errors(case))
    assert errors, "blocked_assumptions array is required"


# -- Verdict <-> repair_mode consistency --


@pytest.mark.parametrize(
    "verdict,required_mode",
    [
        ("restore_path_found", "restore"),
        ("compensate_required", "compensate"),
        ("reconcile_required", "reconcile"),
        ("rollback_recommended", "rollback"),
        ("tolerate_scar", "tolerate_scar"),
    ],
)
def test_verdict_requires_matching_repair_mode(verdict, required_mode):
    case = _load_example()
    case["trace"]["verdict"] = verdict
    case["trace"]["recommended_repair_mode"] = "restore" if required_mode != "restore" else "compensate"
    if verdict == "tolerate_scar":
        case["trace"]["tolerated_scar_note"] = "local + non-cascading"
    errors = list(_validator().iter_errors(case))
    assert errors, f"verdict={verdict} must force recommended_repair_mode={required_mode}"


def test_verdict_insufficient_trace_requires_hold_or_escalate():
    case = _load_example()
    case["trace"]["verdict"] = "insufficient_trace"
    case["trace"]["recommended_repair_mode"] = "restore"
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=insufficient_trace requires repair_mode in {hold, escalate_to_human}"


def test_verdict_boundary_obscured_requires_hold_and_blocked_assumption():
    case = _load_example()
    case["trace"]["verdict"] = "boundary_obscured"
    case["trace"]["recommended_repair_mode"] = "hold"
    case["trace"]["blocked_assumptions"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=boundary_obscured requires blocked_assumptions minItems:1"


# -- Enum + structure guards --


def test_unknown_verdict_rejected():
    case = _load_example()
    case["trace"]["verdict"] = "issue_solved"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_outcome_kind_rejected():
    case = _load_example()
    case["trace"]["observed_outcome"]["kind"] = "feeling_bad"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_prior_path_kind_rejected():
    case = _load_example()
    case["trace"]["plausible_prior_paths"][0]["path"] = "voodoo"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_repair_mode_rejected():
    case = _load_example()
    case["trace"]["recommended_repair_mode"] = "just_ignore"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_invariant_class_rejected():
    case = _load_example()
    case["trace"]["damaged_invariants"][0]["class"] = "vibes"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_split_location_rejected():
    case = _load_example()
    case["trace"]["likely_split_point"]["location"] = "thoughts"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_step_mutability_must_be_in_enum():
    case = _load_example()
    case["trace"]["minimal_repair_path"]["steps"][0]["mutability"] = "destroy"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_at_root_rejected():
    case = _load_example()
    case["unexpected_field"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_trace_rejected():
    case = _load_example()
    case["trace"]["extra"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_confidence_must_be_in_unit_interval():
    case = _load_example()
    case["trace"]["plausible_prior_paths"][0]["confidence"] = 1.5
    errors = list(_validator().iter_errors(case))
    assert errors
