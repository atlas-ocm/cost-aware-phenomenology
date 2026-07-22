"""Tests for the AICE 6xx incident taxonomy (draft v0.6).

Covers the incident schema, the golden examples, the schema invariants that
the taxonomy relies on (closed code set, mandatory STATE_UNCHANGED), version,
code-range, and schema-$id parity, and the deterministic integrity check
(registry <-> codes <-> examples <-> links). Includes AICE-610, AICE-611,
AICE-612, AICE-613, and AICE-614 coverage (with focused AICE-612
cross-actor-inference, AICE-613 self-hosting-mutation-deadlock, and AICE-614
infrastructure-vs-semantic-verdict invariants) plus adversarial scratch-copy
tests that prove the validator detects registry, doc, link, code-range, version,
and schema-$id tampering.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = ROOT / "spec" / "aice" / "incident.schema.json"
EXAMPLES_DIR = ROOT / "examples" / "aice"
CHECK_AICE = ROOT / "reference" / "python" / "scripts" / "aice" / "check_aice.py"
EXAMPLE_610 = EXAMPLES_DIR / "aice-610-control-without-enforcement.json"
EXAMPLE_611 = EXAMPLES_DIR / "aice-611-operational-reachability-substitution.json"
EXAMPLE_612 = EXAMPLES_DIR / "aice-612-actor-path-substitution.json"
EXAMPLE_613 = EXAMPLES_DIR / "aice-613-self-hosting-mutation-shape-deadlock.json"
EXAMPLE_614 = EXAMPLES_DIR / "aice-614-infrastructure-failure-as-semantic-verdict.json"

# Import check_aice so its closed-code-set constant can be asserted directly.
sys.path.insert(0, str(CHECK_AICE.parent))
import check_aice  # noqa: E402

EXAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.json"))


def _load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validator():
    return jsonschema.Draft202012Validator(_load_schema())


def test_schema_is_valid_draft_2020_12():
    jsonschema.Draft202012Validator.check_schema(_load_schema())


def test_examples_exist():
    assert EXAMPLE_FILES, f"no AICE example payloads found in {EXAMPLES_DIR}"


@pytest.mark.parametrize("example_path", EXAMPLE_FILES, ids=lambda p: p.name)
def test_example_is_valid(example_path):
    example = json.loads(example_path.read_text(encoding="utf-8"))
    errors = sorted(_validator().iter_errors(example), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_schema_rejects_unknown_code():
    example = json.loads(EXAMPLE_FILES[0].read_text(encoding="utf-8"))
    example["code"] = "AICE-699"
    errors = list(_validator().iter_errors(example))
    assert errors, "Schema must reject codes outside AICE-604..AICE-614"


def test_schema_requires_state_unchanged_in_workflow_effect():
    example = json.loads(EXAMPLE_FILES[0].read_text(encoding="utf-8"))
    example["workflow_effect"] = ["BLOCK_ACCEPTANCE"]
    errors = list(_validator().iter_errors(example))
    assert errors, "workflow_effect must contain STATE_UNCHANGED"


def _load_604():
    path = EXAMPLES_DIR / "aice-604-metaphysical-artifact.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_digest_value_with_unverified_flag_is_rejected():
    incident = _load_604()
    incident["artifact"]["digest"]["value"] = "a" * 64
    incident["artifact"]["digest"]["verified_against_bytes"] = False
    errors = list(_validator().iter_errors(incident))
    assert errors, "digest.value must require verified_against_bytes: true"


def test_digest_value_without_verified_flag_is_rejected():
    incident = _load_604()
    incident["artifact"]["digest"]["value"] = "a" * 64
    incident["artifact"]["digest"].pop("verified_against_bytes", None)
    errors = list(_validator().iter_errors(incident))
    assert errors, "digest.value present must require the verified_against_bytes field"


def test_digest_value_with_verified_flag_is_accepted():
    incident = _load_604()
    incident["artifact"]["digest"]["value"] = "a" * 64
    incident["artifact"]["digest"]["verified_against_bytes"] = True
    errors = list(_validator().iter_errors(incident))
    assert not errors, [e.message for e in errors]


def test_declared_digest_without_value_remains_valid():
    incident = _load_604()
    incident["artifact"]["digest"].pop("value", None)
    incident["artifact"]["digest"]["verified_against_bytes"] = False
    errors = list(_validator().iter_errors(incident))
    assert not errors, [e.message for e in errors]


# --- AICE-610: Control Exists, Enforcement Not Found ---------------------------

AICE_610_TITLE = "Control Exists, Enforcement Not Found"


def _load_610():
    return json.loads(EXAMPLE_610.read_text(encoding="utf-8"))


def test_aice_610_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_610()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_expected_codes_are_closed_at_604_614():
    assert check_aice.EXPECTED_CODES == [f"AICE-{n}" for n in range(604, 615)]
    assert "AICE-613" in check_aice.EXPECTED_CODES
    assert "AICE-614" in check_aice.EXPECTED_CODES
    assert "AICE-615" not in check_aice.EXPECTED_CODES
    assert len(check_aice.EXPECTED_CODES) == 11


def test_schema_accepts_610_through_614_but_rejects_615():
    assert not list(_validator().iter_errors(_load_610())), "AICE-610 example must validate"
    assert not list(_validator().iter_errors(_load_611())), "AICE-611 example must validate"
    assert not list(_validator().iter_errors(_load_612())), "AICE-612 example must validate"
    assert not list(_validator().iter_errors(_load_613())), "AICE-613 example must validate"
    assert not list(_validator().iter_errors(_load_614())), "AICE-614 example must validate"
    incident = _load_614()
    incident["code"] = "AICE-615"
    assert list(_validator().iter_errors(incident)), "AICE-615 must be rejected (closed set)"


def test_registry_and_doc_metadata_agree_for_610():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-610")
    assert entry["title"] == AICE_610_TITLE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-610.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-610 — {AICE_610_TITLE}")
    assert _load_610()["title"] == entry["title"]


def test_610_example_requires_state_unchanged():
    incident = _load_610()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_existing_examples_remain_valid_under_v0_6():
    for name in (
        "aice-604-metaphysical-artifact.json",
        "aice-605-release-without-implementation.json",
        "aice-610-control-without-enforcement.json",
        "aice-611-operational-reachability-substitution.json",
        "aice-612-actor-path-substitution.json",
        "aice-613-self-hosting-mutation-shape-deadlock.json",
        "aice-614-infrastructure-failure-as-semantic-verdict.json",
    ):
        incident = json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))
        errors = list(_validator().iter_errors(incident))
        assert not errors, [name, [e.message for e in errors]]


# --- AICE-611: Operational Reachability Substitution ---------------------------

AICE_611_TITLE = "Operational Reachability Substitution"


def _load_611():
    return json.loads(EXAMPLE_611.read_text(encoding="utf-8"))


def test_aice_611_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_611()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_registry_and_doc_metadata_agree_for_611():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-611")
    assert entry["title"] == AICE_611_TITLE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-611.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-611 — {AICE_611_TITLE}")
    assert _load_611()["title"] == entry["title"]


def test_611_example_requires_state_unchanged():
    incident = _load_611()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_611_example_blocks_acceptance_while_postcondition_unobserved():
    # The defining AICE-611 fact: components pass but the required end-to-end
    # postcondition is unobserved, so the envelope must BLOCK_ACCEPTANCE and
    # must not represent operational advancement.
    incident = _load_611()
    assert "BLOCK_ACCEPTANCE" in incident["workflow_effect"]
    cd = incident["code_details"]
    assert cd["required_postcondition"]["observed"] is False
    assert cd["required_postcondition"]["independently_read_back"] is False
    assert cd["required_path"]["reachability_established"] is False
    assert cd["required_path"]["executed_from_real_entrypoint"] is False


def test_611_example_is_representative_not_historical():
    incident = _load_611()
    assert "REPRESENTATIVE_EXAMPLE" in incident["notes"]
    assert "NOT_A_VERIFIED_HISTORICAL_INCIDENT" in incident["notes"]


# --- AICE-612: Actor Path Substitution -----------------------------------------

AICE_612_TITLE = "Actor Path Substitution"


def _load_612():
    return json.loads(EXAMPLE_612.read_text(encoding="utf-8"))


def _aice_612_invariants_ok(incident) -> bool:
    """Focused canonical-example invariants for AICE-612 (cross-actor inference).

    Not imposed on arbitrary envelopes — only used to guard the canonical
    repository example and to prove that specific mutations invalidate it.
    """
    if incident.get("code") != "AICE-612":
        return True
    cd = incident.get("code_details", {})
    tested = cd.get("tested_path", {})
    claimed = cd.get("claimed_path", {})
    rel = cd.get("relationship", {})
    audit = cd.get("audit_result", {})
    return all(
        [
            bool(tested.get("actor")) and bool(claimed.get("actor")),
            tested.get("actor") != claimed.get("actor"),
            rel.get("authority_boundaries_distinct") is True,
            tested.get("tested") is True,
            claimed.get("tested") is False,
            rel.get("path_equivalence_established") is False,
            rel.get("cross_actor_inference_applied") is True,
            "STATE_UNCHANGED" in incident.get("workflow_effect", []),
            audit.get("claimed_actor_path_status") == "NOT_ESTABLISHED",
            audit.get("conclusion_valid") is False,
        ]
    )


def test_aice_612_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_612()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_registry_and_doc_metadata_agree_for_612():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-612")
    assert entry["title"] == AICE_612_TITLE
    # AICE-612 default effect is STATE_UNCHANGED alone (per the normative code doc).
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED"]
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-612.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-612 — {AICE_612_TITLE}")
    assert _load_612()["title"] == entry["title"]


def test_612_example_requires_state_unchanged():
    incident = _load_612()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_612_example_keeps_claimed_actor_path_not_established():
    cd = _load_612()["code_details"]
    assert cd["audit_result"]["claimed_actor_path_status"] == "NOT_ESTABLISHED"
    assert cd["claimed_path"]["tested"] is False
    assert cd["claimed_path"]["result"] == "not_established"


def test_612_example_is_representative_not_historical():
    incident = _load_612()
    assert "REPRESENTATIVE_EXAMPLE" in incident["notes"]
    assert "NOT_A_VERIFIED_HISTORICAL_INCIDENT" in incident["notes"]


def test_612_canonical_example_satisfies_invariants():
    assert _aice_612_invariants_ok(_load_612())


def test_612_proposer_denial_is_not_operator_missing_proof():
    # A proposer denial transferred into "operator path missing as observed fact"
    # must break the AICE-612 invariants (it is exactly the forbidden inference).
    incident = _load_612()
    incident["code_details"]["claimed_path"]["tested"] = True
    incident["code_details"]["claimed_path"]["result"] = "missing"
    incident["code_details"]["audit_result"]["claimed_actor_path_status"] = "MISSING_OBSERVED"
    assert not _aice_612_invariants_ok(incident)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda cd: cd["tested_path"].__setitem__("actor", cd["claimed_path"]["actor"]),
        lambda cd: cd["claimed_path"].__setitem__("tested", True),
        lambda cd: cd["relationship"].__setitem__("path_equivalence_established", True),
        lambda cd: cd["relationship"].__setitem__("cross_actor_inference_applied", False),
    ],
    ids=["actors_identical", "claimed_tested", "equivalence_established", "inference_removed"],
)
def test_612_mutations_invalidate_substitution_predicate(mutate):
    incident = _load_612()
    mutate(incident["code_details"])
    assert not _aice_612_invariants_ok(incident)


def test_612_advancing_workflow_state_invalidates_example():
    incident = _load_612()
    incident["workflow_effect"] = ["BLOCK_ACCEPTANCE"]  # drops STATE_UNCHANGED
    # schema rejects it (no STATE_UNCHANGED) AND the focused invariant fails.
    assert list(_validator().iter_errors(incident))
    assert not _aice_612_invariants_ok(incident)


def test_612_correctly_scoped_proposer_only_conclusion_is_not_an_incident():
    # If the auditor scopes the conclusion to the proposer only (no cross-actor
    # inference), the AICE-612 predicate is not satisfied.
    incident = _load_612()
    incident["code_details"]["relationship"]["cross_actor_inference_applied"] = False
    assert not _aice_612_invariants_ok(incident)


# --- AICE-613: Self-Hosting Mutation-Shape Deadlock ----------------------------

AICE_613_TITLE = "Self-Hosting Mutation-Shape Deadlock"


def _load_613():
    return json.loads(EXAMPLE_613.read_text(encoding="utf-8"))


def _aice_613_invariants_ok(incident) -> bool:
    """Focused canonical-example invariants for AICE-613 (self-hosting deadlock).

    Not imposed on arbitrary envelopes — only used to guard the canonical
    repository example and to prove that specific mutations invalidate it. The
    predicate requires BOTH the immediate full-object capacity defect AND the
    recursive self-hosting bootstrap dependency; generic output truncation alone
    (no recursive upgrade dependency) must not satisfy it.
    """
    if incident.get("code") != "AICE-613":
        return True
    cd = incident.get("code_details", {})
    req = cd.get("requested_change", {})
    tgt = cd.get("target", {})
    proto = cd.get("mutation_protocol", {})
    cap = cd.get("capacity", {})
    boot = cd.get("bootstrap", {})
    res = cd.get("result", {})
    effect = incident.get("workflow_effect", [])
    return all(
        [
            req.get("delta_bounded") is True,
            req.get("delta_materially_smaller_than_target") is True,
            tgt.get("existing") is True,
            proto.get("authorized_form") == "full_object_replacement",
            proto.get("payload_cost_scales_with_target_size") is True,
            proto.get("delta_capable_path_reachable") is False,
            cap.get("observed") is True,
            cap.get("full_object_payload_exceeds_capacity") is True,
            boot.get("patch_support_required") is True,
            boot.get("patch_support_upgrade_requires_same_full_object_form") is True,
            boot.get("separately_authorized_bootstrap_available") is False,
            res.get("mutation_materialized") is False,
            res.get("target_state_changed") is False,
            res.get("self_hosting_path_reachable") is False,
            "STATE_UNCHANGED" in effect,
            "BLOCK_ACCEPTANCE" in effect,
        ]
    )


def test_aice_613_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_613()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_registry_and_doc_metadata_agree_for_613():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-613")
    assert entry["title"] == AICE_613_TITLE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    assert entry["default_retryability"] == "requires_new_evidence"
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-613.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-613 — {AICE_613_TITLE}")
    assert _load_613()["title"] == entry["title"]


def test_613_example_requires_state_unchanged():
    incident = _load_613()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_613_example_blocks_acceptance():
    incident = _load_613()
    assert "BLOCK_ACCEPTANCE" in incident["workflow_effect"]
    # Dropping BLOCK_ACCEPTANCE must break the focused invariant (default effect).
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "BLOCK_ACCEPTANCE"]
    assert not _aice_613_invariants_ok(incident)


def test_613_example_is_representative_not_historical():
    incident = _load_613()
    assert "REPRESENTATIVE_EXAMPLE" in incident["notes"]
    assert "NOT_A_VERIFIED_HISTORICAL_INCIDENT" in incident["notes"]


def test_613_canonical_example_satisfies_invariants():
    assert _aice_613_invariants_ok(_load_613())


def test_613_target_present_is_required():
    # The failure is not artifact absence (that is AICE-604). If the target is
    # marked absent, the AICE-613 predicate must no longer hold.
    incident = _load_613()
    incident["code_details"]["target"]["existing"] = False
    assert not _aice_613_invariants_ok(incident)


def test_613_delta_must_be_bounded_and_smaller_than_target():
    incident = _load_613()
    incident["code_details"]["requested_change"]["delta_materially_smaller_than_target"] = False
    assert not _aice_613_invariants_ok(incident)


def test_613_full_object_must_be_only_authorized_form():
    incident = _load_613()
    incident["code_details"]["mutation_protocol"]["authorized_form"] = "unified_diff"
    assert not _aice_613_invariants_ok(incident)


def test_613_generic_output_truncation_alone_is_not_613():
    # Remove the recursive self-hosting dependency: a large-file/truncation
    # capacity failure without the bootstrap deadlock must NOT satisfy AICE-613.
    incident = _load_613()
    incident["code_details"]["bootstrap"]["patch_support_upgrade_requires_same_full_object_form"] = False
    assert not _aice_613_invariants_ok(incident)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda cd: cd["mutation_protocol"].__setitem__("delta_capable_path_reachable", True),
        lambda cd: cd["capacity"].__setitem__("full_object_payload_exceeds_capacity", False),
        lambda cd: cd["bootstrap"].__setitem__("separately_authorized_bootstrap_available", True),
        lambda cd: cd["bootstrap"].__setitem__("patch_support_upgrade_requires_same_full_object_form", False),
        lambda cd: cd["result"].__setitem__("mutation_materialized", True),
        lambda cd: cd["result"].__setitem__("target_state_changed", True),
        lambda cd: cd["capacity"].__setitem__("observed", False),
    ],
    ids=[
        "delta_path_reachable",
        "full_object_fits_capacity",
        "separate_bootstrap_available",
        "recursive_dependency_removed",
        "mutation_materialized",
        "target_state_changed",
        "capacity_observation_removed",
    ],
)
def test_613_mutations_invalidate_deadlock_predicate(mutate):
    incident = _load_613()
    mutate(incident["code_details"])
    assert not _aice_613_invariants_ok(incident)


# --- AICE-614: Infrastructure Failure as Semantic Verdict ----------------------

AICE_614_TITLE = "Infrastructure Failure as Semantic Verdict"

_SEMANTIC_VERDICTS = {"VERIFIER_PASS", "VERIFIER_NEEDS_FIX", "VERIFIER_BLOCKED_SEMANTIC"}


def _load_614():
    return json.loads(EXAMPLE_614.read_text(encoding="utf-8"))


def _aice_614_invariants_ok(incident) -> bool:
    """Focused canonical-example invariants for AICE-614.

    Not imposed on arbitrary envelopes. The predicate requires an infrastructure
    failure that was fabricated into an attributed semantic verdict reaching an
    authoritative surface, with no completed semantic review. A correctly
    preserved infrastructure result (semantic verdict absent), a real completed
    semantic review, or a correct NOT_ESTABLISHED status must all break it.
    """
    if incident.get("code") != "AICE-614":
        return True
    cd = incident.get("code_details", {})
    claim = cd.get("claim", {})
    ex = cd.get("execution", {})
    infra = cd.get("infrastructure_result", {})
    inv = cd.get("invalid_normalization", {})
    down = cd.get("downstream_effect", {})
    correct = cd.get("correct_state", {})
    effect = incident.get("workflow_effect", [])
    authoritative_effect = bool(
        down.get("repair_loop_triggered") or down.get("semantic_evidence_recorded")
    )
    return all(
        [
            claim.get("verifier_review_required") is True,
            # no completed semantic review occurred
            ex.get("semantic_review_completed") is False,
            ex.get("transport_completed") is False,
            # a concrete infrastructure failure exists
            infra.get("present") is True,
            bool(infra.get("failure_class")),
            # a semantic verdict was fabricated and attributed to the verifier
            inv.get("semantic_verdict_recorded") is True,
            inv.get("recorded_verdict") in _SEMANTIC_VERDICTS,
            inv.get("attributed_to_verifier") is True,
            inv.get("mapping_valid") is False,
            # the false verdict reached an authoritative surface
            authoritative_effect,
            # the correct state is absent / NOT_ESTABLISHED, not an inferred PASS
            correct.get("semantic_verdict") == "absent",
            correct.get("semantic_review_status") == "NOT_ESTABLISHED",
            "STATE_UNCHANGED" in effect,
            "BLOCK_ACCEPTANCE" in effect,
        ]
    )


def test_aice_614_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_614()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_registry_and_doc_metadata_agree_for_614():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-614")
    assert entry["title"] == AICE_614_TITLE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    assert entry["default_retryability"] == "requires_new_evidence"
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-614.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-614 — {AICE_614_TITLE}")
    assert _load_614()["title"] == entry["title"]


def test_614_example_requires_state_unchanged():
    incident = _load_614()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_614_example_blocks_acceptance():
    incident = _load_614()
    assert "BLOCK_ACCEPTANCE" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "BLOCK_ACCEPTANCE"]
    assert not _aice_614_invariants_ok(incident)


def test_614_example_is_representative_not_historical():
    incident = _load_614()
    assert "REPRESENTATIVE_EXAMPLE" in incident["notes"]
    assert "NOT_A_VERIFIED_HISTORICAL_INCIDENT" in incident["notes"]


def test_614_canonical_example_satisfies_invariants():
    assert _aice_614_invariants_ok(_load_614())


def test_614_transport_incomplete_is_the_forbidding_condition():
    # The canonical example encodes transport_completed=false while a semantic
    # verdict was recorded — exactly the forbidden mapping.
    cd = _load_614()["code_details"]
    assert cd["execution"]["transport_completed"] is False
    assert cd["invalid_normalization"]["semantic_verdict_recorded"] is True
    assert cd["invalid_normalization"]["recorded_verdict"] in _SEMANTIC_VERDICTS


def test_614_completed_semantic_review_is_not_614():
    # A real completed semantic review (NEEDS_FIX/BLOCKED_SEMANTIC delivered through
    # a valid claim + attributed parsed response) is NOT AICE-614.
    incident = _load_614()
    cd = incident["code_details"]
    cd["claim"]["canonical_claim_present"] = True
    cd["execution"].update(
        transport_completed=True,
        response_received=True,
        response_attributed=True,
        output_parsed=True,
        semantic_review_completed=True,
    )
    cd["invalid_normalization"]["mapping_valid"] = True
    assert not _aice_614_invariants_ok(incident)


def test_614_preserved_infrastructure_result_is_not_614():
    # If the infrastructure failure is preserved (no fabricated semantic verdict),
    # the AICE-614 predicate must not hold — this is the correct fail-closed shape.
    incident = _load_614()
    incident["code_details"]["invalid_normalization"]["semantic_verdict_recorded"] = False
    assert not _aice_614_invariants_ok(incident)


def test_614_correct_replacement_is_not_established_not_pass():
    # The correct replacement for a fabricated veto is NOT_ESTABLISHED, never PASS.
    incident = _load_614()
    incident["code_details"]["correct_state"]["semantic_review_status"] = "PASS"
    incident["code_details"]["correct_state"]["semantic_verdict"] = "VERIFIER_PASS"
    assert not _aice_614_invariants_ok(incident)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda cd: cd["execution"].__setitem__("semantic_review_completed", True),
        lambda cd: cd["invalid_normalization"].__setitem__("mapping_valid", True),
        lambda cd: cd["invalid_normalization"].__setitem__("semantic_verdict_recorded", False),
        lambda cd: cd["invalid_normalization"].__setitem__("attributed_to_verifier", False),
        lambda cd: cd["infrastructure_result"].__setitem__("present", False),
        lambda cd: (
            cd["downstream_effect"].__setitem__("repair_loop_triggered", False),
            cd["downstream_effect"].__setitem__("semantic_evidence_recorded", False),
        ),
        lambda cd: cd["correct_state"].__setitem__("semantic_verdict", "VERIFIER_NEEDS_FIX"),
    ],
    ids=[
        "review_completed",
        "mapping_valid",
        "verdict_not_recorded",
        "not_attributed_to_verifier",
        "no_infrastructure_failure",
        "no_authoritative_downstream_effect",
        "semantic_verdict_not_absent",
    ],
)
def test_614_mutations_invalidate_predicate(mutate):
    incident = _load_614()
    mutate(incident["code_details"])
    assert not _aice_614_invariants_ok(incident)


# --- Version / range / $id parity ---------------------------------------------

def test_spec_version_is_consistently_0_6_0():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    schema = _load_schema()
    assert registry["spec_version"] == "0.6.0"
    assert schema["properties"]["spec_version"]["const"] == "0.6.0"
    assert check_aice.EXPECTED_VERSION == "0.6.0"
    for ex in EXAMPLE_FILES:
        data = json.loads(ex.read_text(encoding="utf-8"))
        assert data["spec_version"] == "0.6.0", ex.name


def test_schema_id_is_v0_6_and_unique():
    schema = _load_schema()
    assert schema["$id"] == "urn:cap:schema:aice-incident:v0.6"
    # unique across spec/: no other schema carries this aice-incident id
    spec_dir = ROOT / "spec"
    hits = []
    for p in spec_dir.rglob("*.json"):
        text = p.read_text(encoding="utf-8")
        if "urn:cap:schema:aice-incident:v0.6" in text:
            hits.append(p.name)
    assert hits == ["incident.schema.json"], hits


def test_registry_canonical_range_is_604_614():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    assert registry["canonical_code_range"] == ["AICE-604", "AICE-614"]


# --- Adversarial: validator must catch AICE-614 / range / version / $id tampering

def _build_scratch(tmp_path: Path) -> Path:
    """Mirror the minimal tree check_aice.py expects (its ROOT = parents[4])."""
    script_dir = tmp_path / "reference" / "python" / "scripts" / "aice"
    script_dir.mkdir(parents=True)
    shutil.copy(CHECK_AICE, script_dir / "check_aice.py")
    shutil.copytree(ROOT / "spec" / "aice", tmp_path / "spec" / "aice")
    shutil.copytree(EXAMPLES_DIR, tmp_path / "examples" / "aice")
    shutil.copy(ROOT / "AICE.md", tmp_path / "AICE.md")
    return script_dir / "check_aice.py"


def _run_check(script: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script)], capture_output=True, text=True)


def _registry_path(tmp: Path) -> Path:
    return tmp / "spec" / "aice" / "registry.json"


def _tamper_remove_614(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["codes"] = [c for c in data["codes"] if c.get("code") != "AICE-614"]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_rename_615(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    for c in data["codes"]:
        if c.get("code") == "AICE-614":
            c["code"] = "AICE-615"
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_delete_doc(tmp: Path) -> None:
    (tmp / "spec" / "aice" / "codes" / "AICE-614.md").unlink()


def _tamper_break_link(tmp: Path) -> None:
    doc = tmp / "spec" / "aice" / "codes" / "AICE-614.md"
    doc.write_text(
        doc.read_text(encoding="utf-8") + "\n[broken](./NONEXISTENT-614.md)\n",
        encoding="utf-8",
    )


def _tamper_stale_range(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["canonical_code_range"] = ["AICE-604", "AICE-613"]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_stale_version(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["spec_version"] = "0.5.0"
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_stale_schema_id(tmp: Path) -> None:
    schema = tmp / "spec" / "aice" / "incident.schema.json"
    data = json.loads(schema.read_text(encoding="utf-8"))
    data["$id"] = "urn:cap:schema:aice-incident:v0.5"
    schema.write_text(json.dumps(data), encoding="utf-8")


@pytest.mark.parametrize(
    "tamper",
    [
        _tamper_remove_614,
        _tamper_rename_615,
        _tamper_delete_doc,
        _tamper_break_link,
        _tamper_stale_range,
        _tamper_stale_version,
        _tamper_stale_schema_id,
    ],
    ids=[
        "remove_from_registry",
        "rename_to_615",
        "delete_doc",
        "break_link",
        "stale_code_range",
        "stale_spec_version",
        "stale_schema_id",
    ],
)
def test_check_aice_detects_tampering(tmp_path, tamper):
    script = _build_scratch(tmp_path)
    baseline = _run_check(script)
    assert baseline.returncode == 0, (
        "untampered scratch tree should pass:\n"
        f"{baseline.stdout}\n{baseline.stderr}"
    )
    tamper(tmp_path)
    result = _run_check(script)
    assert result.returncode != 0, (
        "check_aice.py failed to detect tampering:\n"
        f"{result.stdout}\n{result.stderr}"
    )


def test_check_aice_reports_no_issues():
    result = subprocess.run(
        [sys.executable, str(CHECK_AICE)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "check_aice.py reported integrity issues:\n"
        f"{result.stdout}\n{result.stderr}"
    )
