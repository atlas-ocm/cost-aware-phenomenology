"""Tests for the Memory Dreaming schema.

Covers the golden example and the doc-level invariants that the v0.3 schema
is supposed to enforce:

- candidate_store / rejected_items cannot carry status=approved or status=raw
- memory_diff requires provenance (minItems: 1)
- target_id is required for keep / reconcile / deprecate / supersede / retcon / quarantine
- proposed_id is required for supersede / retcon
- dream_policy is locked to allow_direct_canonical_write=false,
  require_provenance=true, require_approval=true
- approval.approved_diff_indexes must be empty when status is
  not_reviewed / rejected / rolled_back, and non-empty when status is
  approved / partially_approved
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = ROOT / "spec" / "memory_dreaming" / "run.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "memory_dreaming" / "run_example.json"


def _load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_example():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def _validator():
    return jsonschema.Draft202012Validator(_load_schema())


def test_schema_is_valid_draft_2020_12():
    jsonschema.Draft202012Validator.check_schema(_load_schema())


def test_golden_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_example()), key=lambda e: e.path)
    assert not errors, [e.message for e in errors]


def test_dream_output_rejects_approved_status_in_candidate_store():
    run = _load_example()
    run["output"]["candidate_store"][0]["status"] = "approved"
    errors = list(_validator().iter_errors(run))
    assert errors, "Dream output must not contain candidate nodes with status=approved"


def test_dream_output_rejects_raw_status_in_candidate_store():
    run = _load_example()
    run["output"]["candidate_store"][0]["status"] = "raw"
    errors = list(_validator().iter_errors(run))
    assert errors, "Dream output must not contain candidate nodes with status=raw"


def test_dream_output_rejects_approved_status_in_rejected_items():
    run = _load_example()
    run["output"]["rejected_items"][0]["status"] = "approved"
    errors = list(_validator().iter_errors(run))
    assert errors, "Rejected items must not carry status=approved"


def test_memory_diff_requires_provenance():
    run = _load_example()
    run["output"]["memory_diff"][0]["provenance"] = []
    errors = list(_validator().iter_errors(run))
    assert errors, "memory_diff.provenance must have minItems:1"


def test_memory_diff_provenance_field_is_required():
    run = _load_example()
    del run["output"]["memory_diff"][0]["provenance"]
    errors = list(_validator().iter_errors(run))
    assert errors, "memory_diff must require provenance field"


@pytest.mark.parametrize(
    "op_index",
    [0, 1, 2, 3, 4, 5],
    ids=["keep", "reconcile", "deprecate", "supersede", "retcon", "quarantine"],
)
def test_target_id_required_for_non_rollback_ops(op_index):
    run = _load_example()
    diff = run["output"]["memory_diff"][op_index]
    if "target_id" not in diff:
        pytest.skip(f"example diff[{op_index}] has no target_id to remove")
    del diff["target_id"]
    errors = list(_validator().iter_errors(run))
    assert errors, f"op={diff.get('op')} must require target_id"


@pytest.mark.parametrize("op_index", [3, 4], ids=["supersede", "retcon"])
def test_proposed_id_required_for_supersede_and_retcon(op_index):
    run = _load_example()
    diff = run["output"]["memory_diff"][op_index]
    assert "proposed_id" in diff
    del diff["proposed_id"]
    errors = list(_validator().iter_errors(run))
    assert errors, f"op={diff.get('op')} must require proposed_id"


def test_policy_cannot_allow_direct_canonical_write():
    run = _load_example()
    run["input"]["policy"]["allow_direct_canonical_write"] = True
    errors = list(_validator().iter_errors(run))
    assert errors, "policy.allow_direct_canonical_write must be locked to false"


def test_policy_cannot_disable_provenance_requirement():
    run = _load_example()
    run["input"]["policy"]["require_provenance"] = False
    errors = list(_validator().iter_errors(run))
    assert errors, "policy.require_provenance must be locked to true"


def test_policy_cannot_disable_approval_requirement():
    run = _load_example()
    run["input"]["policy"]["require_approval"] = False
    errors = list(_validator().iter_errors(run))
    assert errors, "policy.require_approval must be locked to true"


@pytest.mark.parametrize("status", ["not_reviewed", "rejected", "rolled_back"])
def test_non_approval_status_rejects_approved_indexes(status):
    run = _load_example()
    run["approval"]["status"] = status
    run["approval"]["approved_diff_indexes"] = [0]
    errors = list(_validator().iter_errors(run))
    assert errors, (
        f"approval.status={status} must require empty approved_diff_indexes"
    )


@pytest.mark.parametrize("status", ["approved", "partially_approved"])
def test_approval_status_requires_at_least_one_approved_index(status):
    run = _load_example()
    run["approval"]["status"] = status
    run["approval"]["approved_diff_indexes"] = []
    errors = list(_validator().iter_errors(run))
    assert errors, (
        f"approval.status={status} must require at least one approved index"
    )


def test_extra_top_level_field_rejected():
    run = _load_example()
    run["unexpected_field"] = "x"
    errors = list(_validator().iter_errors(run))
    assert errors, "additionalProperties:false should reject unknown top-level fields"


def test_memory_node_requires_non_empty_provenance():
    run = _load_example()
    run["output"]["candidate_store"][0]["provenance"] = []
    errors = list(_validator().iter_errors(run))
    assert errors, "memory_node.provenance must have minItems:1"


@pytest.mark.parametrize(
    "field",
    ["contradicts", "supersedes", "valid_from", "valid_until"],
)
def test_memory_node_requires_pdf_spec_audit_fields(field):
    run = _load_example()
    del run["output"]["candidate_store"][0][field]
    errors = list(_validator().iter_errors(run))
    assert errors, f"memory_node must require {field}"


def test_dream_input_requires_artifact_refs():
    run = _load_example()
    del run["input"]["artifact_refs"]
    errors = list(_validator().iter_errors(run))
    assert errors, "DreamRunInput must include artifact_refs"


def test_dream_input_uses_superseded_ledger_refs():
    run = _load_example()
    run["input"]["deprecated_ledger_refs"] = run["input"].pop(
        "superseded_ledger_refs"
    )
    errors = list(_validator().iter_errors(run))
    assert errors, "DreamRunInput must use superseded_ledger_refs"
