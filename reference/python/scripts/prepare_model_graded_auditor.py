#!/usr/bin/env python3
"""Prepare optional model-graded auditor prompts for CAP dialogue outputs.

This script does not call an LLM. It builds a judge prompt pack from existing
benchmark outputs and optionally summarizes supplied judge responses.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.model_graded_auditor import (
    build_audit_records,
    build_response_template,
    render_prompt_pack_markdown,
    summarize_judge_responses,
)


ROOT = Path(__file__).resolve().parents[3]
BENCH_ROOT = ROOT / "validation_artifacts" / "llm_dialogue_benchmark"
DEFAULT_CASE_DIR = BENCH_ROOT / "cases"
DEFAULT_OUTPUTS_JSON = BENCH_ROOT / "model_outputs" / "comet_silicon_outputs.json"
DEFAULT_OUTPUT_DIR = BENCH_ROOT / "model_graded_auditor"


def load_cases(case_dir: Path) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(case_dir.glob("*.json"))
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare CAP model-graded auditor prompt pack.")
    parser.add_argument("--case-dir", default=str(DEFAULT_CASE_DIR))
    parser.add_argument("--outputs-json", default=str(DEFAULT_OUTPUTS_JSON))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--judge-responses-json")
    parser.add_argument("--limit-records", type=int)
    parser.add_argument("--print-summary", action="store_true")
    args = parser.parse_args()

    case_dir = Path(args.case_dir).resolve()
    outputs_json = Path(args.outputs_json).resolve()
    output_dir = Path(args.output_dir)

    cases = load_cases(case_dir)
    outputs_payload = json.loads(outputs_json.read_text(encoding="utf-8"))
    records = build_audit_records(cases, outputs_payload)
    if args.limit_records:
        records = records[: args.limit_records]

    output_dir.mkdir(parents=True, exist_ok=True)
    pack = {
        "kind": "model_graded_auditor_prompt_pack",
        "status": "optional_auxiliary_not_ground_truth",
        "case_dir": str(case_dir.relative_to(ROOT)),
        "outputs_json": str(outputs_json.relative_to(ROOT)),
        "total_records": len(records),
        "records": records,
    }

    (output_dir / "judge_prompt_pack.json").write_text(
        json.dumps(pack, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "judge_prompt_pack.md").write_text(
        render_prompt_pack_markdown(records),
        encoding="utf-8",
    )
    (output_dir / "judge_response_template.json").write_text(
        json.dumps(build_response_template(records), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(
        render_readme(_display_path(outputs_json), len(records)),
        encoding="utf-8",
    )

    summary = {
        "kind": "model_graded_auditor_prepare_result",
        "status": "prompt_pack_written",
        "output_dir": str(output_dir),
        "records": len(records),
    }

    if args.judge_responses_json:
        responses_payload = json.loads(Path(args.judge_responses_json).read_text(encoding="utf-8"))
        responses = responses_payload.get("judge_responses", responses_payload)
        judge_summary = summarize_judge_responses(records, responses)
        (output_dir / "judge_summary.json").write_text(
            json.dumps(judge_summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        summary["judge_summary"] = judge_summary

    if args.print_summary:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Wrote model-graded auditor prompt pack: {output_dir}")
    return 0


def render_readme(outputs_json: str, records: int) -> str:
    return "\n".join(
        [
            "# Model-Graded Auditor Prompt Pack",
            "",
            "Status: optional auxiliary audit artifact.",
            "",
            "This folder contains prompts that can be given to a separate judge model or human reviewer.",
            "The judge is not treated as ground truth and does not replace blinded manual adjudication.",
            "",
            "Source outputs:",
            "",
            f"```text\n{outputs_json}\n```",
            "",
            f"Records: `{records}`",
            "",
            "Files:",
            "",
            "- `judge_prompt_pack.json` - machine-readable prompt pack",
            "- `judge_prompt_pack.md` - readable prompt pack",
            "- `judge_response_template.json` - response template keyed by `record_id`",
            "",
            "Recommended use:",
            "",
            "1. Freeze the lexical scorer and case pack.",
            "2. Run a judge model over `judge_prompt_pack.json` or review manually.",
            "3. Store responses in the template shape.",
            "4. Compare judge labels with lexical scores and manual adjudication.",
            "",
            "Do not cite the judge score as a benchmark result without reporting the judge model, prompt, disagreements, and manual review status.",
            "",
        ]
    )


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
