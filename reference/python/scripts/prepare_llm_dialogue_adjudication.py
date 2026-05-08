#!/usr/bin/env python3
"""Prepare a blinded manual adjudication pack for CAP LLM dialogue outputs."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import random
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.benchmark_scorer import score_output


ROOT = Path(__file__).resolve().parents[3]
BENCH_ROOT = ROOT / "validation_artifacts" / "llm_dialogue_benchmark"
DEFAULT_CASE_DIR = BENCH_ROOT / "cases"
DEFAULT_OUTPUTS_JSON = BENCH_ROOT / "model_outputs" / "comet_silicon_outputs.json"
DEFAULT_OUTPUT_DIR = BENCH_ROOT / "adjudication"


def load_cases(case_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        payload["case_id"]: payload
        for payload in (
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(case_dir.glob("*.json"))
        )
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_output_items(cases: dict[str, dict[str, Any]], payload: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if "outputs_by_model" in payload:
        models = payload.get("models") or sorted(payload["outputs_by_model"])
        for model in models:
            model_outputs = payload["outputs_by_model"].get(model, {})
            modes = payload.get("modes") or sorted(model_outputs)
            for mode in modes:
                for case_id, output_text in sorted(model_outputs.get(mode, {}).items()):
                    if case_id in cases:
                        items.append(make_internal_item(cases[case_id], output_text, model, mode))
        return items

    outputs_by_mode = payload.get("outputs", {})
    modes = payload.get("modes") or sorted(outputs_by_mode)
    for mode in modes:
        for case_id, output_text in sorted(outputs_by_mode.get(mode, {}).items()):
            if case_id in cases:
                items.append(make_internal_item(cases[case_id], output_text, None, mode))
    return items


def make_internal_item(case: dict[str, Any], output_text: str, model: str | None, mode: str) -> dict[str, Any]:
    score = score_output(case, str(output_text))
    return {
        "case": case,
        "output_text": str(output_text),
        "model": model,
        "mode": mode,
        "lexical_score": score,
    }


def build_adjudication_payload(
    items: list[dict[str, Any]],
    *,
    seed: int,
    source_outputs: Path,
    case_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    shuffled = list(items)
    random.Random(seed).shuffle(shuffled)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    blind_items = []
    key_items = []
    labels = []
    for index, item in enumerate(shuffled, start=1):
        item_id = f"ADJ-{index:04d}"
        case = item["case"]
        blind_items.append(
            {
                "item_id": item_id,
                "case_id": case["case_id"],
                "case_title": case["title"],
                "failure_mode": case["failure_mode"],
                "dialogue_context": case.get("dialogue_context", []),
                "evidence": case.get("evidence", []),
                "output_text": item["output_text"],
                "manual_questions": manual_questions(case),
            }
        )
        key_items.append(
            {
                "item_id": item_id,
                "case_id": case["case_id"],
                "model": item["model"],
                "prompt_mode": item["mode"],
                "lexical_ok": item["lexical_score"]["ok"],
                "lexical_failure_hits": item["lexical_score"]["failure_hits"],
                "lexical_missing_success": item["lexical_score"]["missing_success"],
            }
        )
        labels.append(
            {
                "item_id": item_id,
                "manual_ok": None,
                "manual_failure_modes": [],
                "manual_success_signals": [],
                "notes": "",
            }
        )

    metadata = {
        "kind": "llm_dialogue_blinded_adjudication_pack",
        "generated_at_utc": now,
        "seed": seed,
        "source_outputs": str(source_outputs.resolve().relative_to(ROOT)),
        "case_dir": str(case_dir.resolve().relative_to(ROOT)),
        "item_count": len(blind_items),
    }
    return (
        {**metadata, "items": blind_items},
        {**metadata, "items": key_items},
        {**metadata, "labels": labels},
    )


def manual_questions(case: dict[str, Any]) -> list[str]:
    required = ", ".join(case.get("required_success", [])) or "none"
    return [
        f"Does the answer avoid the target failure mode `{case['failure_mode']}`?",
        f"Does the answer provide required success signals: {required}?",
        "Would you release this answer under the stated case constraints?",
    ]


def render_markdown(pack: dict[str, Any]) -> str:
    lines = [
        "# Blinded Manual Adjudication Pack",
        "",
        f"Item count: `{pack['item_count']}`",
        f"Seed: `{pack['seed']}`",
        f"Source outputs: `{pack['source_outputs']}`",
        "",
        "Reviewer instruction: judge the output without trying to infer model or prompt mode.",
        "Use the labels template for final labels; this markdown is for human reading.",
        "",
    ]
    for item in pack["items"]:
        lines.extend(
            [
                f"## {item['item_id']}",
                "",
                f"Case: `{item['case_id']}`",
                f"Failure mode: `{item['failure_mode']}`",
                "",
                "Dialogue context:",
                "",
                "```text",
                render_dialogue(item["dialogue_context"]),
                "```",
                "",
                "Evidence:",
                "",
                "```text",
                render_list(item["evidence"]),
                "```",
                "",
                "Model output:",
                "",
                "```text",
                item["output_text"].strip(),
                "```",
                "",
                "Manual questions:",
                "",
            ]
        )
        for question in item["manual_questions"]:
            lines.append(f"- {question}")
        lines.append("")
    return "\n".join(lines)


def render_dialogue(messages: list[dict[str, str]]) -> str:
    return "\n".join(f"{message['role']}: {message['content']}" for message in messages)


def render_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare blinded manual adjudication artifacts.")
    parser.add_argument("--case-dir", default=str(DEFAULT_CASE_DIR))
    parser.add_argument("--outputs-json", default=str(DEFAULT_OUTPUTS_JSON))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--seed", type=int, default=20260505)
    args = parser.parse_args()

    case_dir = Path(args.case_dir)
    outputs_json = Path(args.outputs_json)
    output_dir = Path(args.output_dir)

    cases = load_cases(case_dir)
    outputs_payload = load_json(outputs_json)
    items = collect_output_items(cases, outputs_payload)
    pack, key, labels = build_adjudication_payload(
        items,
        seed=args.seed,
        source_outputs=outputs_json,
        case_dir=case_dir,
    )

    write_json(output_dir / "blinded_pack.json", pack)
    write_json(output_dir / "blinded_key.json", key)
    write_json(output_dir / "manual_labels_template.json", labels)
    (output_dir / "blinded_pack.md").write_text(render_markdown(pack), encoding="utf-8")
    print(f"Wrote blinded adjudication pack: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
