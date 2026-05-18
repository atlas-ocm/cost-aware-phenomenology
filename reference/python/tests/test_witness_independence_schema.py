"""Tests for the Witness Independence schema."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "witness_independence.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "witness_pair_example.json"


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


def test_wi_01_code_change_requires_independence_and_witnesses():
    case = _load_example()
    case["transition_class"] = "code_change"
    case["independence_required"] = False
    errors = list(_validator().iter_errors(case))
    assert errors, "WI-01: code_change requires independence_required=true"


def test_wi_01_code_change_requires_at_least_one_witness():
    case = _load_example()
    case["witnesses"] = []
    errors = list(_validator().iter_errors(case))
    assert errors, "WI-01: code_change requires at least one witness"


def test_wi_02_independent_true_requires_at_least_one_axis_differs():
    case = _load_example()
    case["witnesses"][0]["independence_axes"] = {
        "actor_identity": "same",
        "role": "same",
        "model": "same",
        "evidence_source": "same",
        "time_window": "same"
    }
    errors = list(_validator().iter_errors(case))
    assert errors, "WI-02: independent=true requires at least one axis=differs"


def test_wi_03_same_actor_forbids_independent_true():
    case = _load_example()
    case["witnesses"][0]["same_actor"] = True
    case["witnesses"][0]["independent"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "WI-03: same_actor=true forbids independent=true"


def test_wi_04_self_generated_evidence_forbids_independent_true():
    case = _load_example()
    case["witnesses"][0]["evidence_source"] = "self_generated"
    case["witnesses"][0]["independent"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "WI-04: self_generated evidence forbids independent=true"


def test_wi_05_verdict_must_be_from_closed_enum():
    case = _load_example()
    case["witnesses"][0]["verdict"] = "kind_of_pass"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_mirror_snapshot_does_not_require_independence():
    case = _load_example()
    case["transition_class"] = "mirror_snapshot"
    case["independence_required"] = False
    case["witnesses"] = []
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_internal_reasoning_does_not_require_witness():
    case = _load_example()
    case["transition_class"] = "internal_reasoning_step"
    case["independence_required"] = False
    case["witnesses"] = []
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_memory_canonicalization_requires_independence():
    case = _load_example()
    case["transition_class"] = "memory_canonicalization"
    case["independence_required"] = False
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_transition_class_rejected():
    case = _load_example()
    case["transition_class"] = "vibe_check"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_evidence_source_rejected():
    case = _load_example()
    case["witnesses"][0]["evidence_source"] = "feeling"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_role_rejected():
    case = _load_example()
    case["witnesses"][0]["witness"]["role"] = "supreme_overlord"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_independence_axes_must_be_same_or_differs():
    case = _load_example()
    case["witnesses"][0]["independence_axes"]["model"] = "maybe"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_in_witness_entry_rejected():
    case = _load_example()
    case["witnesses"][0]["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_blocked_verdict_is_valid_enum_member():
    case = _load_example()
    case["witnesses"][0]["verdict"] = "blocked"
    case["release_verdict"] = "blocked"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]
