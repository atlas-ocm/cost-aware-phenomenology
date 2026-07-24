"""Tests for the AICE 6xx incident taxonomy (draft v0.9).

Covers the incident schema, the golden examples, the schema invariants that
the taxonomy relies on (closed but SPARSE code set, mandatory STATE_UNCHANGED),
version, defined-set, and schema-$id parity, and the deterministic integrity
check (registry <-> codes <-> examples <-> links). Includes AICE-601, AICE-602,
AICE-603, AICE-610, AICE-611, AICE-612, AICE-613, AICE-614, AICE-615, AICE-616,
and AICE-618 coverage (with focused AICE-601 minimum-sufficient-mechanism-bypass,
AICE-602 gateway-authority-context, AICE-603 governance-induced-service-unavailability,
AICE-612 cross-actor-inference, AICE-613 self-hosting-mutation-deadlock,
AICE-614 infrastructure-vs-semantic-verdict, AICE-615 rollback-restore-identity,
AICE-616 review-input-identity, and AICE-618 verifier-eligibility-ceiling invariants)
plus adversarial scratch-copy tests that prove the validator detects registry, doc,
link, sparse-set, unassigned-code, false-contiguity, version, and schema-$id tampering.

The v0.9 defined set is closed but sparse: AICE-601..AICE-616 and AICE-618.
AICE-600 and AICE-617 are unassigned. AICE-615 and AICE-616 share the
non-normative EPISODE_EXACT_IDENTITY_BINDING family.
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
EXAMPLE_601 = EXAMPLES_DIR / "aice-601-minimum-sufficient-mechanism-bypass.json"
EXAMPLE_602 = EXAMPLES_DIR / "aice-602-gateway-authority-context-failure.json"
EXAMPLE_603 = EXAMPLES_DIR / "aice-603-governance-induced-service-unavailability.json"
EXAMPLE_610 = EXAMPLES_DIR / "aice-610-control-without-enforcement.json"
EXAMPLE_611 = EXAMPLES_DIR / "aice-611-operational-reachability-substitution.json"
EXAMPLE_612 = EXAMPLES_DIR / "aice-612-actor-path-substitution.json"
EXAMPLE_613 = EXAMPLES_DIR / "aice-613-self-hosting-mutation-shape-deadlock.json"
EXAMPLE_614 = EXAMPLES_DIR / "aice-614-infrastructure-failure-as-semantic-verdict.json"
EXAMPLE_615 = EXAMPLES_DIR / "aice-615-accepted-state-rollback-erasure.json"
EXAMPLE_616 = EXAMPLES_DIR / "aice-616-baseline-diff-conflation.json"
EXAMPLE_618 = EXAMPLES_DIR / "aice-618-verifier-gated-by-coder-evidence-ceiling.json"

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
    assert errors, "Schema must reject codes outside the defined sparse set"


@pytest.mark.parametrize("unassigned", ["AICE-600", "AICE-617"])
def test_schema_rejects_unassigned_codes(unassigned):
    example = json.loads(EXAMPLE_FILES[0].read_text(encoding="utf-8"))
    example["code"] = unassigned
    errors = list(_validator().iter_errors(example))
    assert errors, f"{unassigned} is unassigned and must be rejected by the closed set"


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


def test_expected_codes_are_the_sparse_defined_set():
    assert check_aice.EXPECTED_CODES == (
        [f"AICE-{n}" for n in range(601, 617)] + ["AICE-618"]
    )
    for newly_defined in ("AICE-601", "AICE-603", "AICE-615", "AICE-616", "AICE-618"):
        assert newly_defined in check_aice.EXPECTED_CODES
    # AICE-619 is beyond the defined set; must not be present.
    assert "AICE-619" not in check_aice.EXPECTED_CODES
    # The set is sparse, not contiguous: 600 and 617 are unassigned.
    for unassigned in ("AICE-600", "AICE-617"):
        assert unassigned not in check_aice.EXPECTED_CODES
        assert unassigned in check_aice.EXPECTED_UNASSIGNED
    assert len(check_aice.EXPECTED_CODES) == 17


def test_registry_declares_sparse_closed_set_and_unassigned():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    assert sorted(registry["canonical_defined_set"]) == sorted(check_aice.EXPECTED_CODES)
    assert sorted(registry["unassigned_codes"]) == ["AICE-600", "AICE-617"]
    codes = [c["code"] for c in registry["codes"]]
    assert sorted(codes) == sorted(check_aice.EXPECTED_CODES)
    assert len(codes) == 17
    # No contiguity-promising range field, and no entry for an unassigned code.
    assert "canonical_code_range" not in registry
    for unassigned in ("AICE-600", "AICE-617"):
        assert unassigned not in codes
        assert not (ROOT / "spec" / "aice" / "codes" / f"{unassigned}.md").exists()


def test_aice_617_is_genuinely_unassigned():
    # AICE-617 has NO title, machine name, definition, file, example, or registry
    # entry — it exists only in the machine-readable UNASSIGNED_CODES set.
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    assert "AICE-617" in registry["unassigned_codes"]
    assert "AICE-617" not in registry["canonical_defined_set"]
    assert "AICE-617" not in [c["code"] for c in registry["codes"]]
    assert "AICE-617" not in check_aice.EXPECTED_CODES
    assert not (ROOT / "spec" / "aice" / "codes" / "AICE-617.md").exists()
    assert not list(EXAMPLES_DIR.glob("aice-617*.json"))
    # Schema must reject AICE-617 as an incident code.
    incident = json.loads(EXAMPLE_FILES[0].read_text(encoding="utf-8"))
    incident["code"] = "AICE-617"
    assert list(_validator().iter_errors(incident)), "AICE-617 is unassigned and must be rejected"


def test_registry_machine_names_are_unique():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    names = [c.get("machine_name") for c in registry["codes"] if c.get("machine_name")]
    assert len(names) == len(set(names)), f"duplicate machine_name(s): {names}"


def test_schema_accepts_defined_set_but_rejects_unassigned_617():
    # Migrated from the v0.7 form (which rejected AICE-615): AICE-615/616/618 are
    # now DEFINED and must validate, while the still-unassigned AICE-617 must be
    # rejected. The original safety intent — the closed set rejects codes outside
    # it — is preserved, retargeted to the current sparse gap.
    for loader in (_load_601, _load_602, _load_603, _load_610, _load_611, _load_612,
                   _load_613, _load_614, _load_615, _load_616, _load_618):
        assert not list(_validator().iter_errors(loader())), f"{loader.__name__} must validate"
    incident = _load_614()
    incident["code"] = "AICE-617"
    assert list(_validator().iter_errors(incident)), "AICE-617 must be rejected (unassigned)"


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


def test_existing_examples_remain_valid_under_v0_8():
    for name in (
        "aice-601-minimum-sufficient-mechanism-bypass.json",
        "aice-602-gateway-authority-context-failure.json",
        "aice-603-governance-induced-service-unavailability.json",
        "aice-604-metaphysical-artifact.json",
        "aice-605-release-without-implementation.json",
        "aice-610-control-without-enforcement.json",
        "aice-611-operational-reachability-substitution.json",
        "aice-612-actor-path-substitution.json",
        "aice-613-self-hosting-mutation-shape-deadlock.json",
        "aice-614-infrastructure-failure-as-semantic-verdict.json",
        "aice-615-accepted-state-rollback-erasure.json",
        "aice-616-baseline-diff-conflation.json",
        "aice-618-verifier-gated-by-coder-evidence-ceiling.json",
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


# --- AICE-602: Gateway Authority Context Failure -------------------------------

AICE_602_TITLE = "Gateway Authority Context Failure"
AICE_602_MACHINE = "GATEWAY_AUTHORITY_CONTEXT_FAILURE"


def _load_602():
    return json.loads(EXAMPLE_602.read_text(encoding="utf-8"))


def _aice_602_invariants_ok(incident) -> bool:
    """Focused canonical-example invariants for AICE-602 (authorized-denial branch).

    Not imposed on arbitrary envelopes — only used to guard the canonical
    repository example and to prove that specific mutations invalidate it. The
    predicate requires a real security-relevant gateway decision that governed an
    externally-authorized, bounded operation but used content shape as an
    authority proxy without consuming actor context, producing an operationally
    effective authorized denial. A self-declared-only actor, an out-of-scope
    action, correctly consumed context, no authoritative decision, or no
    operational effect must all break it.
    """
    if incident.get("code") != "AICE-602":
        return True
    cd = incident.get("code_details", {})
    action = cd.get("reviewed_action", {})
    actor = cd.get("actor", {})
    scope = cd.get("scope", {})
    gw = cd.get("gateway", {})
    decision = cd.get("decision", {})
    result = cd.get("result", {})
    effect = incident.get("workflow_effect", [])
    return all(
        [
            action.get("security_relevant") is True,
            action.get("operation_within_authority") is True,
            actor.get("identity_established") is True,
            actor.get("authority_established") is True,
            actor.get("authority_self_declared_only") is False,
            scope.get("purpose_bounded") is True,
            scope.get("target_bounded") is True,
            gw.get("decision_applied") is True,
            gw.get("actor_context_required") is True,
            gw.get("actor_context_consumed") is False,
            gw.get("content_shape_used_as_authority_proxy") is True,
            decision.get("authorized_action_denied") is True,
            decision.get("denial_operationally_effective") is True,
            result.get("authority_aware_governance_established") is False,
            "STATE_UNCHANGED" in effect,
            "BLOCK_ACCEPTANCE" in effect,
        ]
    )


def _full_authority_inversion_valid(
    authorized_denied: bool, untrusted_admitted: bool, comparable_gateway_semantics: bool
) -> bool:
    """A full authority inversion requires BOTH branches AND proven comparable
    gateway/policy semantics (same gateway or established policy equivalence).
    Two unrelated control planes must not be combined into a full-inversion claim."""
    return authorized_denied and untrusted_admitted and comparable_gateway_semantics


def test_aice_602_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_602()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_registry_and_doc_metadata_agree_for_602():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-602")
    assert entry["title"] == AICE_602_TITLE
    assert entry["machine_name"] == AICE_602_MACHINE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    assert entry["default_retryability"] == "requires_new_evidence"
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-602.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-602 — {AICE_602_TITLE}")
    # machine name present in the doc (registry <-> doc machine-name parity)
    assert AICE_602_MACHINE in doc
    # "Bad Gateway" is the non-normative alias / pun, not the canonical machine name
    assert "Bad Gateway" in doc
    assert AICE_602_MACHINE != "Bad Gateway"
    assert _load_602()["title"] == entry["title"]


def test_602_example_requires_state_unchanged():
    incident = _load_602()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_602_example_blocks_acceptance():
    incident = _load_602()
    assert "BLOCK_ACCEPTANCE" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "BLOCK_ACCEPTANCE"]
    assert not _aice_602_invariants_ok(incident)


def test_602_canonical_example_satisfies_invariants():
    assert _aice_602_invariants_ok(_load_602())


def test_602_authorized_denial_branch_alone_is_sufficient():
    # The canonical example proves AICE-602 with authorized denial only; the
    # untrusted-admission branch is not required.
    cd = _load_602()["code_details"]
    assert cd["decision"]["authorized_action_denied"] is True
    assert cd["decision"]["untrusted_action_admitted"] is False
    assert cd["authority_context_failure_mode"] == "AUTHORIZED_DENIAL"


def test_602_uses_context_required_but_not_establishable_subform():
    # HF sources establish subform B (no trusted authority channel), NOT that a
    # signed actor-context field was supplied and ignored (subform A).
    cd = _load_602()["code_details"]
    assert cd["context_failure_subform"] == "CONTEXT_REQUIRED_BUT_NOT_ESTABLISHABLE"


def test_602_self_declared_authority_alone_invalidates_predicate():
    incident = _load_602()
    incident["code_details"]["actor"]["authority_self_declared_only"] = True
    assert not _aice_602_invariants_ok(incident)


def test_602_out_of_scope_action_is_not_602():
    # A responder requesting something outside their authority is a correct denial,
    # not a gateway authority-context failure.
    incident = _load_602()
    incident["code_details"]["reviewed_action"]["operation_within_authority"] = False
    assert not _aice_602_invariants_ok(incident)


def test_602_correctly_consumed_context_is_not_602():
    # If the gateway consumed actor authority context and decided consistently,
    # the predicate must not hold.
    incident = _load_602()
    incident["code_details"]["gateway"]["actor_context_consumed"] = True
    assert not _aice_602_invariants_ok(incident)


def test_602_content_proxy_removed_is_not_602():
    # Remove the defining defect (content shape used as authority proxy) → not 602.
    incident = _load_602()
    incident["code_details"]["gateway"]["content_shape_used_as_authority_proxy"] = False
    assert not _aice_602_invariants_ok(incident)


def test_602_no_operational_effect_is_not_602():
    incident = _load_602()
    incident["code_details"]["decision"]["denial_operationally_effective"] = False
    assert not _aice_602_invariants_ok(incident)


def test_602_no_authoritative_decision_is_not_602():
    # A transport/timeout failure has no authoritative gateway decision (that is
    # AICE-614 territory); without decision_applied the predicate must not hold.
    incident = _load_602()
    incident["code_details"]["gateway"]["decision_applied"] = False
    assert not _aice_602_invariants_ok(incident)


def test_602_advancing_workflow_state_invalidates_example():
    incident = _load_602()
    incident["workflow_effect"] = ["BLOCK_ACCEPTANCE"]  # drops STATE_UNCHANGED
    assert list(_validator().iter_errors(incident))
    assert not _aice_602_invariants_ok(incident)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda cd: cd["actor"].__setitem__("authority_established", False),
        lambda cd: cd["actor"].__setitem__("authority_self_declared_only", True),
        lambda cd: cd["scope"].__setitem__("purpose_bounded", False),
        lambda cd: cd["scope"].__setitem__("target_bounded", False),
        lambda cd: cd["gateway"].__setitem__("actor_context_consumed", True),
        lambda cd: cd["gateway"].__setitem__("actor_context_required", False),
        lambda cd: cd["decision"].__setitem__("authorized_action_denied", False),
    ],
    ids=[
        "authority_not_established",
        "authority_self_declared",
        "purpose_unbounded",
        "target_scope_absent",
        "context_consumed",
        "context_not_required",
        "no_authorized_denial",
    ],
)
def test_602_mutations_invalidate_authority_context_predicate(mutate):
    incident = _load_602()
    mutate(incident["code_details"])
    assert not _aice_602_invariants_ok(incident)


def test_602_full_inversion_requires_comparable_gateway_semantics():
    # Both branches proven + comparable gateway semantics → valid full inversion.
    assert _full_authority_inversion_valid(True, True, True)
    # Both branches from separate, unproven-equivalent control planes → NOT a
    # full inversion (only a SEPARATE_CONTROL_PLANE_CONTRAST).
    assert not _full_authority_inversion_valid(True, True, False)
    # One branch alone is never a full inversion.
    assert not _full_authority_inversion_valid(True, False, True)


def test_602_example_does_not_claim_full_inversion_or_name_provider():
    incident = _load_602()
    raw = EXAMPLE_602.read_text(encoding="utf-8")
    # The verified HF scope is one-sided (authorized denial); no full-inversion claim.
    assert incident["code_details"]["authority_context_failure_mode"] != "FULL_AUTHORITY_INVERSION"
    assert incident["code_details"]["decision"]["untrusted_action_admitted"] is False
    # The sources name no specific commercial provider; the example must not either.
    for provider in ("OpenAI", "Anthropic", "Google", "Gemini", "Claude", "GPT"):
        assert provider not in raw, f"example must not name provider {provider}"


def test_602_example_historical_scope_is_narrow_and_verified():
    incident = _load_602()
    notes = incident["notes"]
    assert "VERIFIED_PUBLIC_HISTORICAL_SCOPE" in notes
    # Explicit non-claims the narrow scope must NOT assert as fact.
    assert "SEPARATE_CONTROL_PLANE_CONTRAST" in notes
    assert "full authority inversion" in notes.lower() or "FULL_AUTHORITY_INVERSION" in notes


# --- Version / defined-set / $id parity ---------------------------------------

def test_spec_version_is_consistently_0_9_0():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    schema = _load_schema()
    assert registry["spec_version"] == "0.9.0"
    assert schema["properties"]["spec_version"]["const"] == "0.9.0"
    assert check_aice.EXPECTED_VERSION == "0.9.0"
    for ex in EXAMPLE_FILES:
        data = json.loads(ex.read_text(encoding="utf-8"))
        assert data["spec_version"] == "0.9.0", ex.name


def test_schema_id_is_v0_9_and_unique():
    schema = _load_schema()
    assert schema["$id"] == "urn:cap:schema:aice-incident:v0.9"
    # unique across spec/: no other schema carries this aice-incident id
    spec_dir = ROOT / "spec"
    hits = []
    for p in spec_dir.rglob("*.json"):
        text = p.read_text(encoding="utf-8")
        if "urn:cap:schema:aice-incident:v0.9" in text:
            hits.append(p.name)
    assert hits == ["incident.schema.json"], hits


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


def _tamper_remove_602(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["codes"] = [c for c in data["codes"] if c.get("code") != "AICE-602"]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_rename_602_to_600(tmp: Path) -> None:
    # Rename AICE-602 to the UNASSIGNED code AICE-600: breaks set membership and
    # gives an unassigned code a registry entry.
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    for c in data["codes"]:
        if c.get("code") == "AICE-602":
            c["code"] = "AICE-600"
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_rename_602_to_615(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    for c in data["codes"]:
        if c.get("code") == "AICE-602":
            c["code"] = "AICE-615"
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_delete_602_doc(tmp: Path) -> None:
    (tmp / "spec" / "aice" / "codes" / "AICE-602.md").unlink()


def _tamper_break_602_link(tmp: Path) -> None:
    doc = tmp / "spec" / "aice" / "codes" / "AICE-602.md"
    doc.write_text(
        doc.read_text(encoding="utf-8") + "\n[broken](./NONEXISTENT-602.md)\n",
        encoding="utf-8",
    )


def _tamper_false_contiguous_range(tmp: Path) -> None:
    # Re-introduce a contiguity-promising range field (a false 'AICE-602..AICE-614'
    # claim that hides the unassigned AICE-603).
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["canonical_code_range"] = ["AICE-602", "AICE-614"]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_stale_defined_set(tmp: Path) -> None:
    # Stale set that drops AICE-602 (the pre-0.7 contiguous 604..614 set).
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["canonical_defined_set"] = [f"AICE-{n}" for n in range(604, 615)]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_stale_count_11(tmp: Path) -> None:
    # Drop AICE-602 from both the entries and the declared set so the defined
    # set no longer matches the expected sparse set (a stale pre-602 shape).
    # Retained from the v0.7 suite; still detects the dropped code under v0.8.
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["codes"] = [c for c in data["codes"] if c.get("code") != "AICE-602"]
    data["canonical_defined_set"] = [
        c for c in data["canonical_defined_set"] if c != "AICE-602"
    ]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_placeholder_600(tmp: Path) -> None:
    # Insert a placeholder entry for the UNASSIGNED code AICE-600.
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["codes"].append(
        {
            "code": "AICE-600",
            "title": "Placeholder",
            "default_workflow_effect": ["STATE_UNCHANGED"],
            "default_retryability": "requires_new_evidence",
            "spec_status": "draft",
        }
    )
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_stale_version(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["spec_version"] = "0.6.0"
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_stale_schema_id(tmp: Path) -> None:
    schema = tmp / "spec" / "aice" / "incident.schema.json"
    data = json.loads(schema.read_text(encoding="utf-8"))
    data["$id"] = "urn:cap:schema:aice-incident:v0.6"
    schema.write_text(json.dumps(data), encoding="utf-8")


def _tamper_remove_code(tmp: Path, code: str) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["codes"] = [c for c in data["codes"] if c.get("code") != code]
    data["canonical_defined_set"] = [c for c in data["canonical_defined_set"] if c != code]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_remove_615(tmp: Path) -> None:
    _tamper_remove_code(tmp, "AICE-615")


def _tamper_remove_616(tmp: Path) -> None:
    _tamper_remove_code(tmp, "AICE-616")


def _tamper_remove_618(tmp: Path) -> None:
    _tamper_remove_code(tmp, "AICE-618")


def _tamper_stale_count_14(tmp: Path) -> None:
    # Drop AICE-618 so the defined count is a stale 14 instead of 15.
    _tamper_remove_code(tmp, "AICE-618")


def _tamper_placeholder_617(tmp: Path) -> None:
    # Insert a placeholder entry for the UNASSIGNED code AICE-617.
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["codes"].append(
        {
            "code": "AICE-617",
            "title": "Placeholder",
            "default_workflow_effect": ["STATE_UNCHANGED"],
            "default_retryability": "requires_new_evidence",
            "spec_status": "draft",
        }
    )
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_false_contiguous_range_618(tmp: Path) -> None:
    # A false 'AICE-602..AICE-618' contiguity claim that hides unassigned 603/617.
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["canonical_code_range"] = ["AICE-602", "AICE-618"]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_stale_defined_set_v07(tmp: Path) -> None:
    # The pre-0.8 defined set (602 + 604..614) — stale: missing 615/616/618.
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["canonical_defined_set"] = ["AICE-602"] + [f"AICE-{n}" for n in range(604, 615)]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_stale_version_07(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["spec_version"] = "0.7.0"
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_stale_schema_id_v07(tmp: Path) -> None:
    schema = tmp / "spec" / "aice" / "incident.schema.json"
    data = json.loads(schema.read_text(encoding="utf-8"))
    data["$id"] = "urn:cap:schema:aice-incident:v0.7"
    schema.write_text(json.dumps(data), encoding="utf-8")


def _tamper_duplicate_machine_name(tmp: Path) -> None:
    # Give AICE-616 the same machine_name as AICE-615 (duplicate must be caught).
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    for c in data["codes"]:
        if c.get("code") == "AICE-616":
            c["machine_name"] = "ACCEPTED_STATE_ROLLBACK_ERASURE"
    reg.write_text(json.dumps(data), encoding="utf-8")


@pytest.mark.parametrize(
    "tamper",
    [
        _tamper_remove_614,
        _tamper_rename_615,
        _tamper_delete_doc,
        _tamper_break_link,
        _tamper_remove_602,
        _tamper_rename_602_to_600,
        _tamper_rename_602_to_615,
        _tamper_delete_602_doc,
        _tamper_break_602_link,
        _tamper_false_contiguous_range,
        _tamper_stale_defined_set,
        _tamper_stale_count_11,
        _tamper_placeholder_600,
        _tamper_stale_version,
        _tamper_stale_schema_id,
        _tamper_remove_615,
        _tamper_remove_616,
        _tamper_remove_618,
        _tamper_stale_count_14,
        _tamper_placeholder_617,
        _tamper_false_contiguous_range_618,
        _tamper_stale_defined_set_v07,
        _tamper_stale_version_07,
        _tamper_stale_schema_id_v07,
        _tamper_duplicate_machine_name,
    ],
    ids=[
        "remove_614_from_registry",
        "rename_614_to_615",
        "delete_614_doc",
        "break_614_link",
        "remove_602_from_registry",
        "rename_602_to_unassigned_600",
        "rename_602_to_615",
        "delete_602_doc",
        "break_602_link",
        "false_contiguous_range",
        "stale_defined_set",
        "stale_count_11",
        "placeholder_unassigned_600",
        "stale_spec_version",
        "stale_schema_id",
        "remove_615_from_registry",
        "remove_616_from_registry",
        "remove_618_from_registry",
        "stale_count_14",
        "placeholder_unassigned_617",
        "false_contiguous_range_618",
        "stale_defined_set_v07",
        "stale_spec_version_07",
        "stale_schema_id_v07",
        "duplicate_machine_name",
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


# --- AICE-615: Accepted-State Rollback Erasure ---------------------------------

AICE_615_TITLE = "Accepted-State Rollback Erasure"
AICE_615_MACHINE = "ACCEPTED_STATE_ROLLBACK_ERASURE"


def _load_615():
    return json.loads(EXAMPLE_615.read_text(encoding="utf-8"))


def _aice_615_invariants_ok(incident) -> bool:
    """Focused canonical-example invariants for AICE-615 (restore identity).

    The predicate requires a real mutation, a non-accepting terminal, a
    repository-relative rollback target (not the exact preimage), preimage bytes
    that were accepted/unrelated and got erased, and the block effect. An
    exact-preimage digest-verified restore, or a clean HEAD==preimage case with
    nothing to erase, must break it.
    """
    if incident.get("code") != "AICE-615":
        return True
    cd = incident.get("code_details", {})
    ep = cd.get("episode", {})
    rb = cd.get("rollback", {})
    pre = cd.get("preimage", {})
    correct = cd.get("correct_terminal", {})
    effect = incident.get("workflow_effect", [])
    return all(
        [
            ep.get("mutated_real_target") is True,
            ep.get("non_accepting_terminal") is True,
            rb.get("target_derivation") == "REPOSITORY_RELATIVE",
            rb.get("exact_episode_preimage_used") is False,
            rb.get("restored_bytes_equal_episode_preimage") is False,
            pre.get("accepted_or_unrelated_bytes_present") is True,
            pre.get("accepted_bytes_erased") is True,
            correct.get("required_target") == "EXACT_EPISODE_PREIMAGE",
            "STATE_UNCHANGED" in effect,
            "BLOCK_ACCEPTANCE" in effect,
        ]
    )


def test_aice_615_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_615()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_registry_and_doc_metadata_agree_for_615():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-615")
    assert entry["title"] == AICE_615_TITLE
    assert entry["machine_name"] == AICE_615_MACHINE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    assert entry["default_retryability"] == "requires_new_evidence"
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-615.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-615 — {AICE_615_TITLE}")
    assert AICE_615_MACHINE in doc
    assert _load_615()["title"] == entry["title"]


def test_615_example_requires_state_unchanged():
    incident = _load_615()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_615_canonical_example_satisfies_invariants():
    assert _aice_615_invariants_ok(_load_615())


def test_615_repository_relative_rollback_erasing_accepted_state_triggers():
    cd = _load_615()["code_details"]
    assert cd["rollback"]["target_derivation"] == "REPOSITORY_RELATIVE"
    assert cd["preimage"]["accepted_bytes_erased"] is True


def test_615_exact_preimage_digest_verified_restore_is_not_615():
    incident = _load_615()
    incident["code_details"]["rollback"]["target_derivation"] = "EXACT_EPISODE_PREIMAGE"
    incident["code_details"]["rollback"]["exact_episode_preimage_used"] = True
    incident["code_details"]["rollback"]["restored_bytes_equal_episode_preimage"] = True
    assert not _aice_615_invariants_ok(incident)


def test_615_clean_head_equals_preimage_is_false_positive():
    # Nothing accepted existed to erase -> not AICE-615.
    incident = _load_615()
    incident["code_details"]["preimage"]["accepted_or_unrelated_bytes_present"] = False
    incident["code_details"]["preimage"]["accepted_bytes_erased"] = False
    assert not _aice_615_invariants_ok(incident)


def test_615_example_is_representative_not_historical():
    incident = _load_615()
    assert "REPRESENTATIVE_EXAMPLE" in incident["notes"]
    assert "NOT_A_VERIFIED_HISTORICAL_INCIDENT" in incident["notes"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda cd: cd["episode"].__setitem__("mutated_real_target", False),
        lambda cd: cd["episode"].__setitem__("non_accepting_terminal", False),
        lambda cd: cd["rollback"].__setitem__("target_derivation", "EXACT_EPISODE_PREIMAGE"),
        lambda cd: cd["rollback"].__setitem__("restored_bytes_equal_episode_preimage", True),
        lambda cd: cd["preimage"].__setitem__("accepted_bytes_erased", False),
    ],
    ids=[
        "no_real_mutation",
        "accepting_terminal",
        "exact_preimage_target",
        "restored_equals_preimage",
        "nothing_erased",
    ],
)
def test_615_mutations_invalidate_erasure_predicate(mutate):
    incident = _load_615()
    mutate(incident["code_details"])
    assert not _aice_615_invariants_ok(incident)


# --- AICE-616: Baseline Diff Conflation ----------------------------------------

AICE_616_TITLE = "Baseline Diff Conflation"
AICE_616_MACHINE = "BASELINE_DIFF_CONFLATION"


def _load_616():
    return json.loads(EXAMPLE_616.read_text(encoding="utf-8"))


def _aice_616_invariants_ok(incident) -> bool:
    """Focused canonical-example invariants for AICE-616 (review-input identity).

    The predicate requires a review payload derived from a repository baseline
    diff (not the normalized episode delta), a dirty target with non-episode
    bytes, an authority-affecting conflation, and the block effect. An
    episode-delta payload, or a clean worktree where repo diff == episode delta,
    must break it. It must hold even when the verifier is independent.
    """
    if incident.get("code") != "AICE-616":
        return True
    cd = incident.get("code_details", {})
    rp = cd.get("review_payload", {})
    tgt = cd.get("target", {})
    conf = cd.get("conflation", {})
    correct = cd.get("correct_terminal", {})
    effect = incident.get("workflow_effect", [])
    return all(
        [
            rp.get("derived_from") == "GIT_DIFF_AGAINST_HEAD",
            rp.get("equals_normalized_episode_delta") is False,
            tgt.get("dirty_vs_head") is True,
            tgt.get("contains_non_episode_bytes") is True,
            conf.get("authority_affecting") is True,
            conf.get("verifier_reviews_non_episode_bytes") is True,
            correct.get("required_payload") == "NORMALIZED_EPISODE_PREIMAGE_TO_POSTIMAGE_DELTA",
            "STATE_UNCHANGED" in effect,
            "BLOCK_ACCEPTANCE" in effect,
        ]
    )


def test_aice_616_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_616()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_registry_and_doc_metadata_agree_for_616():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-616")
    assert entry["title"] == AICE_616_TITLE
    assert entry["machine_name"] == AICE_616_MACHINE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    assert entry["default_retryability"] == "requires_new_evidence"
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-616.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-616 — {AICE_616_TITLE}")
    assert AICE_616_MACHINE in doc
    assert _load_616()["title"] == entry["title"]


def test_616_example_requires_state_unchanged():
    incident = _load_616()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_616_canonical_example_satisfies_invariants():
    assert _aice_616_invariants_ok(_load_616())


def test_616_dirty_repo_diff_with_prior_accepted_bytes_triggers():
    cd = _load_616()["code_details"]
    assert cd["review_payload"]["derived_from"] == "GIT_DIFF_AGAINST_HEAD"
    assert cd["target"]["contains_non_episode_bytes"] is True


def test_616_exact_normalized_episode_delta_is_not_616():
    incident = _load_616()
    incident["code_details"]["review_payload"]["derived_from"] = "NORMALIZED_EPISODE_DELTA"
    incident["code_details"]["review_payload"]["equals_normalized_episode_delta"] = True
    assert not _aice_616_invariants_ok(incident)


def test_616_clean_worktree_repo_diff_equals_episode_delta_is_false_positive():
    incident = _load_616()
    incident["code_details"]["target"]["dirty_vs_head"] = False
    incident["code_details"]["target"]["contains_non_episode_bytes"] = False
    assert not _aice_616_invariants_ok(incident)


def test_616_holds_even_with_independent_verifier():
    # Independence (AICE-608) is orthogonal: a fully independent verifier that
    # receives the wrong payload still yields AICE-616.
    incident = _load_616()
    assert incident["code_details"]["conflation"]["verifier_independent"] is True
    assert _aice_616_invariants_ok(incident)


def test_616_example_is_representative_not_historical():
    incident = _load_616()
    assert "REPRESENTATIVE_EXAMPLE" in incident["notes"]
    assert "NOT_A_VERIFIED_HISTORICAL_INCIDENT" in incident["notes"]


def test_615_and_616_do_not_collapse_and_are_separable():
    # 615 governs restore identity (rollback fields); 616 governs review-input
    # identity (review_payload fields). Neither example carries the other's
    # defining structure — they are separable, not one class.
    cd615 = _load_615()["code_details"]
    cd616 = _load_616()["code_details"]
    assert "rollback" in cd615 and "review_payload" not in cd615
    assert "review_payload" in cd616 and "rollback" not in cd616
    # The 616 example does not satisfy the 615 predicate and vice versa when
    # each is coerced to the other's code with mismatched details.
    coerced = _load_616()
    coerced["code"] = "AICE-615"
    assert not _aice_615_invariants_ok(coerced)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda cd: cd["review_payload"].__setitem__("derived_from", "NORMALIZED_EPISODE_DELTA"),
        lambda cd: cd["review_payload"].__setitem__("equals_normalized_episode_delta", True),
        lambda cd: cd["target"].__setitem__("dirty_vs_head", False),
        lambda cd: cd["target"].__setitem__("contains_non_episode_bytes", False),
        lambda cd: cd["conflation"].__setitem__("authority_affecting", False),
    ],
    ids=[
        "payload_is_episode_delta",
        "payload_equals_episode_delta",
        "clean_worktree",
        "no_non_episode_bytes",
        "not_authority_affecting",
    ],
)
def test_616_mutations_invalidate_conflation_predicate(mutate):
    incident = _load_616()
    mutate(incident["code_details"])
    assert not _aice_616_invariants_ok(incident)


# --- AICE-618: Verifier Gated by Coder Evidence Ceiling ------------------------

AICE_618_TITLE = "Verifier Gated by Coder Evidence Ceiling"
AICE_618_MACHINE = "VERIFIER_GATED_BY_CODER_EVIDENCE_CEILING"


def _load_618():
    return json.loads(EXAMPLE_618.read_text(encoding="utf-8"))


def _aice_618_invariants_ok(incident) -> bool:
    """Focused canonical-example invariants for AICE-618 (verifier eligibility).

    The predicate requires a verifier role, a coder-execution-evidence ceiling
    applied to it, a real eligibility change excluding valid candidates, a
    required control made unreachable, coder output byte-for-byte unchanged, and
    the block effect. A role-aware verifier ceiling, an unchanged coder output
    assumption violated, or an infrastructure-sourced exclusion must break it.
    """
    if incident.get("code") != "AICE-618":
        return True
    cd = incident.get("code_details", {})
    ceiling = cd.get("ceiling_applied", {})
    elig = cd.get("eligibility_change", {})
    ctrl = cd.get("required_control", {})
    coder = cd.get("coder_output", {})
    effect = incident.get("workflow_effect", [])
    return all(
        [
            cd.get("role") == "verifier",
            ceiling.get("source") == "CODER_EXECUTION_EVIDENCE",
            ceiling.get("correct_source_for_role") == "VERIFIER_REGISTRY_REVIEW_CAPABILITY",
            elig.get("real") is True,
            elig.get("valid_candidates_excluded") is True,
            ctrl.get("became_unreachable") is True,
            coder.get("byte_for_byte_unchanged") is True,
            "STATE_UNCHANGED" in effect,
            "BLOCK_ACCEPTANCE" in effect,
        ]
    )


def test_aice_618_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_618()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_registry_and_doc_metadata_agree_for_618():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-618")
    assert entry["title"] == AICE_618_TITLE
    assert entry["machine_name"] == AICE_618_MACHINE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    assert entry["default_retryability"] == "requires_new_evidence"
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-618.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-618 — {AICE_618_TITLE}")
    assert AICE_618_MACHINE in doc
    assert _load_618()["title"] == entry["title"]


def test_618_narrow_title_not_broad_alias():
    # The narrowest justified title is canonical; the broad operator-era phrasing
    # must NOT be the normative title or machine name.
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-618")
    assert entry["title"] == "Verifier Gated by Coder Evidence Ceiling"
    assert entry["machine_name"] == "VERIFIER_GATED_BY_CODER_EVIDENCE_CEILING"
    assert "ROLE_SEMANTIC_RISK_CEILING_CONFLATION" != entry["machine_name"]
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-618.md").read_text(encoding="utf-8")
    assert doc.startswith("# AICE-618 — Verifier Gated by Coder Evidence Ceiling")


def test_618_example_requires_state_unchanged():
    incident = _load_618()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_618_canonical_example_satisfies_invariants():
    assert _aice_618_invariants_ok(_load_618())


def test_618_coder_ceiling_applied_to_verifier_triggers():
    cd = _load_618()["code_details"]
    assert cd["role"] == "verifier"
    assert cd["ceiling_applied"]["source"] == "CODER_EXECUTION_EVIDENCE"
    assert cd["required_control"]["became_unreachable"] is True


def test_618_role_aware_verifier_capability_is_not_618():
    incident = _load_618()
    incident["code_details"]["ceiling_applied"]["source"] = "VERIFIER_REGISTRY_REVIEW_CAPABILITY"
    incident["code_details"]["eligibility_change"]["valid_candidates_excluded"] = False
    incident["code_details"]["required_control"]["became_unreachable"] = False
    assert not _aice_618_invariants_ok(incident)


def test_618_requires_coder_output_byte_for_byte_unchanged():
    # A deliberate coder change is a different episode; 618 requires the coder
    # path byte-for-byte unchanged.
    incident = _load_618()
    incident["code_details"]["coder_output"]["byte_for_byte_unchanged"] = False
    assert not _aice_618_invariants_ok(incident)


def test_618_infrastructure_sourced_exclusion_is_not_618():
    # An exclusion sourced from infrastructure failure (AICE-614 territory), not
    # a coder evidence ceiling, must not satisfy AICE-618.
    incident = _load_618()
    incident["code_details"]["ceiling_applied"]["source"] = "INFRASTRUCTURE_FAILURE"
    assert not _aice_618_invariants_ok(incident)


def test_618_inert_ceiling_change_excluding_no_candidate_is_not_618():
    incident = _load_618()
    incident["code_details"]["eligibility_change"]["real"] = False
    incident["code_details"]["eligibility_change"]["valid_candidates_excluded"] = False
    assert not _aice_618_invariants_ok(incident)


def test_618_example_is_representative_not_historical():
    incident = _load_618()
    assert "REPRESENTATIVE_EXAMPLE" in incident["notes"]
    assert "NOT_A_VERIFIED_HISTORICAL_INCIDENT" in incident["notes"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda cd: cd.__setitem__("role", "coder"),
        lambda cd: cd["ceiling_applied"].__setitem__("source", "VERIFIER_REGISTRY_REVIEW_CAPABILITY"),
        lambda cd: cd["eligibility_change"].__setitem__("real", False),
        lambda cd: cd["eligibility_change"].__setitem__("valid_candidates_excluded", False),
        lambda cd: cd["required_control"].__setitem__("became_unreachable", False),
        lambda cd: cd["coder_output"].__setitem__("byte_for_byte_unchanged", False),
    ],
    ids=[
        "role_is_coder",
        "ceiling_source_role_aware",
        "eligibility_change_inert",
        "no_candidate_excluded",
        "control_reachable",
        "coder_output_changed",
    ],
)
def test_618_mutations_invalidate_ceiling_predicate(mutate):
    incident = _load_618()
    mutate(incident["code_details"])
    assert not _aice_618_invariants_ok(incident)


def test_618_distinct_from_602_610_611_614():
    # 618 governs verifier eligibility; it carries none of the defining fields of
    # 602 (gateway/actor context), and its example is a distinct code.
    cd618 = _load_618()["code_details"]
    assert "gateway" not in cd618
    assert "role" in cd618 and "required_control" in cd618
    for other in (_load_602(), _load_610(), _load_611(), _load_614()):
        assert other["code"] != "AICE-618"


# --- AICE-601: Minimum Sufficient Mechanism Bypass -----------------------------

AICE_601_TITLE = "Minimum Sufficient Mechanism Bypass"
AICE_601_MACHINE = "MINIMUM_SUFFICIENT_MECHANISM_BYPASS"


def _load_601():
    return json.loads(EXAMPLE_601.read_text(encoding="utf-8"))


def _aice_601_invariants_ok(incident) -> bool:
    """Focused canonical-example invariants for AICE-601 (mechanism bypass).

    The predicate requires a bounded objective with an established minimum
    sufficient path that satisfies all active invariants, a larger mechanism made
    prerequisite with NO unique necessity witness, an increase in surface/cost,
    and displacement of the sufficient path. A verified necessity witness, a
    sufficient path that does not preserve invariants, or no displacement must
    all break it.
    """
    if incident.get("code") != "AICE-601":
        return True
    cd = incident.get("code_details", {})
    obj = cd.get("objective", {})
    msp = cd.get("minimum_sufficient_path", {})
    larger = cd.get("larger_mechanism", {})
    exp = cd.get("expansion_effect", {})
    disp = cd.get("displacement", {})
    effect = incident.get("workflow_effect", [])
    return all(
        [
            obj.get("mechanically_bounded") is True,
            msp.get("identified") is True,
            msp.get("satisfies_all_active_invariants") is True,
            larger.get("introduced_or_made_prerequisite") is True,
            larger.get("unique_necessity_witness") is False,
            exp.get("increases_surface_or_cost") is True,
            disp.get("sufficient_path_delayed_blocked_displaced_or_denied") is True,
            "STATE_UNCHANGED" in effect,
            "BLOCK_ACCEPTANCE" in effect,
        ]
    )


def test_aice_601_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_601()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_registry_and_doc_metadata_agree_for_601():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-601")
    assert entry["title"] == AICE_601_TITLE
    assert entry["machine_name"] == AICE_601_MACHINE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    assert entry["default_retryability"] == "requires_new_evidence"
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-601.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-601 — {AICE_601_TITLE}")
    assert AICE_601_MACHINE in doc
    assert _load_601()["title"] == entry["title"]


def test_601_example_requires_state_unchanged():
    incident = _load_601()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_601_canonical_example_satisfies_invariants():
    assert _aice_601_invariants_ok(_load_601())


def test_601_necessity_witness_present_is_not_601():
    # A verified unique necessity witness for the expansion is the primary false
    # positive guard: with it, the larger mechanism is justified, not an incident.
    incident = _load_601()
    incident["code_details"]["larger_mechanism"]["unique_necessity_witness"] = True
    assert not _aice_601_invariants_ok(incident)


def test_601_no_displacement_is_not_601():
    # Architecture merely proposed and refused (no displacement) is not an incident.
    incident = _load_601()
    incident["code_details"]["displacement"]["sufficient_path_delayed_blocked_displaced_or_denied"] = False
    assert not _aice_601_invariants_ok(incident)


def test_601_insufficient_smaller_path_is_not_601():
    # If the smaller path does not satisfy all active invariants, it was not a
    # sufficient path and the expansion may be legitimate.
    incident = _load_601()
    incident["code_details"]["minimum_sufficient_path"]["satisfies_all_active_invariants"] = False
    assert not _aice_601_invariants_ok(incident)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda cd: cd["objective"].__setitem__("mechanically_bounded", False),
        lambda cd: cd["minimum_sufficient_path"].__setitem__("identified", False),
        lambda cd: cd["larger_mechanism"].__setitem__("introduced_or_made_prerequisite", False),
        lambda cd: cd["larger_mechanism"].__setitem__("unique_necessity_witness", True),
        lambda cd: cd["expansion_effect"].__setitem__("increases_surface_or_cost", False),
        lambda cd: cd["displacement"].__setitem__("sufficient_path_delayed_blocked_displaced_or_denied", False),
    ],
    ids=[
        "objective_unbounded",
        "no_sufficient_path",
        "expansion_not_prerequisite",
        "necessity_witness_present",
        "no_surface_increase",
        "no_displacement",
    ],
)
def test_601_mutations_invalidate_bypass_predicate(mutate):
    incident = _load_601()
    mutate(incident["code_details"])
    assert not _aice_601_invariants_ok(incident)


def test_601_example_scope_is_narrow_and_verified():
    notes = _load_601()["notes"]
    assert "VERIFIED_INTERNAL_HISTORICAL_SCOPE" in notes
    # The negative controls are recorded and must not be read as this incident.
    assert "proposed and refused" in notes
    assert "complexity alone" in notes


# --- AICE-603: Governance-Induced Service Unavailability -----------------------

AICE_603_TITLE = "Governance-Induced Service Unavailability"
AICE_603_MACHINE = "GOVERNANCE_INDUCED_SERVICE_UNAVAILABILITY"

_UNAVAILABLE_STATES = {"UNAVAILABLE", "UNREACHABLE", "UNSATISFIABLE"}


def _load_603():
    return json.loads(EXAMPLE_603.read_text(encoding="utf-8"))


def _aice_603_invariants_ok(incident) -> bool:
    """Focused canonical-example invariants for AICE-603 (governance unavailability).

    The predicate requires an existing capability, an admissible alternative
    path, a mandatory governance dependency NOT uniquely required, that
    dependency unavailable/unreachable/unsatisfiable, and the capability withheld.
    A genuinely absent capability, no admissible alternative, a uniquely-required
    dependency, or a satisfiable dependency must all break it.
    """
    if incident.get("code") != "AICE-603":
        return True
    cd = incident.get("code_details", {})
    cap = cd.get("capability", {})
    path = cd.get("admissible_path", {})
    dep = cd.get("mandatory_dependency", {})
    withholding = cd.get("withholding", {})
    effect = incident.get("workflow_effect", [])
    return all(
        [
            cap.get("exists") is True,
            path.get("exists") is True,
            dep.get("exists") is True,
            dep.get("uniquely_required_by_objective") is False,
            dep.get("status") in _UNAVAILABLE_STATES,
            withholding.get("capability_withheld_from_authorized_workflow") is True,
            "STATE_UNCHANGED" in effect,
            "BLOCK_ACCEPTANCE" in effect,
        ]
    )


def test_aice_603_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_603()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_registry_and_doc_metadata_agree_for_603():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-603")
    assert entry["title"] == AICE_603_TITLE
    assert entry["machine_name"] == AICE_603_MACHINE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    assert entry["default_retryability"] == "requires_new_evidence"
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-603.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-603 — {AICE_603_TITLE}")
    assert AICE_603_MACHINE in doc
    assert _load_603()["title"] == entry["title"]


def test_603_example_requires_state_unchanged():
    incident = _load_603()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_603_canonical_example_satisfies_invariants():
    assert _aice_603_invariants_ok(_load_603())


def test_603_ordinary_outage_is_not_603():
    # If the underlying capability is genuinely absent, it is an ordinary outage,
    # not governance-induced unavailability.
    incident = _load_603()
    incident["code_details"]["capability"]["exists"] = False
    assert not _aice_603_invariants_ok(incident)


def test_603_no_admissible_alternative_is_not_603():
    # If no admissible alternative path exists, the service is legitimately
    # unavailable.
    incident = _load_603()
    incident["code_details"]["admissible_path"]["exists"] = False
    assert not _aice_603_invariants_ok(incident)


def test_603_uniquely_required_dependency_is_not_603():
    # A dependency uniquely required by a verified safety/independence invariant
    # is not this incident.
    incident = _load_603()
    incident["code_details"]["mandatory_dependency"]["uniquely_required_by_objective"] = True
    assert not _aice_603_invariants_ok(incident)


def test_603_available_dependency_is_not_603():
    # If the mandatory dependency is available/satisfiable, nothing is withheld.
    incident = _load_603()
    incident["code_details"]["mandatory_dependency"]["status"] = "AVAILABLE"
    assert not _aice_603_invariants_ok(incident)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda cd: cd["capability"].__setitem__("exists", False),
        lambda cd: cd["admissible_path"].__setitem__("exists", False),
        lambda cd: cd["mandatory_dependency"].__setitem__("exists", False),
        lambda cd: cd["mandatory_dependency"].__setitem__("uniquely_required_by_objective", True),
        lambda cd: cd["mandatory_dependency"].__setitem__("status", "AVAILABLE"),
        lambda cd: cd["withholding"].__setitem__("capability_withheld_from_authorized_workflow", False),
    ],
    ids=[
        "capability_absent",
        "no_admissible_alternative",
        "no_mandatory_dependency",
        "dependency_uniquely_required",
        "dependency_available",
        "nothing_withheld",
    ],
)
def test_603_mutations_invalidate_unavailability_predicate(mutate):
    incident = _load_603()
    mutate(incident["code_details"])
    assert not _aice_603_invariants_ok(incident)


def test_601_and_603_are_separable():
    # 601 governs mechanism bypass (minimum_sufficient_path fields); 603 governs
    # capability withholding (capability/mandatory_dependency fields). Neither
    # example carries the other's defining structure.
    cd601 = _load_601()["code_details"]
    cd603 = _load_603()["code_details"]
    assert "minimum_sufficient_path" in cd601 and "mandatory_dependency" not in cd601
    assert "mandatory_dependency" in cd603 and "minimum_sufficient_path" not in cd603
