#!/usr/bin/env python3
"""Score LLM dialogue benchmark outputs for CAP failure modes.

This runner does not call an LLM. It scores already-produced outputs. The
default input is a synthetic fixture set used to verify the benchmark harness.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.benchmark_scorer import score_output, summarize_mode


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


def run_benchmark(case_dir: Path, outputs_json: Path) -> dict:
    case_dir = case_dir.resolve()
    outputs_json = outputs_json.resolve()
    cases = load_cases(case_dir)
    payload = load_outputs(outputs_json)
    mode_summaries = build_mode_summaries(cases, payload)

    return {
        "track": "llm_dialogue_benchmark",
        "status": "synthetic_fixture_smoke_test"
        if payload.get("kind") == "synthetic_smoke_outputs"
        else "scored_model_outputs",
        "case_dir": str(case_dir.relative_to(ROOT)),
        "outputs_json": str(outputs_json.relative_to(ROOT)),
        "total_cases": len(cases),
        "modes": mode_summaries,
    }


def build_mode_summaries(cases: list[dict], payload: dict) -> list[dict]:
    if "outputs_by_model" in payload:
        summaries = []
        models = payload.get("models") or sorted(payload["outputs_by_model"])
        modes = payload.get("modes")
        for model in models:
            model_outputs = payload["outputs_by_model"].get(model, {})
            model_modes = modes or sorted(model_outputs)
            for mode in model_modes:
                summary = summarize_mode_outputs(
                    cases,
                    f"{model} / {mode}",
                    model_outputs.get(mode, {}),
                )
                summary["model"] = model
                summary["prompt_mode"] = mode
                summaries.append(summary)
        return summaries

    outputs_by_mode = payload.get("outputs", {})
    modes = payload.get("modes") or sorted(outputs_by_mode)
    return [
        summarize_mode_outputs(cases, mode, outputs_by_mode.get(mode, {}))
        for mode in modes
    ]


def summarize_mode_outputs(cases: list[dict], mode: str, mode_outputs: dict) -> dict:
    case_scores = []
    for case in cases:
        output_text = mode_outputs.get(case["case_id"], "")
        if output_text:
            case_scores.append(score_output(case, output_text))
        else:
            case_scores.append(
                {
                    "case_id": case["case_id"],
                    "failure_mode": case["failure_mode"],
                    "ok": False,
                    "failure_hits": {"missing_output": ["missing output"]},
                    "success_hits": {},
                    "missing_success": case.get("required_success", []),
                    "output_excerpt": "",
                }
            )
    return summarize_mode(mode, case_scores)


def render_markdown(summary: dict) -> str:
    lines = [
        "# CAP LLM Dialogue Benchmark Report",
        "",
        f"Status: `{summary['status']}`",
        f"Case dir: `{summary['case_dir']}`",
        f"Outputs: `{summary['outputs_json']}`",
        f"Cases: `{summary['total_cases']}`",
        "",
        "This report scores already-produced outputs. It does not call an LLM.",
        "",
        "## Mode Summary",
        "",
        "| Mode | Passed | Failed | Pass rate | Failure counts | Missing required success |",
        "|---|---:|---:|---:|---|---|",
    ]
    if summary["status"] == "synthetic_fixture_smoke_test":
        lines.insert(8, "Synthetic fixture results are only a harness smoke test, not empirical evidence.")
        lines.insert(9, "")
    else:
        lines.insert(8, "These are scored model outputs. The scorer is lexical/heuristic and should be audited before treating the result as a benchmark claim.")
        lines.insert(9, "")
    for mode in summary["modes"]:
        lines.append(
            f"| `{mode['mode']}` | {mode['passed']} | {mode['failed']} | "
            f"{mode['pass_rate']:.2f} | {_format_counts(mode['failure_counts'])} | "
            f"{_format_counts(mode['missing_success_counts'])} |"
        )

    lines.extend(["", "## Case Matrix", ""])
    for mode in summary["modes"]:
        lines.extend([
            f"### {mode['mode']}",
            "",
            "| Case | Failure mode | OK | Failures | Missing success |",
            "|---|---|---:|---|---|",
        ])
        for score in mode["case_scores"]:
            lines.append(
                f"| `{score['case_id']}` | `{score['failure_mode']}` | {score['ok']} | "
                f"{_format_counts({key: len(value) for key, value in score['failure_hits'].items()})} | "
                f"{', '.join(score['missing_success']) or 'none'} |"
            )
        lines.append("")
    return "\n".join(lines)


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}:{value}" for key, value in sorted(counts.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description="Score CAP LLM dialogue benchmark outputs.")
    parser.add_argument("--case-dir", default=str(DEFAULT_CASE_DIR))
    parser.add_argument("--outputs-json", default=str(DEFAULT_OUTPUTS_JSON))
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--print-md", action="store_true")
    args = parser.parse_args()

    summary = run_benchmark(Path(args.case_dir), Path(args.outputs_json))

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
