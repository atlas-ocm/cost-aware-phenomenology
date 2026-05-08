#!/usr/bin/env python3
"""Redact provider-internal reasoning fields from benchmark JSON artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_llm_dialogue_outputs import REDACTED_PROVIDER_FIELDS


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = ROOT / "validation_artifacts" / "llm_dialogue_benchmark"
REDACTION_MARKER = "[redacted_provider_internal]"


def sanitize_provider_internal_fields(value: Any) -> tuple[Any, int]:
    """Return a copy with provider-internal fields redacted and redaction count."""
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        redactions = 0
        for key, child in value.items():
            if key in REDACTED_PROVIDER_FIELDS:
                sanitized[key] = REDACTION_MARKER
                redactions += 0 if child == REDACTION_MARKER else 1
                continue
            sanitized_child, child_redactions = sanitize_provider_internal_fields(child)
            sanitized[key] = sanitized_child
            redactions += child_redactions
        return sanitized, redactions

    if isinstance(value, list):
        sanitized_items = []
        redactions = 0
        for item in value:
            sanitized_item, item_redactions = sanitize_provider_internal_fields(item)
            sanitized_items.append(sanitized_item)
            redactions += item_redactions
        return sanitized_items, redactions

    return value, 0


def iter_json_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(root.rglob("*.json"))


def sanitize_file(path: Path, *, write: bool) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    sanitized, redactions = sanitize_provider_internal_fields(payload)
    if write and redactions:
        path.write_text(
            json.dumps(sanitized, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return redactions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Redact provider-internal reasoning fields from CAP benchmark JSON "
            "artifacts. Defaults to dry-run; pass --write to update files."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help=f"JSON file or directory to scan (default: {DEFAULT_ROOT})",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="write sanitized JSON files instead of reporting only",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root if args.root.is_absolute() else (Path.cwd() / args.root)
    if not root.exists():
        raise SystemExit(f"Path not found: {root}")

    changed: list[tuple[Path, int]] = []
    for path in iter_json_files(root):
        redactions = sanitize_file(path, write=args.write)
        if redactions:
            changed.append((path, redactions))

    action = "updated" if args.write else "would update"
    if not changed:
        print("No unredacted provider-internal fields found.")
        return 0

    total = sum(count for _, count in changed)
    print(f"{action} {len(changed)} file(s), {total} field value(s):")
    for path, count in changed:
        print(f"- {path.relative_to(ROOT)} ({count})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
