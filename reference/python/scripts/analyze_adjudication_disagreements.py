#!/usr/bin/env python3
"""Compare lexical scorer labels with manual adjudication labels."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.adjudication_disagreement import analyze_disagreements, render_markdown
from cap.adjudication_labels_tsv import labels_payload_from_tsv


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ADJUDICATION_DIR = (
    ROOT / "validation_artifacts" / "llm_dialogue_benchmark" / "adjudication_four_model"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze lexical/manual adjudication disagreements.")
    parser.add_argument("--adjudication-dir", default=str(DEFAULT_ADJUDICATION_DIR))
    parser.add_argument("--labels-json", help="Override manual labels JSON path.")
    parser.add_argument("--labels-tsv", help="Use a TSV manual labels sheet instead of JSON.")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--print-md", action="store_true")
    args = parser.parse_args()

    adjudication_dir = Path(args.adjudication_dir)
    key_path = adjudication_dir / "blinded_key.json"
    if args.labels_json and args.labels_tsv:
        raise SystemExit("--labels-json and --labels-tsv are mutually exclusive")

    key_payload = json.loads(key_path.read_text(encoding="utf-8"))
    if args.labels_tsv:
        labels_tsv_path = Path(args.labels_tsv)
        base_labels_path = adjudication_dir / "manual_labels_template.json"
        base_payload = json.loads(base_labels_path.read_text(encoding="utf-8")) if base_labels_path.exists() else None
        labels_payload = labels_payload_from_tsv(labels_tsv_path.read_text(encoding="utf-8"), base_payload)
    else:
        labels_path = Path(args.labels_json) if args.labels_json else adjudication_dir / "manual_labels_template.json"
        labels_payload = json.loads(labels_path.read_text(encoding="utf-8"))
    summary = analyze_disagreements(key_payload, labels_payload)

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
