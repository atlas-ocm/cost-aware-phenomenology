#!/usr/bin/env python3
"""Run the deterministic CAP proxy rewrite shaper over produced outputs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.proxy_release_gate import GATE_VERSION_V02
from cap.proxy_rewrite_shaper import shape_outputs_payload, summarize_shape_decisions


ROOT = Path(__file__).resolve().parents[3]
BENCH_ROOT = ROOT / "validation_artifacts" / "llm_dialogue_benchmark"
DEFAULT_CASE_DIR = BENCH_ROOT / "hard_holdout" / "cases"


def load_cases(case_dir: Path) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(case_dir.glob("*.json"))
    ]


def load_outputs(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_markdown(summary: dict) -> str:
    lines = [
        "# CAP Proxy Rewrite Shaper Report",
        "",
        "Status: `deterministic_case_contract_shaper`",
        "",
        "This report summarizes a deterministic post-gate shaper run. It does not",
        "call an LLM and the shaped outputs are not raw model outputs.",
        "",
        f"Total shaped cases: `{summary['total']}`",
        "",
        "## Action Counts",
        "",
        "| Action | Count |",
        "|---|---:|",
    ]
    for action, count in sorted(summary["shaper_action_counts"].items()):
        lines.append(f"| `{action}` | {count} |")

    lines.extend([
        "",
        "## Shaped Gate Actions",
        "",
        "| Gate action after shaping | Count |",
        "|---|---:|",
    ])
    for action, count in sorted(summary["shaped_release_action_counts"].items()):
        lines.append(f"| `{action}` | {count} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CAP proxy rewrite shaper.")
    parser.add_argument("--case-dir", default=str(DEFAULT_CASE_DIR))
    parser.add_argument("--outputs-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--summary-json")
    parser.add_argument("--summary-md")
    args = parser.parse_args()

    cases = load_cases(Path(args.case_dir))
    payload = load_outputs(Path(args.outputs_json))
    shaped_payload = shape_outputs_payload(cases, payload, gate_version=GATE_VERSION_V02)
    summary = summarize_shape_decisions(shaped_payload)
    summary.update({
        "case_dir": str(Path(args.case_dir)),
        "outputs_json": str(Path(args.outputs_json)),
        "output_json": str(Path(args.output_json)),
        "gate_version": GATE_VERSION_V02,
        "kind": "cap_proxy_rewrite_shaper_summary",
    })

    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(shaped_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.summary_json:
        summary_output = Path(args.summary_json)
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.summary_md:
        summary_output = Path(args.summary_md)
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.write_text(render_markdown(summary), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
