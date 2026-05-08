"""Manual adjudication disagreement analysis for CAP dialogue benchmark."""
from __future__ import annotations

from typing import Any


def analyze_disagreements(key_payload: dict[str, Any], labels_payload: dict[str, Any]) -> dict[str, Any]:
    key_by_id = {item["item_id"]: item for item in key_payload.get("items", [])}
    labels = labels_payload.get("labels", [])

    pending: list[str] = []
    agreements: list[dict[str, Any]] = []
    disagreements: list[dict[str, Any]] = []

    for label in labels:
        item_id = label["item_id"]
        key = key_by_id.get(item_id)
        if key is None:
            pending.append(item_id)
            continue
        manual_ok = label.get("manual_ok")
        if manual_ok is None:
            pending.append(item_id)
            continue

        lexical_ok = bool(key.get("lexical_ok", False))
        record = {
            "item_id": item_id,
            "case_id": key.get("case_id"),
            "model": key.get("model"),
            "prompt_mode": key.get("prompt_mode"),
            "lexical_ok": lexical_ok,
            "manual_ok": bool(manual_ok),
            "lexical_missing_success": key.get("lexical_missing_success", []),
            "manual_failure_modes": label.get("manual_failure_modes", []),
            "manual_success_signals": label.get("manual_success_signals", []),
            "notes": label.get("notes", ""),
        }
        if lexical_ok == bool(manual_ok):
            agreements.append(record)
        else:
            disagreements.append(record)

    judged = len(agreements) + len(disagreements)
    return {
        "kind": "adjudication_disagreement_summary",
        "status": "pending_manual_labels" if judged == 0 else "manual_labels_compared",
        "item_count": len(labels),
        "judged_count": judged,
        "pending_count": len(pending),
        "agreement_count": len(agreements),
        "disagreement_count": len(disagreements),
        "agreement_rate": (len(agreements) / judged) if judged else None,
        "pending_items": pending,
        "disagreements": disagreements,
        "summary_by_model_mode": summarize_by_model_mode(agreements + disagreements),
    }


def summarize_by_model_mode(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for record in records:
        key = f"{record.get('model')} / {record.get('prompt_mode')}"
        if key not in summary:
            summary[key] = {"judged": 0, "agreements": 0, "disagreements": 0}
        summary[key]["judged"] += 1
        if record["lexical_ok"] == record["manual_ok"]:
            summary[key]["agreements"] += 1
        else:
            summary[key]["disagreements"] += 1
    return summary


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# CAP Adjudication Disagreement Analysis",
        "",
        f"Status: `{summary['status']}`",
        f"Items: `{summary['item_count']}`",
        f"Judged: `{summary['judged_count']}`",
        f"Pending: `{summary['pending_count']}`",
        f"Agreements: `{summary['agreement_count']}`",
        f"Disagreements: `{summary['disagreement_count']}`",
        "",
    ]
    if summary["agreement_rate"] is None:
        lines.extend(
            [
                "Manual labels are not filled yet. Fill `manual_labels_template.json` or `manual_labels_template.tsv`, then rerun this analysis.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            f"Agreement rate: `{summary['agreement_rate']:.2f}`",
            "",
            "## By Model / Mode",
            "",
            "| Model / mode | Judged | Agreements | Disagreements |",
            "|---|---:|---:|---:|",
        ]
    )
    for key, row in sorted(summary["summary_by_model_mode"].items()):
        lines.append(f"| `{key}` | {row['judged']} | {row['agreements']} | {row['disagreements']} |")

    lines.extend(["", "## Disagreements", ""])
    if not summary["disagreements"]:
        lines.append("No disagreements.")
        return "\n".join(lines)

    lines.extend(
        [
            "| Item | Case | Model | Mode | Lexical | Manual | Notes |",
            "|---|---|---|---|---:|---:|---|",
        ]
    )
    for item in summary["disagreements"]:
        notes = str(item.get("notes", "")).replace("|", "/")
        lines.append(
            f"| `{item['item_id']}` | `{item['case_id']}` | `{item['model']}` | "
            f"`{item['prompt_mode']}` | {item['lexical_ok']} | {item['manual_ok']} | {notes} |"
        )
    return "\n".join(lines)
