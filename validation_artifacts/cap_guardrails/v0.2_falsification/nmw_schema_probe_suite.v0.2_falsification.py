#!/usr/bin/env python3
"""
NO_MAP_NO_WORK v4.2 schema probe suite (negative tests).

Each probe is a counterexample instance that the cap_guardrails schema
SHOULD reject (or, for P5, should be able to represent) according to the
prose invariants in cap_guardrails.md, but which schema v0.2 currently
mishandles.

Usage:
    pip install jsonschema
    python3 nmw_schema_probe_suite.py path/to/cap_guardrails_schema.json

Exit code 0 when every probe matches its `expect_after_fix` target —
i.e. run this AFTER patching the schema; a clean run means the gaps are
closed. Against the unpatched v0.2 schema, all probes report GAP (this
is the documented baseline).

Probe -> prose invariant map:
    P1  NMW-01  authorizing verdict with level_validation_source=UNVALIDATED
    P2  NMW-02  protected_surface=NO self-claimed (detection UNVALIDATED)
    P3  ev-auth DRIVER_SPOT_CHECKED without spot_check_records / artifacts
    P4  registry-drift rule: seal PASS + registry_update_status=BLOCKED_REGISTRY_DRIFT
    P5  NMW-07  BLOCKED_GUARDRAIL_VERSION_MISMATCH must be representable
    P6  protected rule: protected PASS without any Driver signature surface
    P7  authorizing MODIFY_EXISTING on full self-report (decide: gap or calibration)
    P8  Day-1 minimum field set vs full schema required[] (md/spec contradiction)
"""

import copy
import json
import sys

from jsonschema import Draft202012Validator

GV = "cap_guardrails_v0.2_no_map_no_work_v4.2"
H = "sha256:" + "a" * 64
TS = "2026-06-10T10:00:00Z"


def base_doc():
    return {
        "schema_version": "0.2",
        "guardrail_version": GV,
        "input": {
            "task_id": "t1",
            "anchor_support": "strong",
            "conflict_density": 0.0,
            "stale_critical_triggers": 0,
            "boundary_risk": 0.0,
            "intent_ambiguity": 0.0,
            "irreversible_risk": 0,
            "soft_budget_claims": [],
            "frozen_items": [],
        },
        "decision": {
            "detected_risks": [],
            "action": "no_action",
            "fast_mode_verdict": "FAST_DENIED",
            "forbidding_signals": [],
            "reasons": ["probe baseline"],
        },
        "policy": {
            "fast_mode_is_careless": False,
            "free_budget_extends_analysis": False,
            "allow_fast_mode_for_canonical": False,
            "allow_fast_mode_for_irreversible": False,
            "require_reality_floor_for_soft_claims": True,
        },
    }


def scout_ok():
    return {
        "report_id": "SM-1",
        "artifact": {"path": "artifacts/scout/sm1.json", "hash": H},
        "guardrail_version": GV,
        "requested_change": "add helper",
        "proposed_level": "LEVEL_2",
        "validated_level": "LEVEL_2",
        "level_validation_source": "DRIVER",
        "level_validation_phase": "DRIVER_VALIDATED",
        "registry_status": "REGISTRY_PRESENT_KNOWN_INCOMPLETE",
        "registry_entries_checked": ["MECH-001"],
        "protected_surface": "NO",
        "protected_detection_source": "REGISTRY_PATH_MATCH",
        "protected_registry_entries": [],
        "protected_path_matches": [],
        "evidence_authenticity": "DRIVER_SPOT_CHECKED",
        "evidence_artifacts": [{"path": "artifacts/grep1.txt", "hash": H}],
        "spot_check_records": [
            {
                "selector": "DRIVER",
                "selected_after_artifact_fixation": True,
                "target": "grep1.txt",
                "result": "PASS",
            }
        ],
        "snapshot_hashes": [
            {
                "source_path": "cap_guardrails.md",
                "source_kind": "GUARDRAIL_FILE",
                "hash": H,
                "captured_at": TS,
            }
        ],
        "ttl_expiration": "2026-06-12T10:00:00Z",
        "existing_mechanics": "none similar",
        "pipeline_fit": "pre-TC",
        "duplicate_check": "no duplicates found",
        "already_covered_check": "not covered",
        "conflict_check": "no conflict",
        "dead_code_or_orphan_risk": "low",
        "minimal_change_route": "new helper",
        "need_verdict": "BUILD",
        "scout_status": "VALIDATED",
        "max_scout_iterations": 3,
        "scout_iteration_count": 1,
        "termination_reason": "evidence sufficient",
        "next_action": "proceed to Transition Cost",
    }


