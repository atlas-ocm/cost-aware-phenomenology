#!/usr/bin/env python3
"""Build a schema-0.2 executed-transition record from a recorded run directory.

Usage:

    python build_execution_record.py <repo_root> <run_dir_rel> <spec_json> --out <path>

The record spec (record_spec.json) fixes the identity of the transition; the
run directory supplies the artifacts the record points at: the mirror frame,
the candidate, the coding packet and the router/verdict receipts, and the
stored check results. Every figure is read from those artifacts -- nothing
about the observed run is hardcoded. The route and closing-attempt costs come
from the router receipt: costs.route carries every attempt the receipt records
(set-aside ones included), and costs.measured is the closing attempt's.

The built record is validated with cap.execution_record.validate_execution_record
against the repository before it is written. Exit codes:

    0  the record was built, validated with no problem, and written to --out;
    1  the validator returned problems (printed one per line);
    2  a stored check result does not hold exactly one exit= line, or a
       required artifact is missing; the file is named on the line printed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# Make cap importable when running as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cap.execution_record import validate_execution_record  # noqa: E402

EXIT_LINE = re.compile(r"^exit=(-?\d+)$")
ATTEMPT_ROLES = {"first_attempt": "cheap_coder", "fallback_attempt": "fallback_coder"}


def _load_json(path: Path) -> dict:
    """Load a JSON object; read as utf-8-sig so a BOM is tolerated."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _attempt_order(receipt: dict) -> list[str]:
    """The receipt's attempts in order: first_attempt, plus fallback_attempt when used."""
    names = ["first_attempt"]
    if receipt.get("fallback_used") is True:
        names.append("fallback_attempt")
    return names


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build an executed-transition record from a run directory.",
    )
    parser.add_argument("repo_root", help="Repository root the record's refs are relative to")
    parser.add_argument("run_dir_rel", help="Run directory, repository-relative")
    parser.add_argument("spec_json", help="Record spec, repository-relative")
    parser.add_argument("--out", required=True, help="Path to write the built record to")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    run_dir_rel = args.run_dir_rel.replace("\\", "/").strip("/")
    run_dir = repo_root / run_dir_rel

    if not (repo_root / args.spec_json).is_file():
        print(f"{args.spec_json}: required artifact missing")
        return 2
    spec = _load_json(repo_root / args.spec_json)

    # Stored check results must hold exactly one exit= line each. This runs
    # before any artifact is hashed so a malformed result is named, not read.
    criteria_by_id = {criterion["id"]: criterion for criterion in spec["criteria"]}
    exit_codes: dict[str, int] = {}
    for item in spec["checks"]:
        result_ref = item["result_ref"]
        result_path = repo_root / result_ref
        if not result_path.is_file():
            print(f"{result_ref}: required artifact missing")
            return 2
        lines = result_path.read_text(encoding="utf-8-sig").splitlines()
        matches = [m for m in (EXIT_LINE.match(line) for line in lines) if m]
        if len(matches) != 1:
            print(f"{result_ref}: no single exit= line")
            return 2
        exit_codes[item["criterion_id"]] = int(matches[0].group(1))

    # The run's carriers and every hashed input must exist.
    required = [
        f"{run_dir_rel}/mirror_frame.json",
        f"{run_dir_rel}/candidate_transition.json",
        f"{run_dir_rel}/coding_packet.json",
        f"{run_dir_rel}/nomcp_coding_receipt.json",
        f"{run_dir_rel}/nomcp_verdict_receipt.json",
        *spec["inputs"],
    ]
    for ref in required:
        if not (repo_root / ref).is_file():
            print(f"{ref}: required artifact missing")
            return 2

    candidate_transition = _load_json(run_dir / "candidate_transition.json")
    mirror_frame = _load_json(run_dir / "mirror_frame.json")
    receipt = _load_json(run_dir / "nomcp_coding_receipt.json")
    verdict_receipt = _load_json(run_dir / "nomcp_verdict_receipt.json")

    attempt_names = _attempt_order(receipt)
    closing_name = attempt_names[-1]
    closing = receipt[closing_name]
    verifier_wall = verdict_receipt.get("wall_s")

    checks = [
        {
            "criterion_id": item["criterion_id"],
            "command": criteria_by_id[item["criterion_id"]]["check_command"],
            "exit_code": exit_codes[item["criterion_id"]],
            "status": "pass" if exit_codes[item["criterion_id"]] == 0 else "fail",
            "result_ref": item["result_ref"],
            "revision_checked": spec["revision_after"],
        }
        for item in spec["checks"]
    ]

    route_attempts = [
        {
            "role": ATTEMPT_ROLES[name],
            "model_served": receipt[name]["model_served"],
            "turns": receipt[name]["turns"],
            "output_tokens": receipt[name]["output_tokens"],
            "wall_s": receipt[name]["wall_s"],
        }
        for name in attempt_names
    ]

    record = {
        "schema_version": "0.2",
        "record_id": spec["record_id"],
        "object": {
            "kind": "repo",
            "identifier": spec["object_identifier"],
            "revision_before": spec["revision_before"],
            "revision_after": spec["revision_after"],
        },
        "candidate": {
            "candidate_id": candidate_transition["candidate"]["id"],
            "candidate_ref": f"{run_dir_rel}/candidate_transition.json",
            "mirror_frame_before_id": mirror_frame["frame"]["id"],
            "mirror_frame_before_ref": f"{run_dir_rel}/mirror_frame.json",
        },
        "postcondition": {
            "defined_before_execution": True,
            "criteria": spec["criteria"],
        },
        "execution": {
            "actor": {
                "role": ATTEMPT_ROLES[closing_name],
                "model_requested": closing["model_requested"],
                "model_served": closing["model_served"],
                "identity_source": "claude_cli_modelUsage",
                "identity_independently_verified": False,
            },
            "tool": spec["tool"],
            "inputs": [
                {"ref": ref, "sha256": _sha256(repo_root / ref)} for ref in spec["inputs"]
            ],
            "receipt_ref": f"{run_dir_rel}/nomcp_coding_receipt.json",
            "decision": receipt["decision"],
            "attempts": len(attempt_names),
        },
        "observation_after": {
            "observed_at": spec["observed_after_at"],
            "revision_after": spec["revision_after"],
            "summary": spec["observation_summary"],
        },
        "checks": checks,
        "expected_evidence_results": spec["expected_evidence_results"],
        "divergence": {
            "expected_vs_observed": spec["divergence"],
            "adjustment_ref": spec["adjustment_ref"],
        },
        "costs": {
            "estimated_ref": f"{run_dir_rel}/candidate_transition.json",
            "measured": {
                "worker_output_tokens": closing["output_tokens"],
                "worker_turns": closing["turns"],
                "worker_wall_s": closing["wall_s"],
                "verifier_wall_s": (
                    round(verifier_wall, 1)
                    if isinstance(verifier_wall, (int, float))
                    else None
                ),
                "money": "unknown",
            },
            "route": {
                "attempts": route_attempts,
                "turns_total": sum(attempt["turns"] for attempt in route_attempts),
                "output_tokens_total": sum(
                    attempt["output_tokens"] for attempt in route_attempts
                ),
                "router_wall_s": receipt["total_wall_s"],
            },
        },
        "verdict": {
            "postcondition_met": all(check["exit_code"] == 0 for check in checks),
            "provenance_established": True,
            "reasons": spec["verdict_reasons"],
        },
        "notes": spec["notes"],
    }

    problems = validate_execution_record(record, repo_root, repo_root)
    if problems:
        for problem in problems:
            print(problem)
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
