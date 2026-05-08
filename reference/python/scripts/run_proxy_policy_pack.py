#!/usr/bin/env python3
"""Run deterministic CAP LLM proxy policy cases."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.proxy_policy import evaluate_case, expected_subset_matches


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CASE_DIR = ROOT / "validation_artifacts" / "llm_dialogue_proxy" / "cases"


def load_cases(case_dir: Path) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(case_dir.glob("*.json"))
    ]


def run_cases(case_dir: Path) -> dict:
    cases = []
    for case in load_cases(case_dir):
        actual = evaluate_case(case)
        issues = expected_subset_matches(actual, case.get("expected_policy", {}))
        cases.append(
            {
                "case_id": case["case_id"],
                "ok": not issues,
                "issues": issues,
                "policy": actual["policy"],
            }
        )
    return {
        "track": "llm_dialogue_proxy_policy",
        "case_dir": str(case_dir.relative_to(ROOT)),
        "total": len(cases),
        "passed": sum(1 for case in cases if case["ok"]),
        "failed": sum(1 for case in cases if not case["ok"]),
        "cases": cases,
    }


def render_markdown(summary: dict) -> str:
    lines = [
        "# CAP LLM Dialogue Proxy Policy Pack",
        "",
        f"Case dir: `{summary['case_dir']}`",
        f"Total: `{summary['total']}`",
        f"Passed: `{summary['passed']}`",
        f"Failed: `{summary['failed']}`",
        "",
        "| Case | OK | Node status | Release action | Forbid | Require |",
        "|---|---:|---|---|---|---|",
    ]
    for case in summary["cases"]:
        policy = case["policy"]
        lines.append(
            f"| `{case['case_id']}` | {case['ok']} | "
            f"`{policy['node_status']}` | `{policy['release_action']}` | "
            f"{', '.join(policy['forbid']) or 'none'} | "
            f"{', '.join(policy['require']) or 'none'} |"
        )
    failed = [case for case in summary["cases"] if not case["ok"]]
    if failed:
        lines.extend(["", "## Issues", ""])
        for case in failed:
            for issue in case["issues"]:
                lines.append(f"- `{case['case_id']}`: {issue}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic proxy-policy cases.")
    parser.add_argument("--case-dir", default=str(DEFAULT_CASE_DIR))
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--print-md", action="store_true")
    args = parser.parse_args()

    summary = run_cases(Path(args.case_dir))

    if args.output_json:
        output = Path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        output = Path(args.output_md)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_markdown(summary), encoding="utf-8")

    if args.print_md:
        print(render_markdown(summary))
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
