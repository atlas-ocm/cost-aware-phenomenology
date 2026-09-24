#!/usr/bin/env python3
"""Build a schema-0.2 executed-transition record from a run directory and a record spec.

Usage:

    python build_execution_record.py <repo_root> <run_dir_rel> <spec_json> --out <path>

The record is a transcription of one fixed derivation over files that already
exist. From the run directory it takes the mirror frame and the candidate
transition (their ids), the router receipt (the decision, the closing attempt's
served model and figures, every attempt in order, the router's total wall) and
the verdict receipt (the verifier's wall). From the record spec it takes the
object, the postcondition, the declared checks, the observation and the verdict
reasons. Every reference the record carries is repository-relative, every input
carries the sha256 of the file's bytes, and each check's exit code is read from
the single exit= line of its stored result file.

The record is validated with cap.execution_record.validate_execution_record
against the repository before it is written (base_dir and repo_dir are the
repository root), so a record that merely looks complete is neither written nor
reported as built.

Exit codes: 0 when the record was built, validated and written; 1 with the
validator's problems printed when it returned some; 2, naming the file, when a
required artifact is missing or a stored check result does not hold exactly one
exit= line.
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

EXIT_LINE = re.compile(r"^exit=(-?\d+)$")

# Artifacts the run directory must hold for the derivation to be possible.
RUN_ARTIFACTS = (
    "mirror_frame.json",
    "candidate_transition.json",
    "coding_packet.json",
    "nomcp_coding_receipt.json",
    "nomcp_verdict_receipt.json",
)


def _load_json(path: Path) -> dict:
    """A JSON object read as utf-8 (a BOM is accepted)."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _exit_code(path: Path) -> int | None:
    """The integer of the single exit= line of a stored check result, or None."""
    exit_lines = [
        line
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.startswith("exit=")
    ]
    if len(exit_lines) != 1:
        return None
    match = EXIT_LINE.match(exit_lines[0])
    return int(match.group(1)) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and validate an executed-transition record.",
    )
    parser.add_argument("repo_root", help="Repository root the record is validated against")
    parser.add_argument("run_dir_rel", help="Repository-relative run directory")
    parser.add_argument("spec_json", help="Path to the record spec JSON")
    parser.add_argument("--out", required=True, help="Path the validated record is written to")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    run_dir_rel = str(Path(args.run_dir_rel)).replace("\\", "/").rstrip("/")
    run_dir = repo_root / run_dir_rel

    spec_path = Path(args.spec_json)
    if not spec_path.is_file():
        candidate_spec = repo_root / args.spec_json
        if candidate_spec.is_file():
            spec_path = candidate_spec
    if not spec_path.is_file():
        print(f"missing artifact: {args.spec_json}")
        return 2

    spec = _load_json(spec_path)
    check_specs = [entry for entry in spec.get("checks") or [] if isinstance(entry, dict)]
    input_refs = [str(ref) for ref in spec.get("inputs") or []]

    # -- required artifacts and the stored exit= lines, before anything is built --
    required: list[tuple[str, Path]] = [
        (f"{run_dir_rel}/{name}", run_dir / name) for name in RUN_ARTIFACTS
    ]
    required += [(ref, repo_root / ref) for ref in input_refs]
    required += [
        (str(entry.get("result_ref")), repo_root / str(entry.get("result_ref")))
        for entry in check_specs
    ]

    missing = [ref for ref, path in required if not path.is_file()]
    exit_codes: dict[int, int | None] = {}
    for index, entry in enumerate(check_specs):
        path = repo_root / str(entry.get("result_ref"))
        if path.is_file():
            exit_codes[index] = _exit_code(path)
    malformed = [
        str(entry.get("result_ref"))
        for index, entry in enumerate(check_specs)
        if index in exit_codes and exit_codes[index] is None
    ]

    if missing or malformed:
        for ref in missing:
            print(f"missing artifact: {ref}")
        for ref in malformed:
            print(f"no single exit= line: {ref}")
        return 2

    mirror_frame = _load_json(run_dir / "mirror_frame.json")
    candidate_transition = _load_json(run_dir / "candidate_transition.json")
    receipt = _load_json(run_dir / "nomcp_coding_receipt.json")
    verdict_receipt = _load_json(run_dir / "nomcp_verdict_receipt.json")

    # The route is the whole receipt: every attempt in order, set-aside ones
    # included; the closing attempt is the last one.
    fallback_used = receipt.get("fallback_used") is True
    attempt_names = ["first_attempt"] + (["fallback_attempt"] if fallback_used else [])
    closing = receipt.get(attempt_names[-1]) or {}

    route_attempts = []
    for name in attempt_names:
        attempt = receipt.get(name) or {}
        route_attempts.append(
            {
                "role": "fallback_coder" if name == "fallback_attempt" else "cheap_coder",
                "model_served": attempt.get("model_served"),
                "turns": attempt.get("turns"),
                "output_tokens": attempt.get("output_tokens"),
                "wall_s": attempt.get("wall_s"),
            }
        )

    criteria = {
        entry.get("id"): entry
        for entry in spec.get("criteria") or []
        if isinstance(entry, dict)
    }
    checks = []
    for index, entry in enumerate(check_specs):
        criterion_id = entry.get("criterion_id")
        criterion = criteria.get(criterion_id) or {}
        exit_code = exit_codes[index]
        checks.append(
            {
                "criterion_id": criterion_id,
                "command": criterion.get("check_command"),
                "exit_code": exit_code,
                "status": "pass" if exit_code == 0 else "fail",
                "result_ref": str(entry.get("result_ref")),
                "revision_checked": spec.get("revision_after"),
            }
        )

    verifier_wall_s = verdict_receipt.get("wall_s")
    if isinstance(verifier_wall_s, (int, float)) and not isinstance(verifier_wall_s, bool):
        verifier_wall_s = round(verifier_wall_s, 1)

    record = {
        "schema_version": "0.2",
        "record_id": spec.get("record_id"),
        "object": {
            "kind": "repo",
            "identifier": spec.get("object_identifier"),
            "revision_before": spec.get("revision_before"),
            "revision_after": spec.get("revision_after"),
        },
        "candidate": {
            "candidate_id": (candidate_transition.get("candidate") or {}).get("id"),
            "candidate_ref": f"{run_dir_rel}/candidate_transition.json",
            "mirror_frame_before_id": (mirror_frame.get("frame") or {}).get("id"),
            "mirror_frame_before_ref": f"{run_dir_rel}/mirror_frame.json",
        },
        "postcondition": {
            "defined_before_execution": True,
            "criteria": spec.get("criteria"),
        },
        "execution": {
            "actor": {
                "role": "fallback_coder" if fallback_used else "cheap_coder",
                "model_requested": closing.get("model_requested"),
                "model_served": closing.get("model_served"),
                "identity_source": "claude_cli_modelUsage",
                "identity_independently_verified": False,
            },
            "tool": spec.get("tool"),
            "inputs": [
                {"ref": ref, "sha256": _sha256(repo_root / ref)} for ref in input_refs
            ],
            "receipt_ref": f"{run_dir_rel}/nomcp_coding_receipt.json",
            "decision": receipt.get("decision"),
            "attempts": len(attempt_names),
        },
        "observation_after": {
            "observed_at": spec.get("observed_after_at"),
            "revision_after": spec.get("revision_after"),
            "summary": spec.get("observation_summary"),
        },
        "checks": checks,
        "expected_evidence_results": spec.get("expected_evidence_results"),
        "divergence": {
            "expected_vs_observed": spec.get("divergence"),
            "adjustment_ref": spec.get("adjustment_ref"),
        },
        "costs": {
            "estimated_ref": f"{run_dir_rel}/candidate_transition.json",
            "measured": {
                "worker_output_tokens": closing.get("output_tokens"),
                "worker_turns": closing.get("turns"),
                "worker_wall_s": closing.get("wall_s"),
                "verifier_wall_s": verifier_wall_s,
                "money": "unknown",
            },
            "route": {
                "attempts": route_attempts,
                "turns_total": sum(attempt["turns"] for attempt in route_attempts),
                "output_tokens_total": sum(
                    attempt["output_tokens"] for attempt in route_attempts
                ),
                "router_wall_s": receipt.get("total_wall_s"),
            },
        },
        "verdict": {
            "postcondition_met": all(check["status"] == "pass" for check in checks),
            "provenance_established": True,
            "reasons": spec.get("verdict_reasons"),
        },
        "notes": spec.get("notes"),
    }

    problems = validate_execution_record(record, repo_root, repo_root)
    if problems:
        for problem in problems:
            print(problem)
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
