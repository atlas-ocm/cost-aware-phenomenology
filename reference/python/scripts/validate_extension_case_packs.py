#!/usr/bin/env python3
"""Validate Looking-Glass and Latent Cause Reconstruction case packs against
their CAP schemas.

Exists so that `check_repo.ps1` can exercise schema-as-contract on every
existing case in both extension packs, not only via pytest collection.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

CAP_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = CAP_ROOT.parent

LOOKING_GLASS_SCHEMA = CAP_ROOT / "spec" / "looking_glass.schema.json"
LATENT_CAUSE_SCHEMA = CAP_ROOT / "spec" / "latent_cause_reconstruction.schema.json"
RELEASE_GATE_SCHEMA = CAP_ROOT / "spec" / "release_gate.schema.json"
RELEASE_GATE_EXAMPLE = CAP_ROOT / "examples" / "release_gate_result_example.json"

MIRROR_LAYER_SCHEMA = CAP_ROOT / "spec" / "mirror_layer.schema.json"
MIRROR_LAYER_EXAMPLE = CAP_ROOT / "examples" / "mirror_frame_example.json"

LOOKING_GLASS_TRACE_SCHEMA = CAP_ROOT / "spec" / "looking_glass_trace.schema.json"
LOOKING_GLASS_TRACE_EXAMPLE = CAP_ROOT / "examples" / "looking_glass_trace_example.json"

CONTEXT_HYGIENE_SCHEMA = CAP_ROOT / "spec" / "context_hygiene.schema.json"
CONTEXT_HYGIENE_EXAMPLE = CAP_ROOT / "examples" / "context_hygiene_result_example.json"

DSSD_SCHEMA = CAP_ROOT / "spec" / "dynamic_subject_state_detection.schema.json"
DSSD_EXAMPLE = CAP_ROOT / "examples" / "subject_state_frame_example.json"

ADJUSTMENT_LAYER_SCHEMA = CAP_ROOT / "spec" / "adjustment_layer.schema.json"
ADJUSTMENT_LAYER_EXAMPLE = CAP_ROOT / "examples" / "adjustment_candidate_transition_example.json"

ROLE_ORCHESTRATION_SCHEMA = CAP_ROOT / "spec" / "role_orchestration.schema.json"
ROLE_ORCHESTRATION_EXAMPLE = CAP_ROOT / "examples" / "role_orchestration_decision_example.json"

CYCLE_STATE_MACHINE_SCHEMA = CAP_ROOT / "spec" / "cycle_state_machine.schema.json"
CYCLE_STATE_MACHINE_EXAMPLE = CAP_ROOT / "examples" / "cycle_node_example.json"

ANCHOR_DECAY_SCHEMA = CAP_ROOT / "spec" / "anchor_decay.schema.json"
ANCHOR_DECAY_EXAMPLE = CAP_ROOT / "examples" / "anchor_decay_example.json"

WITNESS_INDEPENDENCE_SCHEMA = CAP_ROOT / "spec" / "witness_independence.schema.json"
WITNESS_INDEPENDENCE_EXAMPLE = CAP_ROOT / "examples" / "witness_pair_example.json"

CROSS_DOMAIN_DRAIN_SCHEMA = CAP_ROOT / "spec" / "cross_domain_drain.schema.json"
CROSS_DOMAIN_DRAIN_EXAMPLE = CAP_ROOT / "examples" / "cross_domain_drain_event_example.json"

OBSERVABILITY_SCHEMA = CAP_ROOT / "spec" / "observability_protocol.schema.json"
OBSERVABILITY_EXAMPLE = CAP_ROOT / "examples" / "observability_event_example.json"

ANTI_DRAMA_SCHEMA = CAP_ROOT / "spec" / "anti_drama_detection.schema.json"
ANTI_DRAMA_EXAMPLE = CAP_ROOT / "examples" / "anti_drama_event_example.json"

CAP_GUARDRAILS_SCHEMA = CAP_ROOT / "spec" / "cap_guardrails.schema.json"
CAP_GUARDRAILS_EXAMPLE = CAP_ROOT / "examples" / "cap_guardrails_decision_example.json"

LOOKING_GLASS_PACKS = [
    REPO_ROOT / "Patch" / "adjoint_looking_glass_layer_cases",
    REPO_ROOT / "Patch" / "adjoint_looking_glass_layer_holdout_cases",
]
LATENT_CAUSE_PACKS = [
    REPO_ROOT / "Patch" / "latent_cause_reconstruction_cases",
]


def _validate_pack(schema_path: Path, packs: list[Path], glob_pattern: str) -> int:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)

    total = 0
    failures = 0
    for pack in packs:
        if not pack.exists():
            print(f"  [warn] pack missing: {pack}")
            continue
        case_files = sorted(pack.glob(glob_pattern))
        for case_file in case_files:
            total += 1
            case = json.loads(case_file.read_text(encoding="utf-8-sig"))
            errors = sorted(
                validator.iter_errors(case), key=lambda e: list(e.path)
            )
            if errors:
                failures += 1
                print(f"  FAIL {case_file.relative_to(REPO_ROOT)}")
                for err in errors:
                    location = "/".join(str(p) for p in err.path) or "<root>"
                    print(f"    - {location}: {err.message}")
    return total, failures


def _validate_single_example(schema_path: Path, example_path: Path) -> int:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    instance = json.loads(example_path.read_text(encoding="utf-8-sig"))
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(instance),
        key=lambda e: list(e.path),
    )
    if errors:
        print(f"  FAIL {example_path.relative_to(REPO_ROOT)}")
        for err in errors:
            location = "/".join(str(p) for p in err.path) or "<root>"
            print(f"    - {location}: {err.message}")
        return 1
    return 0


def main() -> int:
    print(f"Validating Looking-Glass case pack against {LOOKING_GLASS_SCHEMA.name} ...")
    lg_total, lg_failures = _validate_pack(LOOKING_GLASS_SCHEMA, LOOKING_GLASS_PACKS, "alg_*.json")
    print(f"  {lg_total - lg_failures}/{lg_total} passed")

    print(f"Validating Latent Cause case pack against {LATENT_CAUSE_SCHEMA.name} ...")
    lc_total, lc_failures = _validate_pack(LATENT_CAUSE_SCHEMA, LATENT_CAUSE_PACKS, "lcr_*.json")
    print(f"  {lc_total - lc_failures}/{lc_total} passed")

    print(f"Validating Release Gate example against {RELEASE_GATE_SCHEMA.name} ...")
    rg_failures = _validate_single_example(RELEASE_GATE_SCHEMA, RELEASE_GATE_EXAMPLE)
    if rg_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Mirror Layer example against {MIRROR_LAYER_SCHEMA.name} ...")
    ml_failures = _validate_single_example(MIRROR_LAYER_SCHEMA, MIRROR_LAYER_EXAMPLE)
    if ml_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Looking-Glass trace example against {LOOKING_GLASS_TRACE_SCHEMA.name} ...")
    lgt_failures = _validate_single_example(LOOKING_GLASS_TRACE_SCHEMA, LOOKING_GLASS_TRACE_EXAMPLE)
    if lgt_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Context Hygiene example against {CONTEXT_HYGIENE_SCHEMA.name} ...")
    ch_failures = _validate_single_example(CONTEXT_HYGIENE_SCHEMA, CONTEXT_HYGIENE_EXAMPLE)
    if ch_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Dynamic Subject-State Detection example against {DSSD_SCHEMA.name} ...")
    dssd_failures = _validate_single_example(DSSD_SCHEMA, DSSD_EXAMPLE)
    if dssd_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Adjustment Layer example against {ADJUSTMENT_LAYER_SCHEMA.name} ...")
    adj_failures = _validate_single_example(ADJUSTMENT_LAYER_SCHEMA, ADJUSTMENT_LAYER_EXAMPLE)
    if adj_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Role Orchestration example against {ROLE_ORCHESTRATION_SCHEMA.name} ...")
    ro_failures = _validate_single_example(ROLE_ORCHESTRATION_SCHEMA, ROLE_ORCHESTRATION_EXAMPLE)
    if ro_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Cycle State Machine example against {CYCLE_STATE_MACHINE_SCHEMA.name} ...")
    csm_failures = _validate_single_example(CYCLE_STATE_MACHINE_SCHEMA, CYCLE_STATE_MACHINE_EXAMPLE)
    if csm_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Anchor Decay example against {ANCHOR_DECAY_SCHEMA.name} ...")
    ad_failures = _validate_single_example(ANCHOR_DECAY_SCHEMA, ANCHOR_DECAY_EXAMPLE)
    if ad_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Witness Independence example against {WITNESS_INDEPENDENCE_SCHEMA.name} ...")
    wi_failures = _validate_single_example(WITNESS_INDEPENDENCE_SCHEMA, WITNESS_INDEPENDENCE_EXAMPLE)
    if wi_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Cross-Domain Drain example against {CROSS_DOMAIN_DRAIN_SCHEMA.name} ...")
    cdd_failures = _validate_single_example(CROSS_DOMAIN_DRAIN_SCHEMA, CROSS_DOMAIN_DRAIN_EXAMPLE)
    if cdd_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Observability Protocol example against {OBSERVABILITY_SCHEMA.name} ...")
    obs_failures = _validate_single_example(OBSERVABILITY_SCHEMA, OBSERVABILITY_EXAMPLE)
    if obs_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating Anti-drama Detection example against {ANTI_DRAMA_SCHEMA.name} ...")
    anti_drama_failures = _validate_single_example(ANTI_DRAMA_SCHEMA, ANTI_DRAMA_EXAMPLE)
    if anti_drama_failures == 0:
        print(f"  1/1 passed")

    print(f"Validating CAP-Guardrails example against {CAP_GUARDRAILS_SCHEMA.name} ...")
    cgr_failures = _validate_single_example(CAP_GUARDRAILS_SCHEMA, CAP_GUARDRAILS_EXAMPLE)
    if cgr_failures == 0:
        print(f"  1/1 passed")

    total_failures = lg_failures + lc_failures + rg_failures + ml_failures + lgt_failures + ch_failures + dssd_failures + adj_failures + ro_failures + csm_failures + ad_failures + wi_failures + cdd_failures + obs_failures + anti_drama_failures + cgr_failures
    if total_failures:
        print(f"Extension case-pack validation FAILED ({total_failures} cases).")
        return 1
    print("Extension case-pack validation OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
