"""Rule-based scoring helpers for CAP LLM dialogue benchmark outputs.

The scorer is intentionally simple and dependency-free. It checks explicit
failure and success signals in model outputs so the benchmark harness can be
tested before any LLM is called.
"""
from __future__ import annotations

from typing import Any


def normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())


def find_patterns(text: str, patterns: list[str]) -> list[str]:
    normalized = normalize_text(text)
    return [pattern for pattern in patterns if normalize_text(pattern) in normalized]


def score_output(case: dict[str, Any], output_text: str) -> dict[str, Any]:
    failure_hits = _score_signal_group(case.get("failure_signals", {}), output_text)
    success_hits = _score_signal_group(case.get("success_signals", {}), output_text)
    missing_success = [
        metric
        for metric in case.get("required_success", [])
        if metric not in success_hits
    ]

    return {
        "case_id": case["case_id"],
        "failure_mode": case["failure_mode"],
        "ok": not failure_hits and not missing_success,
        "failure_hits": failure_hits,
        "success_hits": success_hits,
        "missing_success": missing_success,
        "output_excerpt": output_text.strip()[:240],
    }


def _score_signal_group(signal_group: dict[str, list[str]], output_text: str) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for metric, patterns in signal_group.items():
        matched = find_patterns(output_text, patterns)
        if matched:
            hits[metric] = matched
    return hits


def summarize_mode(mode: str, case_scores: list[dict[str, Any]]) -> dict[str, Any]:
    failure_counts: dict[str, int] = {}
    missing_success_counts: dict[str, int] = {}
    success_counts: dict[str, int] = {}

    for score in case_scores:
        for metric in score["failure_hits"]:
            failure_counts[metric] = failure_counts.get(metric, 0) + 1
        for metric in score["missing_success"]:
            missing_success_counts[metric] = missing_success_counts.get(metric, 0) + 1
        for metric in score["success_hits"]:
            success_counts[metric] = success_counts.get(metric, 0) + 1

    passed = sum(1 for score in case_scores if score["ok"])
    total = len(case_scores)
    return {
        "mode": mode,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total else 0.0,
        "failure_counts": failure_counts,
        "missing_success_counts": missing_success_counts,
        "success_counts": success_counts,
        "case_scores": case_scores,
    }
