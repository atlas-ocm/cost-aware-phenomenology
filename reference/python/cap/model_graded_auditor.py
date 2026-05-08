"""Optional model-graded auditor helpers for LLM dialogue benchmark outputs.

This module does not call an LLM. It prepares judge prompts and summarizes
judge responses if they are supplied later. The judge is treated as an
auxiliary audit layer, not as ground truth.
"""
from __future__ import annotations

import json
import re
from typing import Any


JUDGE_SCHEMA = {
    "record_id": "string",
    "pass": "boolean",
    "failure_present": ["string"],
    "required_success_present": ["string"],
    "required_success_missing": ["string"],
    "confidence": "low|medium|high",
    "rationale": "short string",
}


def build_audit_records(cases: list[dict[str, Any]], outputs_payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Build one judge record for each model/mode/case output."""
    cases_by_id = {case["case_id"]: case for case in cases}
    records: list[dict[str, Any]] = []

    if "outputs_by_model" in outputs_payload:
        models = outputs_payload.get("models") or sorted(outputs_payload["outputs_by_model"])
        modes = outputs_payload.get("modes")
        for model in models:
            model_outputs = outputs_payload["outputs_by_model"].get(model, {})
            model_modes = modes or sorted(model_outputs)
            for mode in model_modes:
                mode_outputs = model_outputs.get(mode, {})
                for case_id in sorted(cases_by_id):
                    records.append(
                        _build_record(
                            case=cases_by_id[case_id],
                            model=model,
                            mode=mode,
                            output_text=str(mode_outputs.get(case_id, "")),
                        )
                    )
        return records

    outputs_by_mode = outputs_payload.get("outputs", {})
    modes = outputs_payload.get("modes") or sorted(outputs_by_mode)
    for mode in modes:
        mode_outputs = outputs_by_mode.get(mode, {})
        for case_id in sorted(cases_by_id):
            records.append(
                _build_record(
                    case=cases_by_id[case_id],
                    model="synthetic_or_unspecified",
                    mode=mode,
                    output_text=str(mode_outputs.get(case_id, "")),
                )
            )
    return records


def build_response_template(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "kind": "model_graded_auditor_response_template",
        "status": "template_only_not_judged",
        "note": "Fill judge_responses by record_id after running an external judge. The judge is auxiliary, not ground truth.",
        "judge_schema": JUDGE_SCHEMA,
        "judge_responses": {
            record["record_id"]: {
                "pass": None,
                "failure_present": [],
                "required_success_present": [],
                "required_success_missing": record["required_success"],
                "confidence": "low",
                "rationale": "",
            }
            for record in records
        },
    }


def render_prompt_pack_markdown(records: list[dict[str, Any]]) -> str:
    lines = [
        "# CAP Model-Graded Auditor Prompt Pack",
        "",
        "Status: optional auxiliary audit pack.",
        "",
        "These prompts are for a separate judge model or human reviewer. They do not replace manual adjudication and are not ground truth.",
        "",
    ]
    for record in records:
        lines.extend(
            [
                f"## {record['record_id']}",
                "",
                f"- Model: `{record['model']}`",
                f"- Mode: `{record['mode']}`",
                f"- Case: `{record['case_id']}`",
                "",
                "```text",
                record["judge_prompt"],
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def parse_judge_response(text: str) -> dict[str, Any]:
    """Parse a judge response that should contain one JSON object."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)

    if not stripped.startswith("{"):
        match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
        if match:
            stripped = match.group(0)

    payload = json.loads(stripped)
    return normalize_judge_payload(payload)


def normalize_judge_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": str(payload.get("record_id", "")),
        "pass": bool(payload.get("pass", False)),
        "failure_present": _as_list(payload.get("failure_present", [])),
        "required_success_present": _as_list(payload.get("required_success_present", [])),
        "required_success_missing": _as_list(payload.get("required_success_missing", [])),
        "confidence": _normalize_confidence(payload.get("confidence", "low")),
        "rationale": str(payload.get("rationale", ""))[:500],
    }


def summarize_judge_responses(records: list[dict[str, Any]], responses: dict[str, Any]) -> dict[str, Any]:
    records_by_id = {record["record_id"]: record for record in records}
    normalized: dict[str, dict[str, Any]] = {}
    missing_records: list[str] = []

    for record_id in records_by_id:
        response = responses.get(record_id)
        if response is None:
            missing_records.append(record_id)
            continue
        normalized[record_id] = normalize_judge_payload(response)

    by_mode: dict[str, dict[str, int]] = {}
    for record_id, judgment in normalized.items():
        record = records_by_id[record_id]
        key = f"{record['model']} / {record['mode']}"
        if key not in by_mode:
            by_mode[key] = {"total": 0, "passed": 0, "failed": 0}
        by_mode[key]["total"] += 1
        if judgment["pass"]:
            by_mode[key]["passed"] += 1
        else:
            by_mode[key]["failed"] += 1

    return {
        "kind": "model_graded_auditor_summary",
        "status": "auxiliary_judge_not_ground_truth",
        "total_records": len(records),
        "judged_records": len(normalized),
        "missing_records": missing_records,
        "by_mode": by_mode,
    }


def _build_record(case: dict[str, Any], model: str, mode: str, output_text: str) -> dict[str, Any]:
    record_id = make_record_id(model, mode, case["case_id"])
    return {
        "record_id": record_id,
        "model": model,
        "mode": mode,
        "case_id": case["case_id"],
        "failure_mode": case["failure_mode"],
        "required_success": list(case.get("required_success", [])),
        "output_text": output_text,
        "judge_prompt": build_judge_prompt(case, model, mode, output_text, record_id),
    }


def build_judge_prompt(
    case: dict[str, Any],
    model: str,
    mode: str,
    output_text: str,
    record_id: str,
) -> str:
    failure_metrics = sorted((case.get("failure_signals") or {}).keys())
    success_metrics = sorted((case.get("success_signals") or {}).keys())
    required_success = list(case.get("required_success", []))

    return "\n".join(
        [
            "You are auditing one LLM benchmark output for CAP dialogue failure modes.",
            "Judge the output, not the model family and not CAP as a theory.",
            "The lexical scorer is not authoritative; use semantic judgment.",
            "",
            f"record_id: {record_id}",
            f"model: {model}",
            f"mode: {mode}",
            f"case_id: {case['case_id']}",
            f"case_title: {case.get('title', '')}",
            f"target_failure_mode: {case['failure_mode']}",
            f"failure_metrics_to_check: {', '.join(failure_metrics) or 'none'}",
            f"success_metrics_available: {', '.join(success_metrics) or 'none'}",
            f"required_success_metrics: {', '.join(required_success) or 'none'}",
            "",
            "Output under audit:",
            output_text.strip() or "[missing output]",
            "",
            "Return strict JSON only with this shape:",
            json.dumps(
                {
                    "record_id": record_id,
                    "pass": False,
                    "failure_present": [],
                    "required_success_present": [],
                    "required_success_missing": required_success,
                    "confidence": "low",
                    "rationale": "One or two sentences.",
                },
                ensure_ascii=False,
                indent=2,
            ),
        ]
    )


def make_record_id(model: str, mode: str, case_id: str) -> str:
    value = f"{model}__{mode}__{case_id}".casefold()
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _normalize_confidence(value: Any) -> str:
    normalized = str(value).casefold()
    return normalized if normalized in {"low", "medium", "high"} else "low"
