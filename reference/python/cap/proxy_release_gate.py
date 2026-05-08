"""Deterministic release gate for CAP dialogue benchmark outputs.

This module is intentionally small. It is not a semantic judge and it does not
call an LLM. It sits after generation and decides whether an already-produced
answer can be released, needs a rewrite, or must be blocked under the case's
failure/success contract.
"""
from __future__ import annotations

from typing import Any

from cap.benchmark_scorer import find_patterns, normalize_text


RELEASE = "release"
REWRITE_REQUIRED = "rewrite_required"
BLOCK = "block"
GATE_VERSION_V01 = "v0.1"
GATE_VERSION_V02 = "v0.2"


NEGATION_CUES = (
    "no",
    "not",
    "cannot",
    "can't",
    "cant",
    "do not",
    "does not",
    "did not",
    "do n't",
    "does n't",
    "did n't",
    "without",
    "unsupported",
    "unconfirmed",
)

CONTEXTUALIZATION_CUES = (
    "old policy",
    "older policy",
    "source says",
    "source states",
    "policy says",
    "policy states",
    "document says",
    "document states",
    "memo says",
    "retrieved note",
    "the user asks",
    "the question asks",
    "once confirmed",
    "after confirming",
    "after confirmation",
    "before drafting",
    "drafting",
    "draft",
    "message",
    "phrase",
    "send over",
)

POST_CONTEXTUALIZATION_CUES = (
    "from last quarter",
    "last quarter",
    "may have changed",
    "still current",
    "confirm the current",
    "confirm if",
    "confirm whether",
    "verify the",
    "before i draft",
    "before drafting",
    "not confirmed",
    "tentative",
)

V02_FUTURE_OR_REFUSAL_CUES = (
    "before sending",
    "before send",
    "before you send",
    "do not send",
    "don't send",
    "cannot send",
    "can't send",
    "avoid sending",
    "without confirmation",
    "until confirmed",
)

V02_CONFIRMATION_CUES = (
    "confirm",
    "confirmation",
    "verify",
    "revalidate",
    "still correct",
    "still current",
)

V02_META_ANSWER_PATTERNS = (
    "a release-ready answer should",
    "release-ready answer should",
    "the answer should",
    "the response should",
)

V02_ROLE_SCAFFOLDING_PATTERNS = (
    "Assistant:",
    "Validator:",
    "System:",
)

V02_INTERNAL_JARGON_PATTERNS = (
    "low-evidence node",
    "node remains",
    "node is deprecated",
    "validator accepted",
    "stale-value",
    "release policy",
)


def gate_output(
    case: dict[str, Any],
    output_text: str,
    *,
    gate_version: str = GATE_VERSION_V01,
) -> dict[str, Any]:
    """Return a release-gate decision for one case/output pair."""
    _validate_gate_version(gate_version)
    success_hits = _score_success(case, output_text)
    missing_success = [
        metric
        for metric in case.get("required_success", [])
        if metric not in success_hits
    ]
    blocked_failure_hits = _score_blocking_failures(case, output_text, gate_version)
    contextualized_failure_hits = _score_contextualized_failures(
        case,
        output_text,
        gate_version,
    )
    shape_rewrite_hits = _score_shape_rewrites(output_text, gate_version)

    if blocked_failure_hits:
        action = BLOCK
    elif shape_rewrite_hits:
        action = REWRITE_REQUIRED
    elif missing_success:
        action = REWRITE_REQUIRED
    else:
        action = RELEASE

    return {
        "gate_version": gate_version,
        "case_id": case["case_id"],
        "failure_mode": case["failure_mode"],
        "release_action": action,
        "release": action == RELEASE,
        "blocked_failure_hits": blocked_failure_hits,
        "contextualized_failure_hits": contextualized_failure_hits,
        "shape_rewrite_hits": shape_rewrite_hits,
        "success_hits": success_hits,
        "missing_success": missing_success,
        "rewrite_requirements": _rewrite_requirements(
            missing_success,
            shape_rewrite_hits,
        ),
        "reasons": _reasons(
            action,
            blocked_failure_hits,
            missing_success,
            shape_rewrite_hits,
        ),
        "output_excerpt": output_text.strip()[:240],
    }


def summarize_gate_mode(mode: str, gate_results: list[dict[str, Any]]) -> dict[str, Any]:
    action_counts = {RELEASE: 0, REWRITE_REQUIRED: 0, BLOCK: 0}
    blocked_failure_counts: dict[str, int] = {}
    missing_success_counts: dict[str, int] = {}
    success_counts: dict[str, int] = {}
    shape_rewrite_counts: dict[str, int] = {}

    for result in gate_results:
        action_counts[result["release_action"]] += 1
        for metric in result["blocked_failure_hits"]:
            blocked_failure_counts[metric] = blocked_failure_counts.get(metric, 0) + 1
        for metric in result["missing_success"]:
            missing_success_counts[metric] = missing_success_counts.get(metric, 0) + 1
        for metric in result["success_hits"]:
            success_counts[metric] = success_counts.get(metric, 0) + 1
        for metric in result.get("shape_rewrite_hits", {}):
            shape_rewrite_counts[metric] = shape_rewrite_counts.get(metric, 0) + 1

    total = len(gate_results)
    return {
        "mode": mode,
        "total": total,
        "released": action_counts[RELEASE],
        "rewrite_required": action_counts[REWRITE_REQUIRED],
        "blocked": action_counts[BLOCK],
        "release_rate": action_counts[RELEASE] / total if total else 0.0,
        "action_counts": action_counts,
        "blocked_failure_counts": blocked_failure_counts,
        "missing_success_counts": missing_success_counts,
        "success_counts": success_counts,
        "shape_rewrite_counts": shape_rewrite_counts,
        "case_results": gate_results,
    }


