#!/usr/bin/env python3
"""
NO_MAP_NO_WORK v4.2 / schema v0.2.1 regression probe suite.

P1-P7 are negative probes derived from the v0.2 falsification report.
P5 is the positive representability probe for version mismatch.
P8 is deliberately split after the Day-1 decision:
  P8a: reduced Day-1 subset is INVALID by design.
  P8b: full-field Day-1 Driver-only Scout Map is VALID.
"""
import copy, json, sys
from jsonschema import Draft202012Validator

GV = "cap_guardrails_v0.2_1_no_map_no_work_v4.2_schema_enforced"
OLD_GV = "cap_guardrails_v0.2_no_map_no_work_v4.2"
H = "sha256:" + "a" * 64
TS = "2026-06-10T10:00:00Z"

SIG = {
    "key_id": "driver-main",
    "algorithm": "ed25519",
    "signature": "sig-placeholder",
    "signed_payload_hash": H,
    "signed_at": TS,
}

def artifact(path="artifacts/grep1.txt"):
    return {"path": path, "hash": H}

def snapshot(path="cap_guardrails.md", kind="GUARDRAIL_FILE"):
    return {"source_path": path, "source_kind": kind, "hash": H, "captured_at": TS}

def spot(selector="DRIVER", result="PASS"):
    rec = {"selector": selector, "selected_after_artifact_fixation": True, "target": "grep1.txt", "result": result}
    if result == "WAIVED":
        rec["waiver_ref"] = "W-1"
    return rec

