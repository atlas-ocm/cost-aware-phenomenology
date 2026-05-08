"""TSV helpers for blinded manual adjudication labels."""
from __future__ import annotations

import csv
import io
from copy import deepcopy
from typing import Any


FIELDS = ["item_id", "manual_ok", "manual_failure_modes", "manual_success_signals", "notes"]

TRUE_VALUES = {"true", "pass", "passed", "ok", "yes", "y", "1"}
FALSE_VALUES = {"false", "fail", "failed", "no", "n", "0"}


def labels_payload_to_tsv(payload: dict[str, Any]) -> str:
    """Render a manual labels JSON payload as spreadsheet-friendly TSV."""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for label in payload.get("labels", []):
        writer.writerow(
            {
                "item_id": label.get("item_id", ""),
                "manual_ok": format_manual_ok(label.get("manual_ok")),
                "manual_failure_modes": format_list(label.get("manual_failure_modes", [])),
                "manual_success_signals": format_list(label.get("manual_success_signals", [])),
                "notes": label.get("notes", ""),
            }
        )
    return buffer.getvalue()


def labels_payload_from_tsv(tsv_text: str, base_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Parse a TSV label sheet back into the JSON payload shape."""
    reader = csv.DictReader(io.StringIO(tsv_text), delimiter="\t")
    if reader.fieldnames is None:
        raise ValueError("TSV label sheet is empty")
    missing = [field for field in FIELDS if field not in reader.fieldnames]
    if missing:
        raise ValueError(f"TSV label sheet is missing required columns: {', '.join(missing)}")

    payload = deepcopy(base_payload) if base_payload else {"kind": "llm_dialogue_blinded_adjudication_pack"}
    existing_labels = {label["item_id"]: deepcopy(label) for label in payload.get("labels", [])}
    ordered_ids = [label["item_id"] for label in payload.get("labels", [])]

    for row in reader:
        item_id = (row.get("item_id") or "").strip()
        if not item_id:
            continue
        if item_id not in existing_labels:
            existing_labels[item_id] = {
                "item_id": item_id,
                "manual_ok": None,
                "manual_failure_modes": [],
                "manual_success_signals": [],
                "notes": "",
            }
            ordered_ids.append(item_id)
        existing_labels[item_id].update(
            {
                "manual_ok": parse_manual_ok(row.get("manual_ok", "")),
                "manual_failure_modes": parse_list(row.get("manual_failure_modes", "")),
                "manual_success_signals": parse_list(row.get("manual_success_signals", "")),
                "notes": row.get("notes", "") or "",
            }
        )

    payload["labels"] = [existing_labels[item_id] for item_id in ordered_ids if item_id in existing_labels]
    payload["item_count"] = len(payload["labels"])
    return payload


def format_manual_ok(value: Any) -> str:
    if value is True:
        return "pass"
    if value is False:
        return "fail"
    return ""


def parse_manual_ok(value: str | None) -> bool | None:
    normalized = (value or "").strip().lower()
    if not normalized:
        return None
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(f"Unsupported manual_ok value: {value!r}")


def format_list(values: list[str]) -> str:
    return ", ".join(values)


def parse_list(value: str | None) -> list[str]:
    if not value:
        return []
    normalized = value.replace(";", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]
