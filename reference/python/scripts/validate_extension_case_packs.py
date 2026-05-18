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

    total_failures = lg_failures + lc_failures + rg_failures + ml_failures + lgt_failures
    if total_failures:
        print(f"Extension case-pack validation FAILED ({total_failures} cases).")
        return 1
    print("Extension case-pack validation OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