def base_doc():
    return {
        "schema_version": "0.2.1",
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
        "artifact": artifact("artifacts/scout/sm1.json"),
        "guardrail_version": GV,
        "requested_change": "add helper",
        "proposed_level": "LEVEL_2",
        "validated_level": "LEVEL_2",
        "level_validation_source": "DRIVER",
        "level_validation_phase": "VALIDATED_PRE_WORK",
        "registry_status": "REGISTRY_PRESENT_KNOWN_INCOMPLETE",
        "registry_entries_checked": ["MECH-001"],
        "protected_surface": "NO",
        "protected_detection_source": "REGISTRY_PATH_MATCH",
        "protected_registry_entries": [],
        "protected_path_matches": [],
        "evidence_authenticity": "DRIVER_SPOT_CHECKED",
        "evidence_artifacts": [artifact()],
        "spot_check_records": [spot("DRIVER")],
        "waiver_records": [],
        "snapshot_hashes": [snapshot()],
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

def day1_full():
    sm = scout_ok()
    sm.update({
        "report_id": "SM-D1-FULL",
        "requested_change": "day-1 driver-only scout",
        "proposed_level": "LEVEL_1",
        "validated_level": "LEVEL_1",
        "level_validation_source": "DRIVER",
        "level_validation_phase": "VALIDATED_PRE_WORK",
        "protected_surface": "NO",
        "protected_detection_source": "DRIVER_SEMANTIC_REVIEW",
        "need_verdict": "MODIFY_EXISTING",
        "minimal_change_route": "modify existing guardrail docs only",
        "termination_reason": "Driver reviewed Day-1 fallback evidence",
        "next_action": "proceed under Driver-only profile",
    })
    return sm

def seal_ok():
    return {
        "seal_id": "SEAL-1",
        "guardrail_version": GV,
        "scout_map_report": artifact("artifacts/scout/sm1.json"),
        "need_verdict": "BUILD",
        "validated_level": "LEVEL_2",
        "protected_surface": "NO",
        "protected_detection_source": "REGISTRY_PATH_MATCH",
        "evidence_authenticity": "DRIVER_SPOT_CHECKED",
        "snapshot_hashes": [snapshot("x", "SOURCE_FILE")],
        "seal_status": "PASS",
        "registry_update_status": "UPDATED",
        "telemetry_update_source": "SEAL_PACKET_AGGREGATION",
    }

def build_probes():
    probes = []
    doc = base_doc(); doc["scout_map"] = scout_ok(); probes.append(("P0_sanity_wellformed_BUILD", doc, True))

    doc = base_doc(); sm = scout_ok(); sm["level_validation_source"] = "UNVALIDATED"; sm["level_validation_phase"] = "PROPOSED_PRE_WORK"; doc["scout_map"] = sm; probes.append(("P1_NMW01_unvalidated_level_source_on_BUILD", doc, False))

    doc = base_doc(); sm = scout_ok(); sm["protected_detection_source"] = "UNVALIDATED"; doc["scout_map"] = sm; probes.append(("P2_NMW02_selfclaimed_not_protected", doc, False))

    doc = base_doc(); sm = scout_ok(); sm["spot_check_records"] = []; sm["evidence_artifacts"] = []; doc["scout_map"] = sm; probes.append(("P3_spotcheck_claim_without_records", doc, False))

    doc = base_doc(); sp = seal_ok(); sp["registry_update_status"] = "BLOCKED_REGISTRY_DRIFT"; doc["seal_packet"] = sp; probes.append(("P4_PASS_with_blocked_registry_update", doc, False))

    doc = base_doc(); sp = seal_ok(); sp["seal_id"] = "SEAL-2"; sp["seal_status"] = "BLOCKED_GUARDRAIL_VERSION_MISMATCH"; sp["registry_update_status"] = "NOT_REQUIRED"; sp["scout_map_guardrail_version"] = OLD_GV; doc["seal_packet"] = sp; probes.append(("P5_version_mismatch_representable_with_stale_scout_field", doc, True))

    doc = base_doc(); sp = seal_ok(); sp["seal_id"] = "SEAL-3"; sp["need_verdict"] = "MODIFY_EXISTING"; sp["protected_surface"] = "YES"; sp["protected_detection_source"] = "DIFF_CLASSIFIER"; sp["evidence_authenticity"] = "RUNTIME_CAPTURED"; sp["registry_update_status"] = "NOT_REQUIRED"; doc["seal_packet"] = sp; probes.append(("P6_protected_PASS_without_driver_attestation", doc, False))

    doc = base_doc(); sm = scout_ok(); sm["need_verdict"] = "MODIFY_EXISTING"; sm["scout_status"] = "SELF_REPORT_ONLY"; sm["evidence_authenticity"] = "SELF_REPORTED"; sm["evidence_artifacts"] = []; sm["level_validation_source"] = "UNVALIDATED"; sm["level_validation_phase"] = "PROPOSED_PRE_WORK"; sm["protected_detection_source"] = "UNVALIDATED"; sm["spot_check_records"] = []; doc["scout_map"] = sm; probes.append(("P7_modify_existing_full_selfreport", doc, False))

    # Chosen decision: Day-1 is not a reduced schema. It must fill all fields.
    doc = base_doc(); doc["scout_map"] = {
        "report_id": "SM-D1",
        "artifact": artifact("artifacts/scout/d1.json"),
        "guardrail_version": GV,
        "requested_change": "day-1 minimal scout",
        "proposed_level": "LEVEL_1",
        "validated_level": "LEVEL_1",
        "level_validation_source": "DRIVER",
        "level_validation_phase": "VALIDATED_PRE_WORK",
        "registry_status": "REGISTRY_PRESENT_KNOWN_INCOMPLETE",
        "protected_surface": "NO",
        "protected_detection_source": "DRIVER_SEMANTIC_REVIEW",
        "evidence_authenticity": "DRIVER_SPOT_CHECKED",
        "spot_check_records": [spot("DRIVER")],
        "need_verdict": "MODIFY_EXISTING",
        "scout_status": "VALIDATED",
    }; probes.append(("P8a_day1_reduced_fieldset_rejected", doc, False))

    doc = base_doc(); doc["scout_map"] = day1_full(); probes.append(("P8b_day1_full_fieldset_valid", doc, True))

    doc = base_doc(); sp = seal_ok(); sp["seal_id"] = "SEAL-4"; sp["need_verdict"] = "MODIFY_EXISTING"; sp["protected_surface"] = "YES"; sp["protected_detection_source"] = "DIFF_CLASSIFIER"; sp["validated_level"] = "LEVEL_2"; sp["evidence_authenticity"] = "RUNTIME_CAPTURED"; sp["registry_update_status"] = "NOT_REQUIRED"; sp["driver_attestation"] = SIG; doc["seal_packet"] = sp; probes.append(("P9_protected_PASS_with_driver_attestation_valid", doc, True))

    return probes

def main():
    schema_path = sys.argv[1] if len(sys.argv) > 1 else "cap_guardrails.schema.v0.2.1.json"
    with open(schema_path) as f:
        schema = json.load(f)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    gaps = 0
    for name, doc, expect in build_probes():
        errors = list(validator.iter_errors(copy.deepcopy(doc)))
        is_valid = not errors
        matches = is_valid == expect
        status = "OK  " if matches else "GAP "
        if not matches:
            gaps += 1
        print(f"{status}| {name}: want {'VALID' if expect else 'INVALID'}, schema says {'VALID' if is_valid else 'INVALID'}")
        if not matches and errors:
            e = errors[0]
            print(f"      first error @ {e.json_path}: {e.message[:120]}")
    print(f"\n{gaps} gap(s) against v0.2.1 expectations.")
    return 1 if gaps else 0

if __name__ == "__main__":
    sys.exit(main())
