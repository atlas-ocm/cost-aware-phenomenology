#!/usr/bin/env python3
"""Run validation across all JSON files in a case pack folder."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cap.validator import validate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run validation across a case pack folder."
    )
    parser.add_argument("folder", help="Folder containing case JSON files")
    args = parser.parse_args()

    folder = Path(args.folder)
    case_files = sorted(folder.glob("*.json"))

    valid = 0
    invalid = 0
    for f in case_files:
        data = json.loads(f.read_text(encoding="utf-8"))
        # Skip case-definition files (they are inputs, not COM-Log outputs)
        if "ground_truth" in data and "case_id" in data:
            print(f"SKIP (case definition): {f.name}")
            continue
        result = validate(data)
        if result["valid"]:
            print(f"VALID:   {f.name}")
            valid += 1
        else:
            print(f"INVALID: {f.name}")
            for err in result["errors"]:
                print(f"  {err}")
            invalid += 1

    total = valid + invalid
    print(f"\nSummary: {valid} valid / {invalid} invalid / {total} checked")
    return 0 if invalid == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
