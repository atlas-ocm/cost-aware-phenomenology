#!/usr/bin/env python3
"""Validate an executed-transition record against its schema and the repository.

Usage:

    python validate_execution_record.py <record.json> [--repo <dir>]

The schema check is only half of it: this command also resolves every
reference, re-derives every input hash, resolves every git revision (using
--repo) and checks criterion coverage. Exit 0 means no problems, 1 means the
record has problems, 2 means the record file could not be read.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make cap module importable when running as script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cap.execution_record import validate_execution_record  # noqa: E402

CAP_ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an executed-transition record.",
    )
    parser.add_argument("record", help="Path to the executed-transition record JSON file")
    parser.add_argument(
        "--repo",
        default=None,
        help="Repository directory used to resolve the record's revisions",
    )
    args = parser.parse_args()

    try:
        record = json.loads(Path(args.record).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        print(f"{args.record}: cannot read record: {exc}")
        return 2

    repo_dir = Path(args.repo) if args.repo else None
    problems = validate_execution_record(record, base_dir=CAP_ROOT, repo_dir=repo_dir)

    if not problems:
        print("OK")
        return 0
    for problem in problems:
        print(problem)
    return 1


if __name__ == "__main__":
    sys.exit(main())
