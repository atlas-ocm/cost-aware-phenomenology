"""Whole-route costs of every recorded run, read from the verbatim NoMCP receipts (driver-run, deterministic).

usage: python route_costs_from_receipts.py <repo_root>

Writes validation_artifacts/ameba_cycle/route_costs_correction_001.json. The execution records of runs
002-006 carry the costs of the CLOSING attempt only (costs.measured.worker_*); for a research question about
cheap transitions the figure that matters is the whole route: every attempt (set-aside ones included), the
router's baseline and checks, and the verifier. Units are kept apart and never converted; money is unknown.
"""
import json
import pathlib
import sys

repo = pathlib.Path(sys.argv[1]).resolve()
runs = sorted((repo / "validation_artifacts" / "ameba_cycle").glob("run_00*/nomcp_coding_receipt.json"))
rows = []
for receipt_path in runs:
    coding = json.loads(receipt_path.read_text(encoding="utf-8"))
    verdict = json.loads(receipt_path.with_name("nomcp_verdict_receipt.json").read_text(encoding="utf-8"))
    attempts = [a for a in (coding.get("first_attempt"), coding.get("fallback_attempt")) if a]
    record_path = receipt_path.with_name("transition_execution_record.json")
    closing = None
    if record_path.is_file():
        closing = json.loads(record_path.read_text(encoding="utf-8"))["costs"]["measured"]
    rows.append({
        "run": receipt_path.parts[-2],
        "decision": coding.get("decision"),
        "attempts": [{"model_served": a.get("model_served"), "turns": a.get("turns"),
                      "output_tokens": a.get("output_tokens"), "wall_s": a.get("wall_s")} for a in attempts],
        "route_total": {"turns": sum(a.get("turns") or 0 for a in attempts),
                        "output_tokens": sum(a.get("output_tokens") or 0 for a in attempts),
                        "router_wall_s": coding.get("total_wall_s")},
        "verifier_wall_s": round(float(verdict["wall_s"]), 2) if verdict.get("wall_s") is not None else None,
        "recorded_in_execution_record": closing,
        "money": "unknown",
    })
out = {
    "correction_id": "route_costs_correction_001",
    "date": "2026-09-24",
    "reason": "Review of 26535dc: the execution records store the closing attempt's costs; the receipts hold every attempt and the router's total wall time. Whole-route figures are the ones to compare transitions on.",
    "source": "nomcp_coding_receipt.json (first_attempt, fallback_attempt, total_wall_s) and nomcp_verdict_receipt.json (wall_s) of each run, verbatim",
    "not_included": "driver time (packet, oracle, re-observation in a detached worktree, records); relay tokens where a Workflow relay was used (in the run READMEs where measured); money",
    "runs": rows,
}
target = repo / "validation_artifacts" / "ameba_cycle" / "route_costs_correction_001.json"
with open(target, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=True)
    fh.write("\n")
print("wrote", target.relative_to(repo).as_posix(), "runs:", len(rows))
