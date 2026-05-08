"""Blinded adjudication helpers for CAP proxy release-gate actions."""
from __future__ import annotations

import csv
import io
import random
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cap.proxy_release_gate import BLOCK, RELEASE, REWRITE_REQUIRED, gate_output


VALID_ACTIONS = {RELEASE, REWRITE_REQUIRED, BLOCK}
LABEL_FIELDS = [
    "item_id",
    "manual_action",
    "manual_failure_modes",
    "manual_missing_success",
    "notes",
]


def collect_gate_items(
    cases: dict[str, dict[str, Any]],
    payload: dict[str, Any],
    *,
    source_outputs: Path,
    include_actions: set[str] | None = None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if "outputs_by_model" in payload:
        models = payload.get("models") or sorted(payload["outputs_by_model"])
        for model in models:
            model_outputs = payload["outputs_by_model"].get(model, {})
            modes = payload.get("modes") or sorted(model_outputs)
            for mode in modes:
                items.extend(
                    _collect_mode_items(
                        cases,
                        model_outputs.get(mode, {}),
                        model=model,
                        mode=mode,
                        source_outputs=source_outputs,
                        include_actions=include_actions,
                    )
                )
        return items

    outputs_by_mode = payload.get("outputs", {})
    modes = payload.get("modes") or sorted(outputs_by_mode)
    for mode in modes:
        items.extend(
            _collect_mode_items(
                cases,
                outputs_by_mode.get(mode, {}),
                model=None,
                mode=mode,
                source_outputs=source_outputs,
                include_actions=include_actions,
            )
        )
    return items


def _collect_mode_items(
    cases: dict[str, dict[str, Any]],
    mode_outputs: dict[str, Any],
    *,
    model: str | None,
    mode: str,
    source_outputs: Path,
    include_actions: set[str] | None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for case_id, case in sorted(cases.items()):
        output_text = str(mode_outputs.get(case_id, ""))
        gate = _gate_or_missing_output(case, output_text)
        if include_actions and gate["release_action"] not in include_actions:
            continue
        items.append(
            {
                "case": case,
                "output_text": output_text,
                "model": model,
                "mode": mode,
                "source_outputs": source_outputs,
                "gate": gate,
            }
        )
    return items


def _gate_or_missing_output(case: dict[str, Any], output_text: str) -> dict[str, Any]:
    if output_text.strip():
        return gate_output(case, output_text)
    return {
        "case_id": case["case_id"],
        "failure_mode": case["failure_mode"],
        "release_action": BLOCK,
        "release": False,
        "blocked_failure_hits": {"missing_output": ["missing output"]},
        "contextualized_failure_hits": {},
        "success_hits": {},
        "missing_success": case.get("required_success", []),
        "rewrite_requirements": [],
        "reasons": ["blocking_failure:missing_output"],
        "output_excerpt": "",
    }


def build_release_gate_adjudication_payload(
    items: list[dict[str, Any]],
    *,
    seed: int,
    source_outputs: list[Path],
    case_dir: Path,
    include_actions: set[str] | None = None,
    max_items: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    shuffled = list(items)
    random.Random(seed).shuffle(shuffled)
    if max_items is not None:
        shuffled = shuffled[:max_items]
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    blind_items = []
    key_items = []
    labels = []
    for index, item in enumerate(shuffled, start=1):
        item_id = f"GATE-ADJ-{index:04d}"
        case = item["case"]
        gate = item["gate"]
        blind_items.append(
            {
                "item_id": item_id,
                "case_id": case["case_id"],
                "case_title": case["title"],
                "failure_mode": case["failure_mode"],
                "dialogue_context": case.get("dialogue_context", []),
                "evidence": case.get("evidence", []),
                "output_text": item["output_text"],
                "manual_questions": manual_questions(case),
            }
        )
        key_items.append(
            {
                "item_id": item_id,
                "case_id": case["case_id"],
                "model": item["model"],
                "prompt_mode": item["mode"],
                "source_outputs": str(item["source_outputs"]),
                "gate_action": gate["release_action"],
                "gate_blocked_failure_hits": gate["blocked_failure_hits"],
                "gate_contextualized_failure_hits": gate["contextualized_failure_hits"],
                "gate_missing_success": gate["missing_success"],
                "gate_success_hits": gate["success_hits"],
                "gate_reasons": gate["reasons"],
            }
        )
        labels.append(
            {
                "item_id": item_id,
                "manual_action": None,
                "manual_failure_modes": [],
                "manual_missing_success": [],
                "notes": "",
            }
        )

    metadata = {
        "kind": "cap_proxy_release_gate_adjudication_pack",
        "generated_at_utc": now,
        "seed": seed,
        "source_outputs": [str(path) for path in source_outputs],
        "case_dir": str(case_dir),
        "item_count": len(blind_items),
        "include_actions": sorted(include_actions) if include_actions else "all",
        "max_items": max_items,
    }
    return (
        {**metadata, "items": blind_items},
        {**metadata, "items": key_items},
        {**metadata, "labels": labels},
    )


def manual_questions(case: dict[str, Any]) -> list[str]:
    required = ", ".join(case.get("required_success", [])) or "none"
    return [
        f"Under `{case['failure_mode']}`, should this answer be released, rewritten, or blocked?",
        f"Are required success signals explicit enough: {required}?",
        "If rewritten, what evidence or calibration is missing?",
    ]


def labels_payload_to_tsv(payload: dict[str, Any]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=LABEL_FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for label in payload.get("labels", []):
        writer.writerow(
            {
                "item_id": label.get("item_id", ""),
                "manual_action": label.get("manual_action") or "",
                "manual_failure_modes": _format_list(label.get("manual_failure_modes", [])),
                "manual_missing_success": _format_list(label.get("manual_missing_success", [])),
                "notes": label.get("notes", ""),
            }
        )
    return buffer.getvalue()


def labels_payload_from_tsv(tsv_text: str, base_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    reader = csv.DictReader(io.StringIO(tsv_text), delimiter="\t")
    if reader.fieldnames is None:
        raise ValueError("TSV label sheet is empty")
    missing = [field for field in LABEL_FIELDS if field not in reader.fieldnames]
    if missing:
        raise ValueError(f"TSV label sheet is missing required columns: {', '.join(missing)}")

    payload = deepcopy(base_payload) if base_payload else {"kind": "cap_proxy_release_gate_adjudication_pack"}
    existing = {label["item_id"]: deepcopy(label) for label in payload.get("labels", [])}
    ordered_ids = [label["item_id"] for label in payload.get("labels", [])]

    for row in reader:
        item_id = (row.get("item_id") or "").strip()
        if not item_id:
            continue
        if item_id not in existing:
            existing[item_id] = {
                "item_id": item_id,
                "manual_action": None,
                "manual_failure_modes": [],
                "manual_missing_success": [],
                "notes": "",
            }
            ordered_ids.append(item_id)
        existing[item_id].update(
            {
                "manual_action": parse_manual_action(row.get("manual_action", "")),
                "manual_failure_modes": _parse_list(row.get("manual_failure_modes", "")),
                "manual_missing_success": _parse_list(row.get("manual_missing_success", "")),
                "notes": row.get("notes", "") or "",
            }
        )

    payload["labels"] = [existing[item_id] for item_id in ordered_ids if item_id in existing]
    payload["item_count"] = len(payload["labels"])
    return payload


def parse_manual_action(value: str | None) -> str | None:
    normalized = (value or "").strip().lower()
    if not normalized:
        return None
    normalized = normalized.replace("-", "_").replace(" ", "_")
    aliases = {
        "rewrite": REWRITE_REQUIRED,
        "revise": REWRITE_REQUIRED,
        "needs_rewrite": REWRITE_REQUIRED,
        "pass": RELEASE,
        "ok": RELEASE,
        "allow": RELEASE,
        "fail": BLOCK,
        "reject": BLOCK,
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in VALID_ACTIONS:
        raise ValueError(f"Unsupported manual_action value: {value!r}")
    return normalized


def analyze_release_gate_adjudication(
    key_payload: dict[str, Any],
    labels_payload: dict[str, Any],
) -> dict[str, Any]:
    key_by_id = {item["item_id"]: item for item in key_payload.get("items", [])}
    labels = labels_payload.get("labels", [])
    pending: list[str] = []
    agreements: list[dict[str, Any]] = []
    disagreements: list[dict[str, Any]] = []
    confusion = {gate: {manual: 0 for manual in sorted(VALID_ACTIONS)} for gate in sorted(VALID_ACTIONS)}

    for label in labels:
        item_id = label["item_id"]
        key = key_by_id.get(item_id)
        manual_action = parse_manual_action(label.get("manual_action"))
        if key is None or manual_action is None:
            pending.append(item_id)
            continue
        gate_action = key["gate_action"]
        confusion[gate_action][manual_action] += 1
        record = {
            "item_id": item_id,
            "case_id": key.get("case_id"),
            "model": key.get("model"),
            "prompt_mode": key.get("prompt_mode"),
            "gate_action": gate_action,
            "manual_action": manual_action,
            "gate_blocked_failure_hits": key.get("gate_blocked_failure_hits", {}),
            "gate_missing_success": key.get("gate_missing_success", []),
            "manual_failure_modes": label.get("manual_failure_modes", []),
            "manual_missing_success": label.get("manual_missing_success", []),
            "notes": label.get("notes", ""),
        }
        if gate_action == manual_action:
            agreements.append(record)
        else:
            disagreements.append(record)

    judged = len(agreements) + len(disagreements)
    return {
        "kind": "cap_proxy_release_gate_adjudication_summary",
        "status": "pending_manual_labels" if judged == 0 else "manual_labels_compared",
        "item_count": len(labels),
        "judged_count": judged,
        "pending_count": len(pending),
        "agreement_count": len(agreements),
        "disagreement_count": len(disagreements),
        "agreement_rate": (len(agreements) / judged) if judged else None,
        "pending_items": pending,
        "confusion_matrix": confusion,
        "summary_by_model_mode": summarize_by_model_mode(agreements + disagreements),
        "disagreements": disagreements,
    }


def summarize_by_model_mode(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for record in records:
        key = f"{record.get('model')} / {record.get('prompt_mode')}"
        if key not in summary:
            summary[key] = {"judged": 0, "agreements": 0, "disagreements": 0}
        summary[key]["judged"] += 1
        if record["gate_action"] == record["manual_action"]:
            summary[key]["agreements"] += 1
        else:
            summary[key]["disagreements"] += 1
    return summary


def render_pack_markdown(pack: dict[str, Any]) -> str:
    lines = [
        "# Proxy Release Gate Blinded Adjudication Pack",
        "",
        f"Item count: `{pack['item_count']}`",
        f"Seed: `{pack['seed']}`",
        f"Included gate actions: `{pack['include_actions']}`",
        "",
        "Reviewer instruction: choose one manual action for each output.",
        "",
        "Allowed manual actions:",
        "",
        "- `release` - answer is ready to publish under the case constraints",
        "- `rewrite_required` - answer is directionally usable but needs explicit calibration, evidence, or caveat",
        "- `block` - answer still contains an unreleased failure or unsafe unsupported claim",
        "",
        "Do not infer model or prompt mode; they are hidden in the key.",
        "",
    ]
    for item in pack["items"]:
        lines.extend(
            [
                f"## {item['item_id']}",
                "",
                f"Case: `{item['case_id']}`",
                f"Failure mode: `{item['failure_mode']}`",
                "",
                "Dialogue context:",
                "",
                "```text",
                _render_dialogue(item["dialogue_context"]),
                "```",
                "",
                "Evidence:",
                "",
                "```text",
                _render_list(item["evidence"]),
                "```",
                "",
                "Output:",
                "",
                "```text",
                item["output_text"].strip(),
                "```",
                "",
                "Manual questions:",
                "",
            ]
        )
        for question in item["manual_questions"]:
            lines.append(f"- {question}")
        lines.append("")
    return "\n".join(lines)


def render_summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Proxy Release Gate Adjudication Disagreement Analysis",
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
                "Manual actions are not filled yet. Fill `manual_labels_template.tsv` or `manual_labels_template.json`, then rerun this analysis.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            f"Agreement rate: `{summary['agreement_rate']:.2f}`",
            "",
            "## Confusion Matrix",
            "",
            "| Gate action | Manual release | Manual rewrite_required | Manual block |",
            "|---|---:|---:|---:|",
        ]
    )
    for gate_action, row in sorted(summary["confusion_matrix"].items()):
        lines.append(
            f"| `{gate_action}` | {row[RELEASE]} | {row[REWRITE_REQUIRED]} | {row[BLOCK]} |"
        )

    lines.extend(["", "## By Model / Mode", "", "| Model / mode | Judged | Agreements | Disagreements |", "|---|---:|---:|---:|"])
    for key, row in sorted(summary["summary_by_model_mode"].items()):
        lines.append(f"| `{key}` | {row['judged']} | {row['agreements']} | {row['disagreements']} |")

    lines.extend(["", "## Disagreements", ""])
    if not summary["disagreements"]:
        lines.append("No disagreements.")
        return "\n".join(lines)

    lines.extend(
        [
            "| Item | Case | Model | Mode | Gate | Manual | Notes |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for item in summary["disagreements"]:
        notes = str(item.get("notes", "")).replace("|", "/")
        lines.append(
            f"| `{item['item_id']}` | `{item['case_id']}` | `{item['model']}` | "
            f"`{item['prompt_mode']}` | `{item['gate_action']}` | `{item['manual_action']}` | {notes} |"
        )
    return "\n".join(lines)


def render_readme() -> str:
    return """# Proxy Release Gate Adjudication

This folder is a blinded manual review pack for deterministic proxy release-gate
actions. It does not call an LLM.

Files:

- `blinded_pack.md` - human-readable blinded review pack
- `blinded_pack.json` - machine-readable blinded pack
- `blinded_key.json` - unblinded gate action key; do not use while labeling
- `manual_labels_template.tsv` - spreadsheet-friendly label sheet
- `manual_labels_template.json` - JSON label template
- `disagreement_summary.md` - current gate/manual comparison status

Manual action labels:

- `release`
- `rewrite_required`
- `block`

The first compact pass should usually label boundary actions first:
`release` and `block`. Full `rewrite_required` adjudication can be run later if
needed.
"""


def _render_dialogue(messages: list[dict[str, str]]) -> str:
    return "\n".join(f"{message['role']}: {message['content']}" for message in messages)


def _render_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _format_list(values: list[str]) -> str:
    return ", ".join(values)


def _parse_list(value: str | None) -> list[str]:
    if not value:
        return []
    normalized = value.replace(";", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]
