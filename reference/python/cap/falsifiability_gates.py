"""Executable falsifiability gates for CAP claims.

Reads `spec/falsifiability_status.json` and runs each claim marked as
`gate: executable`. Each gate function returns a structured result; the
calling tests assert that no claim is falsified.

Two claims are currently executable:

- Claim 1: Operators are consistently assignable. Gate: three named LLM
  models agree on `overall_verdict` and `primary_reading` for every case in
  the COM Grammar pack, matching the deterministic baseline.
- Claim 7: COM-Log format produces structured output. Gate: the full CAP
  validator accepts a set of known-good COM-Log instances and rejects a set
  of known-bad ones, so the structure is doing discrimination work.

Claims 2-6 remain `gate: deferred` because they require human study or
longitudinal data. The manifest spells out the blocker for each.

Adding a new executable claim: append it to the manifest with
`gate: executable` and define a function named exactly
`gate_function` in this module.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .validator import validate


CAP_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = CAP_ROOT / "spec" / "falsifiability_status.json"


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def claim_1_operator_consistency() -> dict[str, Any]:
    """Three-model agreement on COM Grammar pack.

    For each case in the deterministic baseline, every expected model must
    have produced a model_run JSON whose `llm_reading.overall_verdict` and
    `llm_reading.primary_reading` match the baseline.
    """
    manifest = load_manifest()
    claim = _find_claim(manifest, 1)
    evidence = claim["evidence"]

    runs_dir = CAP_ROOT / evidence["model_runs_dir"]
    baseline_path = CAP_ROOT / evidence["baseline_path"]
    expected_models = evidence["expected_models"]
    fields = evidence["fields_checked"]

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    case_expectations = {
        case["case_id"]: {
            "overall_verdict": case["expected_verdict"],
            "primary_reading": case["expected_primary_reading"],
        }
        for case in baseline["cases"]
    }

    disagreements: list[dict[str, Any]] = []
    missing_runs: list[dict[str, str]] = []
    case_count = len(case_expectations)
    checked_runs = 0

    for case_id, expected in case_expectations.items():
        per_model_readings: dict[str, dict[str, str]] = {}
        for model in expected_models:
            run_path = runs_dir / model / f"{case_id}_{model}.json"
            if not run_path.exists():
                missing_runs.append({"case_id": case_id, "model": model})
                continue
            run = json.loads(run_path.read_text(encoding="utf-8"))
            lr = run.get("llm_reading", {})
            per_model_readings[model] = {f: lr.get(f) for f in fields}
            checked_runs += 1

        # check intra-model and baseline agreement
        for field in fields:
            values = {
                model: per_model_readings.get(model, {}).get(field)
                for model in expected_models
            }
            seen = set(v for v in values.values() if v is not None)
            if len(seen) > 1:
                disagreements.append(
                    {
                        "case_id": case_id,
                        "field": field,
                        "values": values,
                    }
                )
            elif seen and expected.get(field) not in seen:
                disagreements.append(
                    {
                        "case_id": case_id,
                        "field": field,
                        "values": values,
                        "expected": expected.get(field),
                    }
                )

    falsified = bool(disagreements) or bool(missing_runs)
    return {
        "claim_id": 1,
        "falsified": falsified,
        "case_count": case_count,
        "checked_runs": checked_runs,
        "expected_runs": case_count * len(expected_models),
        "disagreements": disagreements,
        "missing_runs": missing_runs,
    }


GOLDEN_COM_LOGS_GOOD: list[dict[str, Any]] = [
    {
        "domain": "Work",
        "node": "Free edits / Boundary",
        "current_status": ["Open", "Leaking"],
        "recommended_operator": {
            "operator": "Fixation",
            "risk_weight_percent": 20,
        },
        "target_status": ["Closed"],
        "next_physical_step": "Send written rule: edits only via new payment",
    },
    {
        "domain": "Body / Health",
        "node": "Sleep / Recovery margin",
        "current_status": ["Active", "Leaking"],
        "recommended_operator": {
            "operator": "Hold",
            "risk_weight_percent": 15,
        },
        "target_status": ["On Hold"],
        "next_physical_step": "Stop all optional commitments before 22:00 for 3 nights",
    },
    {
        "domain": "Finance",
        "node": "Contingency buffer",
        "current_status": ["Open", "Leaking"],
        "recommended_operator": {
            "operator": "Fixation",
            "risk_weight_percent": 18,
        },
        "target_status": ["Fixed"],
        "next_physical_step": "Freeze all optional charity transfers from reserve until buffer is 1 month",
    },
]


GOLDEN_COM_LOGS_BAD: list[dict[str, Any]] = [
    # missing required fields
    {"domain": "Work"},
    # unknown operator
    {
        "domain": "Work",
        "node": "Boundary",
        "current_status": ["Open"],
        "recommended_operator": {
            "operator": "UndoHistory",
            "risk_weight_percent": 20,
        },
        "target_status": ["Closed"],
        "next_physical_step": "test",
    },
    # breach state without recovery gate
    {
        "domain": "Work",
        "node": "Boundary",
        "current_status": ["Open"],
        "recommended_operator": {
            "operator": "Fixation",
            "risk_weight_percent": 20,
        },
        "target_status": ["Closed"],
        "next_physical_step": "test",
        "telemetry_state": "Breach",
        "budget_gate": "Allowed",
    },
    # next_physical_step missing
    {
        "domain": "Work",
        "node": "Boundary",
        "current_status": ["Open"],
        "recommended_operator": {
            "operator": "Fixation",
            "risk_weight_percent": 20,
        },
        "target_status": ["Closed"],
    },
]


def claim_7_com_log_validator_accepts_golden_cases() -> dict[str, Any]:
    """The validator must accept known-good COM-Logs and reject known-bad
    ones. If it stops discriminating, the structural claim is falsified."""
    accepted_good = []
    rejected_good = []
    for instance in GOLDEN_COM_LOGS_GOOD:
        result = validate(instance)
        (accepted_good if result["valid"] else rejected_good).append(
            {"instance": instance, "errors": result.get("errors", [])}
        )

    accepted_bad = []
    rejected_bad = []
    for instance in GOLDEN_COM_LOGS_BAD:
        result = validate(instance)
        (accepted_bad if result["valid"] else rejected_bad).append(
            {"instance": instance, "errors": result.get("errors", [])}
        )

    falsified = bool(rejected_good) or bool(accepted_bad)
    return {
        "claim_id": 7,
        "falsified": falsified,
        "good_count": len(GOLDEN_COM_LOGS_GOOD),
        "good_accepted": len(accepted_good),
        "good_rejected": len(rejected_good),
        "bad_count": len(GOLDEN_COM_LOGS_BAD),
        "bad_accepted": len(accepted_bad),
        "bad_rejected": len(rejected_bad),
        "errors_on_supposedly_good": rejected_good,
        "instances_supposed_to_be_bad_but_accepted": [
            {"instance": item["instance"]} for item in accepted_bad
        ],
    }


def _find_claim(manifest: dict[str, Any], claim_id: int) -> dict[str, Any]:
    for claim in manifest["claims"]:
        if claim["id"] == claim_id:
            return claim
    raise KeyError(f"claim id {claim_id} not in manifest")


def run_all_executable_gates() -> dict[str, Any]:
    """Run every claim whose `gate` is `executable` in the manifest.

    Returns a dict keyed by claim_id. The caller (test_falsifiability_gates)
    is responsible for asserting that no result has `falsified: True`.
    """
    manifest = load_manifest()
    results: dict[int, dict[str, Any]] = {}
    for claim in manifest["claims"]:
        if claim.get("gate") != "executable":
            continue
        fn_name = claim["gate_function"]
        fn = globals().get(fn_name)
        if fn is None:
            raise RuntimeError(
                f"manifest references gate_function {fn_name!r} but it is "
                f"not defined in cap.falsifiability_gates"
            )
        results[claim["id"]] = fn()
    return results
