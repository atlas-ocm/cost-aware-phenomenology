#!/usr/bin/env python3
"""Analyze proxy release-gate/manual adjudication disagreements."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.release_gate_adjudication import (
    analyze_release_gate_adjudication,
    labels_payload_from_tsv,
    render_summary_markdown,
)


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ADJUDICATION_DIR = (
    ROOT
    / "validation_artifacts"
    / "llm_dialogue_benchmark"
    / "hard_holdout"
    / "release_gate_adjudication_boundary"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze proxy release-gate adjudication disagreements.")
    parser.add_argument("--adjudication-dir", default=str(DEFAULT_ADJUDICATION_DIR))
    parser.add_argument("--labels-json")
    parser.add_argument("--labels-tsv")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--print-md", action="store_true")
    args = parser.parse_args()

    if args.labels_json and args.labels_tsv:
        raise SystemExit("--labels-json and --labels-tsv are mutually exclusive")

    adjudication_dir = Path(args.adjudication_dir)
    key_payload = json.loads((adjudication_dir / "blinded_key.json").read_text(encoding="utf-8"))
    if args.labels_tsv:
        labels_tsv_path = Path(args.labels_tsv)
        base_path = adjudication_dir / "manual_labels_template.json"
        base_payload = json.loads(base_path.read_text(encoding="utf-8")) if base_path.exists() else None
        labels_payload = labels_payload_from_tsv(labels_tsv_path.read_text(encoding="utf-8"), base_payload)
    else:
        labels_path = Path(args.labels_json) if args.labels_json else adjudication_dir / "manual_labels_template.json"
        labels_payload = json.loads(labels_path.read_text(encoding="utf-8"))

    summary = analyze_release_gate_adjudication(key_payload, labels_payload)

    if args.output_json:
        output = Path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        output = Path(args.output_md)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_summary_markdown(summary), encoding="utf-8")

    if args.print_md:
        print(render_summary_markdown(summary))
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
