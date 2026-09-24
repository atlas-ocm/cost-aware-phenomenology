#!/usr/bin/env python3
"""Build a schema-0.2 executed-transition record from a recorded run directory.

Usage:

    python build_execution_record.py <repo_root> <run_dir_rel> <spec_json> --out <path>

The record is derived from the run directory's stored artifacts (its Mirror
Frame, the candidate transition, the router coding receipt, the verifier
verdict receipt and the stored check results) and the record spec the driver
used. The built record is validated against <repo_root> by
cap.execution_record.validate_execution_record.

Exit 0 means the record was built and the validator returned no problem; 1
means the validator returned problems (printed one per line); 2 means a stored
check result did not hold exactly one exit= line, or a required artifact is
missing (the file is named).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# Make cap module importable when running as script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cap.execution_record import validate_execution_record  # noqa: E402

RUN_FILES = (
    "mirror_frame.json",
    "candidate_transition.json",
    "nomcp_coding_receipt.json",
    "nomcp_verdict_receipt.json",
)
EXIT_RE = re.compile(r"^exit=(-?\d+)$")


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _report_and_exit(ref: str, reason: str) -> int:
    """Name the file and return the exit code for an unusable artifact."""
    print(f"{ref}: {reason}")
    return 2


def _read_exit_code(path: Path):
    """The integer of the single exit= line, or None when there is not exactly one."""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    exit_lines = [line for line in lines if line.startswith("exit=")]
    if len(exit_lines) != 1:
        return None
    match = EXIT_RE.match(exit_lines[0])
    if not match:
        return None
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build an executed-transition record from a run directory.",
    )
    parser.add_argument("repo_root", help="Repository root the record is validated against")
    parser.add_argument("run_dir_rel", help="Run directory, relative to the repository root")
    parser.add_argument("spec_json", help="Record spec the driver used")
    parser.add_argument("--out", required=True, help="Path the built record is written to")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    run_dir_rel = args.run_dir_rel
    run_dir = repo_root / run_dir_rel

    spec_arg = Path(args.spec_json)
    if spec_arg.is_absolute():
        spec_path = spec_arg
    else:
        spec_path = repo_root / spec_arg
        if not spec_path.is_file():
            spec_path = Path.cwd() / spec_arg
    if not spec_path.is_file():
        return _report_and_exit(str(spec_arg), "record spec not found")
    try:
        spec = _load_json(spec_path)
    except (OSError, ValueError) as exc:
        return _report_and_exit(str(spec_path), f"cannot read record spec: {exc}")

    # required run-directory artifacts
    for name in RUN_FILES:
        if not (run_dir / name).is_file():
            return _report_and_exit(f"{run_dir_rel}/{name}", "required artifact not found")

    candidate_transition = _load_json(run_dir / "candidate_transition.json")
    mirror_frame = _load_json(run_dir / "mirror_frame.json")
    receipt = _load_json(run_dir / "nomcp_coding_receipt.json")
    verdict_receipt = _load_json(run_dir / "nomcp_verdict_receipt.json")

    # checks: every stored result must hold exactly one exit= line
    criteria_map = {c.get("id"): c.get("check_command") for c in spec["criteria"]}
    checks = []
    for item in spec["checks"]:
        ref = item["result_ref"]
        target = repo_root / ref
        if not target.is_file():
            return _report_and_exit(ref, "required artifact not found")
        exit_code = _read_exit_code(target)
        if exit_code is None:
            return _report_and_exit(ref, "no single exit= line")
        checks.append(
            {
                "criterion_id": item["criterion_id"],
                "command": criteria_map.get(item["criterion_id"]),
                "exit_code": exit_code,
                "status": "pass" if exit_code == 0 else "fail",
                "result_ref": ref,
                "revision_checked": spec["revision_after"],
            }
        )

    # hashed inputs: the sha256 of each named file's bytes
    inputs = []
    for ref in spec["inputs"]:
        target = repo_root / ref
        if not target.is_file():
            return _report_and_exit(ref, "required artifact not found")
        inputs.append(
            {"ref": ref, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
        )

    fallback_used = receipt.get("fallback_used") is True
    attempt_names = ["first_attempt"] + (["fallback_attempt"] if fallback_used else [])
    closing = receipt["fallback_attempt"] if fallback_used else receipt["first_attempt"]

    route_attempts = []
    for name in attempt_names:
        attempt = receipt[name]
        route_attempts.append(
            {
                "role": "fallback_coder" if name == "fallback_attempt" else "cheap_coder",
                "model_served": attempt.get("model_served"),
                "turns": attempt.get("turns"),
                "output_tokens": attempt.get("output_tokens"),
                "wall_s": attempt.get("wall_s"),
            }
        )

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
                "role": "fallback_coder" if fallback_used else "cheap_coder",
                "model_requested": closing.get("model_requested"),
                "model_served": closing.get("model_served"),
                "identity_source": "claude_cli_modelUsage",
                "identity_independently_verified": False,
            },
            "tool": spec["tool"],
            "inputs": inputs,
            "receipt_ref": f"{run_dir_rel}/nomcp_coding_receipt.json",
            "decision": receipt.get("decision"),
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
                "worker_output_tokens": closing.get("output_tokens"),
                "worker_turns": closing.get("turns"),
                "worker_wall_s": closing.get("wall_s"),
                "verifier_wall_s": round(verdict_receipt.get("wall_s"), 1),
                "money": "unknown",
            },
            "route": {
                "attempts": route_attempts,
                "turns_total": sum(a["turns"] for a in route_attempts),
                "output_tokens_total": sum(a["output_tokens"] for a in route_attempts),
                "router_wall_s": receipt.get("total_wall_s"),
            },
        },
        "verdict": {
            "postcondition_met": all(c["status"] == "pass" for c in checks),
            "provenance_established": True,
            "reasons": spec["verdict_reasons"],
        },
        "notes": spec["notes"],
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    problems = validate_execution_record(record, repo_root, repo_root)
    if problems:
        for problem in problems:
            print(problem)
        return 1
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
