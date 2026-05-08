#!/usr/bin/env python3
"""Prepare blinded manual adjudication artifacts for proxy release-gate actions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.release_gate_adjudication import (
    VALID_ACTIONS,
    build_release_gate_adjudication_payload,
    collect_gate_items,
    labels_payload_to_tsv,
    render_pack_markdown,
    render_readme,
)


ROOT = Path(__file__).resolve().parents[3]
BENCH_ROOT = ROOT / "validation_artifacts" / "llm_dialogue_benchmark"
DEFAULT_CASE_DIR = BENCH_ROOT / "hard_holdout" / "cases"
DEFAULT_OUTPUT_DIR = BENCH_ROOT / "hard_holdout" / "release_gate_adjudication_boundary"


def load_cases(case_dir: Path) -> dict[str, dict]:
    return {
        payload["case_id"]: payload
        for payload in (
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(case_dir.glob("*.json"))
        )
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_actions(value: str) -> set[str] | None:
    normalized = value.strip().lower()
    if normalized == "all":
        return None
    actions = {item.strip().replace("-", "_") for item in normalized.split(",") if item.strip()}
    invalid = sorted(actions - VALID_ACTIONS)
    if invalid:
        raise ValueError(f"Unsupported gate actions: {', '.join(invalid)}")
    return actions


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare proxy release-gate adjudication artifacts.")
    parser.add_argument("--case-dir", default=str(DEFAULT_CASE_DIR))
    parser.add_argument("--outputs-json", action="append", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--seed", type=int, default=20260507)
    parser.add_argument("--include-actions", default="release,block")
    parser.add_argument("--max-items", type=int)
    args = parser.parse_args()

    case_dir = Path(args.case_dir)
    output_dir = Path(args.output_dir)
    source_outputs = [Path(path) for path in args.outputs_json]
    include_actions = parse_actions(args.include_actions)

    cases = load_cases(case_dir)
    items = []
    for outputs_json in source_outputs:
        payload = load_json(outputs_json)
        items.extend(
            collect_gate_items(
                cases,
                payload,
                source_outputs=outputs_json,
                include_actions=include_actions,
            )
        )

    pack, key, labels = build_release_gate_adjudication_payload(
        items,
        seed=args.seed,
        source_outputs=source_outputs,
        case_dir=case_dir,
        include_actions=include_actions,
        max_items=args.max_items,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "blinded_pack.json", pack)
    write_json(output_dir / "blinded_key.json", key)
    write_json(output_dir / "manual_labels_template.json", labels)
    (output_dir / "manual_labels_template.tsv").write_text(labels_payload_to_tsv(labels), encoding="utf-8")
    (output_dir / "blinded_pack.md").write_text(render_pack_markdown(pack), encoding="utf-8")
    (output_dir / "README.md").write_text(render_readme(), encoding="utf-8")
    print(f"Wrote proxy release-gate adjudication pack: {output_dir}")
    print(f"Items: {pack['item_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