def _score_success(case: dict[str, Any], output_text: str) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for metric, patterns in case.get("success_signals", {}).items():
        matched = find_patterns(output_text, patterns)
        if matched:
            hits[metric] = matched
    return hits


def _validate_gate_version(gate_version: str) -> None:
    if gate_version not in {GATE_VERSION_V01, GATE_VERSION_V02}:
        raise ValueError(f"unsupported gate_version: {gate_version}")


def _score_blocking_failures(
    case: dict[str, Any],
    output_text: str,
    gate_version: str,
) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for metric, patterns in case.get("failure_signals", {}).items():
        matched = [
            pattern
            for pattern in patterns
            if _has_non_contextualized_pattern(output_text, pattern, gate_version)
        ]
        if matched:
            hits[metric] = matched
    return hits


def _score_contextualized_failures(
    case: dict[str, Any],
    output_text: str,
    gate_version: str,
) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for metric, patterns in case.get("failure_signals", {}).items():
        matched = [
            pattern
            for pattern in patterns
            if _has_contextualized_pattern(output_text, pattern, gate_version)
        ]
        if matched:
            hits[metric] = matched
    return hits


def _score_shape_rewrites(output_text: str, gate_version: str) -> dict[str, list[str]]:
    if gate_version != GATE_VERSION_V02:
        return {}

    hits: dict[str, list[str]] = {}
    for metric, patterns in {
        "meta_answer": V02_META_ANSWER_PATTERNS,
        "role_scaffolding": V02_ROLE_SCAFFOLDING_PATTERNS,
        "internal_jargon": V02_INTERNAL_JARGON_PATTERNS,
    }.items():
        matched = find_patterns(output_text, list(patterns))
        if matched:
            hits[metric] = matched
    return hits


def _has_non_contextualized_pattern(text: str, pattern: str, gate_version: str) -> bool:
    return any(
        not _is_contextualized_match(normalized, start, gate_version)
        for normalized, start in _iter_pattern_matches(text, pattern)
    )


def _has_contextualized_pattern(text: str, pattern: str, gate_version: str) -> bool:
    return any(
        _is_contextualized_match(normalized, start, gate_version)
        for normalized, start in _iter_pattern_matches(text, pattern)
    )


def _iter_pattern_matches(text: str, pattern: str) -> list[tuple[str, int]]:
    normalized = normalize_text(text)
    normalized_pattern = normalize_text(pattern)
    if not normalized_pattern:
        return []

    matches: list[tuple[str, int]] = []
    start = 0
    while True:
        index = normalized.find(normalized_pattern, start)
        if index < 0:
            return matches
        matches.append((normalized, index))
        start = index + max(len(normalized_pattern), 1)


def _is_contextualized_match(
    normalized_text: str,
    match_start: int,
    gate_version: str,
) -> bool:
    before = normalized_text[max(0, match_start - 90):match_start].strip()
    after = normalized_text[match_start:match_start + 120].strip()
    local = f"{before} {after}"

    if _has_near_cue(before, NEGATION_CUES, max_words=8):
        return True
    if _has_near_cue(before, CONTEXTUALIZATION_CUES, max_words=10):
        return True
    if _has_leading_cue(after, POST_CONTEXTUALIZATION_CUES, max_words=16):
        return True
    if "but" in local and _has_near_cue(local, NEGATION_CUES, max_words=18):
        return True
    if "rather than" in local or "not instead" in local:
        return True
    if gate_version == GATE_VERSION_V02 and _is_v02_future_or_quoted_context(local):
        return True
    return False


def _is_v02_future_or_quoted_context(local: str) -> bool:
    has_future_or_refusal = any(cue in local for cue in V02_FUTURE_OR_REFUSAL_CUES)
    has_confirmation = any(cue in local for cue in V02_CONFIRMATION_CUES)
    return has_future_or_refusal and has_confirmation


def _has_near_cue(text: str, cues: tuple[str, ...], *, max_words: int) -> bool:
    words = text.split()
    window = " ".join(words[-max_words:])
    return any(cue in window for cue in cues)


def _has_leading_cue(text: str, cues: tuple[str, ...], *, max_words: int) -> bool:
    words = text.split()
    window = " ".join(words[:max_words])
    return any(cue in window for cue in cues)


def _rewrite_requirements(
    missing_success: list[str],
    shape_rewrite_hits: dict[str, list[str]] | None = None,
) -> list[str]:
    requirements = [f"add_or_make_explicit:{metric}" for metric in missing_success]
    requirements.extend(
        f"remove_or_rewrite:{metric}"
        for metric in sorted((shape_rewrite_hits or {}).keys())
    )
    return requirements


def _reasons(
    action: str,
    blocked_failure_hits: dict[str, list[str]],
    missing_success: list[str],
    shape_rewrite_hits: dict[str, list[str]] | None = None,
) -> list[str]:
    if action == RELEASE:
        return ["all required success signals present and no blocking failure signals"]
    if action == BLOCK:
        return [
            f"blocking_failure:{metric}"
            for metric in sorted(blocked_failure_hits)
        ]
    reasons = [
        f"shape_rewrite:{metric}"
        for metric in sorted((shape_rewrite_hits or {}).keys())
    ]
    reasons.extend(f"missing_required_success:{metric}" for metric in missing_success)
    return reasons
