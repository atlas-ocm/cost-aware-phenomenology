#!/usr/bin/env python3
"""Build a schema-0.2 executed-transition record from a recorded run.

Usage:

    python build_execution_record.py <repo_root> <run_dir_rel> <spec_json> --out <path>

The run directory holds the carriers a record is built from: mirror_frame.json,
candidate_transition.json, nomcp_coding_receipt.json, nomcp_verdict_receipt.json
and the checks/*.txt results named by the record spec. The spec supplies the
identity of the transition (record id, object identifier, revisions, tool,
inputs, criteria, checks, observation, evidence, divergence, reasons, notes);
everything else is derived from the carriers: the candidate and mirror-frame ids
from their files, the actor from the receipt's closing attempt, each input's
sha256 from the file bytes, each check's exit_code from the single exit= line of
its result file, and the costs from the receipt (the whole route) and the verdict
receipt (verifier wall). The record is validated against <repo_root> before it is
written.

Exit codes: 0 when the record was built, validated with no problem and written;
1 with the problems printed when the validator returned some; 2, naming the
file, when a stored check result does not hold exactly one exit= line or a
required artifact is missing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Make cap module importable when running as script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cap.execution_record import validate_execution_record  # noqa: E402


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _exit_code_of(path: Path) -> int:
    """The integer of the single exit= line of a stored check result."""
    lines = path.read_text(encoding="utf-8").splitlines()
    exit_lines = [line for line in lines if line.startswith("exit=")]
    if len(exit_lines) != 1:
        raise ValueError(f"{path}: check result does not hold exactly one exit= line")
    value = exit_lines[0][len("exit="):].strip()
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{path}: check result does not hold exactly one exit= line")


def _fail(path: Path, reason: str) -> int:
    print(f"{path}: {reason}")
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a schema-0.2 executed-transition record from a run directory and a spec.",
    )
    parser.add_argument("repo_root", help="Repository root the refs resolve against")
    parser.add_argument("run_dir", help="Run directory, relative to repo_root")
    parser.add_argument("spec", help="Record spec JSON, relative to repo_root")
    parser.add_argument("--out", required=True, help="Path to write the built record JSON")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    run_dir_rel = args.run_dir.replace("\\", "/").strip("/")

    def run_ref(name: str) -> str:
        return f"{run_dir_rel}/{name}" if run_dir_rel else name

    def run_path(name: str) -> Path:
        return repo_root / run_dir_rel / name

    # -- the spec and the run's carriers must be present before anything is built
    spec_path = repo_root / args.spec
    if not spec_path.is_file():
        return _fail(spec_path, "required artifact is missing")
    try:
        spec = _load_json(spec_path)
    except (OSError, ValueError) as exc:
        return _fail(spec_path, f"required artifact cannot be read: {exc}")

    carriers: dict[str, dict] = {}
    for name in ("mirror_frame.json", "candidate_transition.json",
                 "nomcp_coding_receipt.json", "nomcp_verdict_receipt.json"):
        path = run_path(name)
        if not path.is_file():
            return _fail(path, "required artifact is missing")
        try:
            carriers[name] = _load_json(path)
        except (OSError, ValueError) as exc:
            return _fail(path, f"required artifact cannot be read: {exc}")

    # A stored check result without exactly one exit= line is a malformed input:
    # exit 2 naming the file, before any hashing or building.
    exit_codes: dict[str, int] = {}
    for entry in spec["checks"]:
        ref = entry["result_ref"]
        path = repo_root / ref
        if not path.is_file():
            return _fail(path, "required artifact is missing")
        try:
            exit_codes[ref] = _exit_code_of(path)
        except (OSError, ValueError):
            return _fail(path, "check result does not hold exactly one exit= line")

    # -- hashed inputs: the refs are repo-relative, the hash is of the file bytes
    inputs = []
    for ref in spec["inputs"]:
        path = repo_root / ref
        if not path.is_file():
            return _fail(path, "required artifact is missing")
        inputs.append({"ref": ref, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

    # -- derived carriers
    mirror_frame = carriers["mirror_frame.json"]
    candidate_doc = carriers["candidate_transition.json"]
    receipt = carriers["nomcp_coding_receipt.json"]
    verdict_receipt = carriers["nomcp_verdict_receipt.json"]

    fallback_used = bool(receipt.get("fallback_used"))
    closing_name = "fallback_attempt" if fallback_used else "first_attempt"
    closing = receipt.get(closing_name)
    if not isinstance(closing, dict):
        return _fail(run_path("nomcp_coding_receipt.json"), f"receipt lacks {closing_name}")

    first = receipt.get("first_attempt")
    if not isinstance(first, dict):
        return _fail(run_path("nomcp_coding_receipt.json"), "receipt lacks first_attempt")

    route_attempts = [
        {
            "role": "cheap_coder",
            "model_served": first["model_served"],
            "turns": first["turns"],
            "output_tokens": first["output_tokens"],
            "wall_s": first["wall_s"],
        }
    ]
    if fallback_used:
        fallback = receipt.get("fallback_attempt")
        if not isinstance(fallback, dict):
            return _fail(run_path("nomcp_coding_receipt.json"), "receipt lacks fallback_attempt")
        route_attempts.append(
            {
                "role": "fallback_coder",
                "model_served": fallback["model_served"],
                "turns": fallback["turns"],
                "output_tokens": fallback["output_tokens"],
                "wall_s": fallback["wall_s"],
            }
        )

    criteria = spec["criteria"]
    criteria_by_id = {criterion["id"]: criterion for criterion in criteria}

    checks = []
    for entry in spec["checks"]:
        criterion_id = entry["criterion_id"]
        ref = entry["result_ref"]
        exit_code = exit_codes[ref]
        checks.append(
            {
                "criterion_id": criterion_id,
                "command": criteria_by_id[criterion_id]["check_command"],
                "exit_code": exit_code,
                "status": "pass" if exit_code == 0 else "fail",
                "result_ref": ref,
                "revision_checked": spec["revision_after"],
            }
        )

    candidate_ref = run_ref("candidate_transition.json")

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
            "candidate_id": candidate_doc["candidate"]["id"],
            "candidate_ref": candidate_ref,
            "mirror_frame_before_id": mirror_frame["frame"]["id"],
            "mirror_frame_before_ref": run_ref("mirror_frame.json"),
        },
        "postcondition": {
            "defined_before_execution": True,
            "criteria": criteria,
        },
        "execution": {
            "actor": {
                "role": "fallback_coder" if fallback_used else "cheap_coder",
                "model_requested": closing["model_requested"],
                "model_served": closing["model_served"],
                "identity_source": "claude_cli_modelUsage",
                "identity_independently_verified": False,
            },
            "tool": spec["tool"],
            "inputs": inputs,
            "receipt_ref": run_ref("nomcp_coding_receipt.json"),
            "decision": receipt["decision"],
            "attempts": len(route_attempts),
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
            "estimated_ref": candidate_ref,
            "measured": {
                "worker_output_tokens": closing["output_tokens"],
                "worker_turns": closing["turns"],
                "worker_wall_s": closing["wall_s"],
                "verifier_wall_s": round(verdict_receipt["wall_s"], 1),
                "money": "unknown",
            },
            "route": {
                "attempts": route_attempts,
                "turns_total": sum(attempt["turns"] for attempt in route_attempts),
                "output_tokens_total": sum(attempt["output_tokens"] for attempt in route_attempts),
                "router_wall_s": receipt["total_wall_s"],
            },
        },
        "verdict": {
            "postcondition_met": all(check["status"] == "pass" for check in checks),
            "provenance_established": True,
            "reasons": spec["verdict_reasons"],
        },
        "notes": spec["notes"],
    }

    problems = validate_execution_record(record, base_dir=repo_root, repo_dir=repo_root)
    if problems:
        for problem in problems:
            print(problem)
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
