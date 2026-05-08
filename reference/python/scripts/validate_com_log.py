#!/usr/bin/env python3
"""Validate a COM-Log JSON file against the CAP schema."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make cap module importable when running as script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cap.validator import validate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a COM-Log JSON file.")
    parser.add_argument("file", help="Path to COM-Log JSON file")
    args = parser.parse_args()

    com_log = json.loads(Path(args.file).read_text(encoding="utf-8"))
    result = validate(com_log)

    if result["valid"]:
        print(f"VALID: {args.file}")
        return 0
    print(f"INVALID: {args.file}")
    for err in result["errors"]:
        print(f"  {err}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