def seal_ok():
    return {
        "seal_id": "SEAL-1",
        "guardrail_version": GV,
        "scout_map_report": {"path": "artifacts/scout/sm1.json", "hash": H},
        "need_verdict": "BUILD",
        "validated_level": "LEVEL_2",
        "protected_surface": "NO",
        "protected_detection_source": "REGISTRY_PATH_MATCH",
        "evidence_authenticity": "DRIVER_SPOT_CHECKED",
        "snapshot_hashes": [
            {
                "source_path": "x",
                "source_kind": "SOURCE_FILE",
                "hash": H,
                "captured_at": TS,
            }
        ],
        "seal_status": "PASS",
        "registry_update_status": "UPDATED",
        "telemetry_update_source": "SEAL_PACKET_AGGREGATION",
    }


def build_probes():
    probes = []

    # P0 sanity — a well-formed BUILD map must validate before and after fixes.
    doc = base_doc()
    doc["scout_map"] = scout_ok()
    probes.append(("P0_sanity_wellformed_BUILD", doc, True))

    # P1 NMW-01: authorizing verdict with UNVALIDATED level source.
    doc = base_doc()
    sm = scout_ok()
    sm["level_validation_source"] = "UNVALIDATED"
    sm["level_validation_phase"] = "PROPOSED_PRE_WORK"
    doc["scout_map"] = sm
    probes.append(("P1_NMW01_unvalidated_level_source_on_BUILD", doc, False))

    # P2 NMW-02: protected_surface=NO is self-claimed (detection UNVALIDATED).
    doc = base_doc()
    sm = scout_ok()
    sm["protected_detection_source"] = "UNVALIDATED"
    doc["scout_map"] = sm
    probes.append(("P2_NMW02_selfclaimed_not_protected", doc, False))

    # P3 evidence chain: DRIVER_SPOT_CHECKED with no spot_check_records and
    # an empty evidence_artifacts array.
    doc = base_doc()
    sm = scout_ok()
    del sm["spot_check_records"]
    sm["evidence_artifacts"] = []
    doc["scout_map"] = sm
    probes.append(("P3_spotcheck_claim_without_records", doc, False))

    # P4 registry drift: seal PASS while registry update is blocked.
    doc = base_doc()
    sp = seal_ok()
    sp["registry_update_status"] = "BLOCKED_REGISTRY_DRIFT"
    doc["seal_packet"] = sp
    probes.append(("P4_PASS_with_blocked_registry_update", doc, False))

    # P5 NMW-07 representability: a version-mismatch incident packet.
    # After the fix this instance (or an equivalent carrying the stale scout
    # version in a dedicated field) must VALIDATE, otherwise
    # BLOCKED_GUARDRAIL_VERSION_MISMATCH is a dead enum and
    # guardrail_version_mismatch_rate can never be fed from valid packets.
    doc = base_doc()
    sp = seal_ok()
    sp["seal_id"] = "SEAL-2"
    sp["seal_status"] = "BLOCKED_GUARDRAIL_VERSION_MISMATCH"
    sp["registry_update_status"] = "NOT_REQUIRED"
    # v0.2 has no field for the stale version; the natural-but-invalid encoding:
    sp["guardrail_version"] = "cap_guardrails_v0.1_no_map_no_work_v4.1"
    doc["seal_packet"] = sp
    probes.append(("P5_version_mismatch_must_be_representable", doc, True))

    # P6 protected authority: protected-surface PASS with no Driver signature
    # anywhere (driver_signature exists only inside waiver_record in v0.2).
    doc = base_doc()
    sp = seal_ok()
    sp["seal_id"] = "SEAL-3"
    sp["need_verdict"] = "MODIFY_EXISTING"
    sp["protected_surface"] = "YES"
    sp["protected_detection_source"] = "DIFF_CLASSIFIER"
    sp["evidence_authenticity"] = "RUNTIME_CAPTURED"
    doc["seal_packet"] = sp
    probes.append(("P6_protected_PASS_without_driver_signature", doc, False))

    # P7 calibration question: non-protected MODIFY_EXISTING on pure
    # self-report. If this is a deliberate Anti-Freeze calibration, set the
    # expectation to True and state the rule in cap_guardrails.md explicitly;
    # if not, authorizing verdicts must require scout_status=VALIDATED.
    doc = base_doc()
    sm = scout_ok()
    sm["need_verdict"] = "MODIFY_EXISTING"
    sm["scout_status"] = "SELF_REPORT_ONLY"
    sm["evidence_authenticity"] = "SELF_REPORTED"
    sm["evidence_artifacts"] = []
    sm["level_validation_source"] = "UNVALIDATED"
    sm["level_validation_phase"] = "PROPOSED_PRE_WORK"
    sm["protected_detection_source"] = "UNVALIDATED"
    del sm["spot_check_records"]
    doc["scout_map"] = sm
    probes.append(("P7_modify_existing_full_selfreport", doc, False))

    # P8 Day-1 contradiction: the md "minimum required fields" subset is not
    # schema-valid because scout_map_report.required[] demands the full set
    # (incl. snapshot_hashes minItems 1, vs md "when available"). Either the
    # md Day-1 wording or the schema must change; until then Day-1 packets
    # are INVALID_SCHEMA by construction. Expectation True = Day-1 minimum
    # becomes representable after the chosen fix.
    doc = base_doc()
    doc["scout_map"] = {
        "report_id": "SM-D1",
        "artifact": {"path": "artifacts/scout/d1.json", "hash": H},
        "guardrail_version": GV,
        "requested_change": "day-1 minimal scout",
        "proposed_level": "LEVEL_1",
        "validated_level": "LEVEL_1",
        "level_validation_source": "DRIVER",
        "level_validation_phase": "DRIVER_VALIDATED",
        "registry_status": "REGISTRY_PRESENT_KNOWN_INCOMPLETE",
        "protected_surface": "NO",
        "protected_detection_source": "DRIVER_SEMANTIC_REVIEW",
        "evidence_authenticity": "DRIVER_SPOT_CHECKED",
        "spot_check_records": [
            {
                "selector": "DRIVER",
                "selected_after_artifact_fixation": True,
                "target": "grep1.txt",
                "result": "PASS",
            }
        ],
        "need_verdict": "MODIFY_EXISTING",
        "scout_status": "VALIDATED",
        # md Day-1 minimum omits: registry_entries_checked, protected_* arrays,
        # evidence_artifacts, snapshot_hashes ("when available"), ttl_expiration,
        # the six prose-claim fields, iteration fields, termination, next_action.
    }
    probes.append(("P8_day1_minimum_fieldset", doc, True))

    return probes


def main():
    schema_path = sys.argv[1] if len(sys.argv) > 1 else "cap_guardrails_schema.json"
    with open(schema_path) as f:
        schema = json.load(f)
    validator = Draft202012Validator(schema)

    gaps = 0
    for name, doc, expect_after_fix in build_probes():
        errors = list(validator.iter_errors(copy.deepcopy(doc)))
        is_valid = not errors
        matches = is_valid == expect_after_fix
        status = "OK  " if matches else "GAP "
        if not matches:
            gaps += 1
        want = "VALID" if expect_after_fix else "INVALID"
        got = "VALID" if is_valid else "INVALID"
        print(f"{status}| {name}: want {want}, schema says {got}")
        if not matches and errors:
            e = errors[0]
            print(f"      first error @ {e.json_path}: {e.message[:100]}")

    print(f"\n{gaps} gap(s) against after-fix expectations.")
    sys.exit(1 if gaps else 0)


if __name__ == "__main__":
    main()
