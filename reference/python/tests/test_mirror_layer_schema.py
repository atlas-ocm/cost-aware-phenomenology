"""Tests for the Mirror Layer schema.

Covers the worked example plus the doc-level invariants ML-01..ML-12 from
02_subsystems/mirror_layer.md. Each invariant is exercised as a negative
test that confirms the schema rejects the violation.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "mirror_layer.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "mirror_frame_example.json"


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


# -- ML-01: no mutation --


def test_ml_01_observation_mutability_must_be_read_only():
    case = _load_example()
    case["frame"]["observations"][0]["mutability"] = "write"
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-01: observation.mutability must be const read_only"


def test_ml_01_policy_allow_mutation_locked_to_false():
    case = _load_example()
    case["policy"]["allow_mutation"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-01: policy.allow_mutation must be const false"


# -- ML-03: declared != observed; policy invariant --


def test_ml_03_policy_allow_declared_as_observed_locked_to_false():
    case = _load_example()
    case["policy"]["allow_declared_as_observed"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-03: policy.allow_declared_as_observed must be const false"


def test_ml_03_declared_state_is_separate_slot():
    case = _load_example()
    # Removing declared_state is allowed (optional); the schema must still
    # require observed_state and observations to be present.
    case["frame"].pop("declared_state", None)
    errors = list(_validator().iter_errors(case))
    assert not errors, "declared_state is optional; observed_state remains required"


# -- ML-04: unknown must remain unknown; verdict=aligned forbidden when unknowns present --


def test_ml_04_aligned_forbidden_when_unknowns_present():
    case = _load_example()
    case["frame"]["unknowns"] = [
        {"path": "hidden_block", "reason": "below viewport"}
    ]
    case["verdict"]["verdict"] = "aligned"
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-04: verdict=aligned must be forbidden when unknowns are present"


def test_ml_04_unknowns_array_required_on_frame():
    case = _load_example()
    del case["frame"]["unknowns"]
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-04: frame.unknowns is a required array"


# -- ML-05: stale evidence cannot confirm; verdict=aligned forbidden when stale obs present --


def test_ml_05_aligned_forbidden_when_stale_observation_present():
    case = _load_example()
    case["frame"]["observations"][0]["freshness"] = "stale"
    case["verdict"]["verdict"] = "aligned"
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-05: verdict=aligned must be forbidden when any observation has freshness=stale"


def test_verdict_stale_requires_a_stale_observation():
    case = _load_example()
    for obs in case["frame"]["observations"]:
        obs["freshness"] = "fresh"
    case["verdict"]["verdict"] = "stale"
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=stale requires at least one observation with freshness=stale"


# -- ML-06: boundary-hidden state cannot be aligned --


def test_ml_06_boundary_signals_forbids_aligned_verdict():
    case = _load_example()
    case["frame"]["boundary_signals"] = [
        {"boundary": "viewport", "reason": "below fold not loaded"}
    ]
    case["verdict"]["verdict"] = "aligned"
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-06: any boundary_signal must forbid verdict=aligned"


def test_verdict_boundary_hidden_requires_a_boundary_signal():
    case = _load_example()
    case["frame"]["boundary_signals"] = []
    case["verdict"]["verdict"] = "boundary_hidden"
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict=boundary_hidden requires at least one boundary_signal"


# -- ML-07: provenance required --


def test_ml_07_policy_require_source_locked_to_true():
    case = _load_example()
    case["policy"]["require_source_for_every_observation"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-07: policy.require_source_for_every_observation must be const true"


def test_ml_07_observation_source_required():
    case = _load_example()
    del case["frame"]["observations"][0]["source"]
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-07: every observation must declare a source"


# -- ML-08: raw vs derived separated --


def test_ml_08_derived_fact_must_reference_an_observation():
    case = _load_example()
    case["frame"]["observed_state"]["derived_facts"].append(
        {
            "id": "bad_derived",
            "claim": "Hangs without provenance",
            "derived_from": []
        }
    )
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-08: derived_fact.derived_from must have minItems:1"


def test_ml_08_observed_state_requires_both_facts_and_derived_facts():
    case = _load_example()
    del case["frame"]["observed_state"]["derived_facts"]
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-08: observed_state.derived_facts is required (may be empty array)"


# -- ML-09 / ML-10: verdict enum only has observational states --


def test_ml_09_verdict_cannot_be_release_gate_word():
    case = _load_example()
    case["verdict"]["verdict"] = "pass"
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-09/ML-10: Mirror verdict enum must not include Release Gate words like pass"


def test_ml_10_verdict_cannot_be_blocked():
    case = _load_example()
    case["verdict"]["verdict"] = "blocked"
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-10: Mirror verdict enum must not include Release Gate words like blocked"


def test_recommended_next_action_has_no_release_word():
    case = _load_example()
    case["verdict"]["recommended_next_action"] = "release"
    errors = list(_validator().iter_errors(case))
    assert errors, "Mirror recommended_next_action must not include release"


# -- ML-12: log contradictions, never silently resolve --


def test_ml_12_contradictions_array_required():
    case = _load_example()
    del case["frame"]["contradictions"]
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-12: frame.contradictions is a required array"


def test_ml_12_verdict_contradicted_requires_contradictions_non_empty():
    case = _load_example()
    case["frame"]["contradictions"] = []
    case["verdict"]["verdict"] = "contradicted"
    errors = list(_validator().iter_errors(case))
    assert errors, "ML-12: verdict=contradicted requires contradictions minItems:1"


# -- Enum and structure guards --


def test_unknown_source_rejected():
    case = _load_example()
    case["frame"]["observations"][0]["source"] = "model_imagination"
    errors = list(_validator().iter_errors(case))
    assert errors, "Mirror source enum must be closed"


def test_unknown_verdict_rejected():
    case = _load_example()
    case["verdict"]["verdict"] = "ok"
    errors = list(_validator().iter_errors(case))
    assert errors, "verdict enum must be from the closed list"


def test_unknown_subject_kind_rejected():
    case = _load_example()
    case["frame"]["subject"]["kind"] = "imaginary"
    errors = list(_validator().iter_errors(case))
    assert errors, "subject.kind enum must be closed"


def test_unknown_boundary_rejected():
    case = _load_example()
    case["frame"]["boundary_signals"] = [
        {"boundary": "model_internal_doubt", "reason": "no"}
    ]
    errors = list(_validator().iter_errors(case))
    assert errors, "boundary enum must be closed"


def test_additional_property_at_root_rejected():
    case = _load_example()
    case["unexpected_field"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_frame_rejected():
    case = _load_example()
    case["frame"]["extra"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_observation_rejected():
    case = _load_example()
    case["frame"]["observations"][0]["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_confidence_must_be_in_unit_interval():
    case = _load_example()
    case["frame"]["observations"][0]["confidence"] = 1.5
    errors = list(_validator().iter_errors(case))
    assert errors


def test_aligned_verdict_passes_when_everything_clean():
    case = _load_example()
    case["frame"]["unknowns"] = []
    case["frame"]["contradictions"] = []
    case["frame"]["boundary_signals"] = []
    for obs in case["frame"]["observations"]:
        obs["freshness"] = "fresh"
    for obs in case["frame"]["observed_state"]["facts"]:
        obs["freshness"] = "fresh"
    case["frame"]["diffs"] = []
    case["verdict"]["verdict"] = "aligned"
    case["verdict"]["recommended_next_action"] = "proceed_to_adjustment"
    case["verdict"]["reasons"] = ["all evidence fresh; no contradictions; no boundary signals"]
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_boundary_hidden_verdict_passes_with_boundary_signal():
    case = _load_example()
    case["frame"]["boundary_signals"] = [
        {"boundary": "viewport", "reason": "below fold not loaded"}
    ]
    case["verdict"]["verdict"] = "boundary_hidden"
    case["verdict"]["recommended_next_action"] = "probe_boundary"
    case["verdict"]["reasons"] = ["below fold not loaded; cannot observe further"]
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]
