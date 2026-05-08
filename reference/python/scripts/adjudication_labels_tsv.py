#!/usr/bin/env python3
"""Export/import blinded manual adjudication labels as TSV."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.adjudication_labels_tsv import labels_payload_from_tsv, labels_payload_to_tsv


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ADJUDICATION_DIR = ROOT / "validation_artifacts" / "llm_dialogue_benchmark" / "adjudication_four_model"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export/import manual adjudication labels as TSV.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Export JSON labels to TSV.")
    export_parser.add_argument("--adjudication-dir", default=str(DEFAULT_ADJUDICATION_DIR))
    export_parser.add_argument("--labels-json", help="Input labels JSON. Defaults to manual_labels_template.json.")
    export_parser.add_argument("--output-tsv", help="Output TSV. Defaults to manual_labels_template.tsv.")

    import_parser = subparsers.add_parser("import", help="Import TSV labels to JSON.")
    import_parser.add_argument("--adjudication-dir", default=str(DEFAULT_ADJUDICATION_DIR))
    import_parser.add_argument("--labels-tsv", help="Input TSV. Defaults to manual_labels_template.tsv.")
    import_parser.add_argument("--base-labels-json", help="Base labels JSON for metadata/order preservation.")
    import_parser.add_argument("--output-json", help="Output JSON. Defaults to manual_labels_from_tsv.json.")

    args = parser.parse_args()
    adjudication_dir = Path(args.adjudication_dir)

    if args.command == "export":
        labels_json = Path(args.labels_json) if args.labels_json else adjudication_dir / "manual_labels_template.json"
        output_tsv = Path(args.output_tsv) if args.output_tsv else adjudication_dir / "manual_labels_template.tsv"
        payload = load_json(labels_json)
        output_tsv.parent.mkdir(parents=True, exist_ok=True)
        output_tsv.write_text(labels_payload_to_tsv(payload), encoding="utf-8")
        print(f"Wrote TSV labels sheet: {output_tsv}")
        return 0

    labels_tsv = Path(args.labels_tsv) if args.labels_tsv else adjudication_dir / "manual_labels_template.tsv"
    base_labels_json = (
        Path(args.base_labels_json) if args.base_labels_json else adjudication_dir / "manual_labels_template.json"
    )
    output_json = Path(args.output_json) if args.output_json else adjudication_dir / "manual_labels_from_tsv.json"
    base_payload = load_json(base_labels_json) if base_labels_json.exists() else None
    payload = labels_payload_from_tsv(labels_tsv.read_text(encoding="utf-8"), base_payload)
    write_json(output_json, payload)
    print(f"Wrote JSON labels: {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
