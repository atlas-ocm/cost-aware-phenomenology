#!/usr/bin/env python3
"""Run the deterministic CAP proxy release gate over produced outputs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.proxy_release_gate import (
    GATE_VERSION_V01,
    GATE_VERSION_V02,
    gate_output,
    summarize_gate_mode,
)


ROOT = Path(__file__).resolve().parents[3]
BENCH_ROOT = ROOT / "validation_artifacts" / "llm_dialogue_benchmark"
DEFAULT_CASE_DIR = BENCH_ROOT / "cases"
DEFAULT_OUTPUTS_JSON = BENCH_ROOT / "fixture_outputs" / "smoke_outputs.json"


def load_cases(case_dir: Path) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(case_dir.glob("*.json"))
    ]


def load_outputs(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_release_gate(
    case_dir: Path,
    outputs_json: Path,
    *,
    gate_version: str = GATE_VERSION_V01,
) -> dict:
    case_dir = case_dir.resolve()
    outputs_json = outputs_json.resolve()
    cases = load_cases(case_dir)
    payload = load_outputs(outputs_json)
    mode_summaries = build_gate_mode_summaries(cases, payload, gate_version=gate_version)

    return {
        "track": "llm_dialogue_proxy_release_gate",
        "status": (
            "deterministic_release_gate"
            if gate_version == GATE_VERSION_V01
            else "deterministic_release_gate_v02"
        ),
        "gate_version": gate_version,
        "case_dir": str(case_dir.relative_to(ROOT)),
        "outputs_json": str(outputs_json.relative_to(ROOT)),
        "total_cases": len(cases),
        "modes": mode_summaries,
    }


def build_gate_mode_summaries(
    cases: list[dict],
    payload: dict,
    *,
    gate_version: str = GATE_VERSION_V01,
) -> list[dict]:
    if "outputs_by_model" in payload:
        summaries = []
        models = payload.get("models") or sorted(payload["outputs_by_model"])
        modes = payload.get("modes")
        for model in models:
            model_outputs = payload["outputs_by_model"].get(model, {})
            model_modes = modes or sorted(model_outputs)
            for mode in model_modes:
                summary = summarize_gate_outputs(
                    cases,
                    f"{model} / {mode}",
                    model_outputs.get(mode, {}),
                    gate_version=gate_version,
                )
                summary["model"] = model
                summary["prompt_mode"] = mode
                summaries.append(summary)
        return summaries

    outputs_by_mode = payload.get("outputs", {})
    modes = payload.get("modes") or sorted(outputs_by_mode)
    return [
        summarize_gate_outputs(
            cases,
            mode,
            outputs_by_mode.get(mode, {}),
            gate_version=gate_version,
        )
        for mode in modes
    ]


def summarize_gate_outputs(
    cases: list[dict],
    mode: str,
    mode_outputs: dict,
    *,
    gate_version: str = GATE_VERSION_V01,
) -> dict:
    results = []
    for case in cases:
        output_text = mode_outputs.get(case["case_id"], "")
        if output_text:
            results.append(gate_output(case, output_text, gate_version=gate_version))
        else:
            results.append(
                {
                    "gate_version": gate_version,
                    "case_id": case["case_id"],
                    "failure_mode": case["failure_mode"],
                    "release_action": "block",
                    "release": False,
                    "blocked_failure_hits": {"missing_output": ["missing output"]},
                    "contextualized_failure_hits": {},
                    "shape_rewrite_hits": {},
                    "success_hits": {},
                    "missing_success": case.get("required_success", []),
                    "rewrite_requirements": [],
                    "reasons": ["blocking_failure:missing_output"],
                    "output_excerpt": "",
                }
            )
    return summarize_gate_mode(mode, results)


def render_markdown(summary: dict) -> str:
    lines = [
        "# CAP Proxy Release Gate Report",
        "",
        f"Status: `{summary['status']}`",
        f"Gate version: `{summary.get('gate_version', GATE_VERSION_V01)}`",
        f"Case dir: `{summary['case_dir']}`",
        f"Outputs: `{summary['outputs_json']}`",
        f"Cases: `{summary['total_cases']}`",
        "",
        "This report runs a deterministic post-generation gate. It does not call an LLM.",
        "A release means no blocking failure signal and all required success signals are present.",
        "A rewrite means no blocking failure signal, but required release evidence is missing.",
        "A block means a non-contextualized failure signal remains in the output.",
        "",
        "## Mode Summary",
        "",
        "| Mode | Release | Rewrite required | Block | Release rate | Blocking failures | Missing success | Shape rewrites |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ]
    for mode in summary["modes"]:
        lines.append(
            f"| `{mode['mode']}` | {mode['released']} | {mode['rewrite_required']} | "
            f"{mode['blocked']} | {mode['release_rate']:.2f} | "
            f"{_format_counts(mode['blocked_failure_counts'])} | "
            f"{_format_counts(mode['missing_success_counts'])} | "
            f"{_format_counts(mode.get('shape_rewrite_counts', {}))} |"
        )

    lines.extend(["", "## Case Matrix", ""])
    for mode in summary["modes"]:
        lines.extend([
            f"### {mode['mode']}",
            "",
            "| Case | Action | Blocking failures | Missing success | Shape rewrites | Rewrite requirements |",
            "|---|---|---|---|---|---|",
        ])
        for result in mode["case_results"]:
            lines.append(
                f"| `{result['case_id']}` | `{result['release_action']}` | "
                f"{_format_counts({key: len(value) for key, value in result['blocked_failure_hits'].items()})} | "
                f"{', '.join(result['missing_success']) or 'none'} | "
                f"{_format_counts({key: len(value) for key, value in result.get('shape_rewrite_hits', {}).items()})} | "
                f"{', '.join(result['rewrite_requirements']) or 'none'} |"
            )
        lines.append("")
    return "\n".join(lines)


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}:{value}" for key, value in sorted(counts.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CAP proxy release gate.")
    parser.add_argument("--case-dir", default=str(DEFAULT_CASE_DIR))
    parser.add_argument("--outputs-json", default=str(DEFAULT_OUTPUTS_JSON))
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument(
        "--gate-version",
        choices=[GATE_VERSION_V01, GATE_VERSION_V02],
        default=GATE_VERSION_V01,
    )
    parser.add_argument("--print-md", action="store_true")
    args = parser.parse_args()

    summary = run_release_gate(
        Path(args.case_dir),
        Path(args.outputs_json),
        gate_version=args.gate_version,
    )

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
