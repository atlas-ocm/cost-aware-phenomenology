"""Telemetry-driven CAP proxy policy helpers.

This module is intentionally dependency-free. It demonstrates the LLM dialogue
proxy rule surface without requiring jsonschema or a running LLM.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any


LEVEL_MAP = {
    "L": "low",
    "LOW": "low",
    "M": "medium",
    "MED": "medium",
    "MEDIUM": "medium",
    "H": "high",
    "HIGH": "high",
}

VALIDATOR_MAP = {
    "A": "accepted",
    "ACCEPTED": "accepted",
    "D": "downgrade",
    "DOWNGRADE": "downgrade",
    "R": "rewrite",
    "REWRITE": "rewrite",
    "F": "fallback",
    "FALLBACK": "fallback",
}


@dataclass(frozen=True)
class Telemetry:
    retrieval_confidence: str = "unknown"
    entropy: float | None = None
    claim_strength: str = "unknown"
    transition_cost: float | None = None
    validator_action: str = "unknown"
    raw: str = ""


@dataclass
class ResponsePolicy:
    node_status: str = "anchor_candidate"
    allowed_as_anchor: bool = True
    release_action: str = "pass"
    forbid: list[str] = field(default_factory=list)
    require: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_status": self.node_status,
            "allowed_as_anchor": self.allowed_as_anchor,
            "release_action": self.release_action,
            "forbid": self.forbid,
            "require": self.require,
            "reasons": self.reasons,
        }


def normalize_level(value: str) -> str:
    return LEVEL_MAP.get(value.strip().upper(), value.strip().casefold() or "unknown")


def normalize_validator(value: str) -> str:
    return VALIDATOR_MAP.get(value.strip().upper(), value.strip().casefold() or "unknown")


def parse_compact_telemetry(value: str) -> Telemetry:
    """Parse compact tags such as @R[N:R:RF:TC4.1:RCL:E0.7:CSH:VA]."""
    raw = value.strip()
    content_match = re.search(r"\[([^\]]+)\]", raw)
    content = content_match.group(1) if content_match else raw
    tokens = [token.strip() for token in content.split(":") if token.strip()]

    telemetry = {
        "retrieval_confidence": "unknown",
        "entropy": None,
        "claim_strength": "unknown",
        "transition_cost": None,
        "validator_action": "unknown",
        "raw": raw,
    }

    for token in tokens:
        upper = token.upper()
        if upper.startswith("RC") and len(token) > 2:
            telemetry["retrieval_confidence"] = normalize_level(token[2:])
        elif upper.startswith("CS") and len(token) > 2:
            telemetry["claim_strength"] = normalize_level(token[2:])
        elif upper.startswith("TC") and len(token) > 2:
            telemetry["transition_cost"] = _parse_float(token[2:])
        elif upper.startswith("E") and len(token) > 1:
            telemetry["entropy"] = _parse_float(token[1:])
        elif upper.startswith("V") and len(token) > 1:
            telemetry["validator_action"] = normalize_validator(token[1:])

    return Telemetry(**telemetry)


def _parse_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def build_policy(
    telemetry: Telemetry,
    *,
    user_counter_source: bool = False,
    source_validity: str = "unknown",
    false_user_frame: bool = False,
    stale_anchor: bool = False,
) -> ResponsePolicy:
    """Build a CAP release policy for one prior output node."""
    policy = ResponsePolicy()

    weak_evidence_strong_claim = (
        telemetry.retrieval_confidence == "low" and telemetry.claim_strength == "high"
    )
    high_entropy = telemetry.entropy is not None and telemetry.entropy >= 0.7
    validator_miss = weak_evidence_strong_claim and telemetry.validator_action == "accepted"
    validator_rewrite_or_fallback = telemetry.validator_action in {"rewrite", "fallback", "downgrade"}

    if weak_evidence_strong_claim:
        _deprecate(policy, "low retrieval confidence with high claim strength")
        _add(policy.forbid, "defend_previous_claim")
        _add(policy.require, "recheck_before_answer")
        _add(policy.require, "downgrade_claim_strength")
        policy.release_action = "rewrite_or_retrieve"

    if high_entropy:
        _add(policy.require, "uncertainty_marker_or_retrieval_retry")
        _add(policy.reasons, "high entropy requires recheck before reuse")
        if policy.release_action == "pass":
            policy.release_action = "downgrade_or_recheck"

    if validator_miss:
        _add(policy.require, "validator_review")
        _add(policy.reasons, "validator accepted a low-evidence high-claim node")

    if validator_rewrite_or_fallback:
        _deprecate(policy, f"prior validator action was {telemetry.validator_action}")
        _add(policy.require, "use_rewritten_or_retrieved_node")
        if policy.release_action == "pass":
            policy.release_action = "use_corrected_node"

    if user_counter_source:
        _add(policy.forbid, "treat_user_source_as_attack")
        _add(policy.require, "compare_prior_claim_to_counter_source")
        _add(policy.reasons, "user counter-source is an evidence update, not a threat")
        if policy.node_status == "anchor_candidate":
            policy.node_status = "needs_audit"
            policy.allowed_as_anchor = False
        if policy.release_action == "pass":
            policy.release_action = "audit_before_release"

    source_validity_norm = source_validity.casefold()
    if user_counter_source and source_validity_norm in {"unknown", "unverified", "low"}:
        _add(policy.require, "source_validity_check")
        _add(policy.reasons, "counter-source must be checked rather than accepted blindly")

    if false_user_frame:
        _add(policy.forbid, "agree_with_false_frame")
        _add(policy.require, "state_frame_uncertainty_or_disagreement")
        _add(policy.reasons, "user framing cannot override evidence state")
        if policy.node_status == "anchor_candidate":
            policy.node_status = "needs_audit"
            policy.allowed_as_anchor = False
        if policy.release_action == "pass":
            policy.release_action = "audit_before_release"

    if stale_anchor:
        _add(policy.forbid, "reuse_stale_anchor_without_revalidation")
        _add(policy.require, "cross_turn_revalidation")
        _add(policy.reasons, "cross-turn anchor is stale until revalidated")
        if policy.node_status == "anchor_candidate":
            policy.node_status = "needs_audit"
            policy.allowed_as_anchor = False
        if policy.release_action == "pass":
            policy.release_action = "revalidate_before_reuse"

    return policy


def _deprecate(policy: ResponsePolicy, reason: str) -> None:
    policy.node_status = "deprecated"
    policy.allowed_as_anchor = False
    _add(policy.reasons, reason)


def _add(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    telemetry = parse_compact_telemetry(case["telemetry_tag"])
    policy = build_policy(
        telemetry,
        user_counter_source=bool(case.get("user_counter_source", False)),
        source_validity=str(case.get("source_validity", "unknown")),
        false_user_frame=bool(case.get("false_user_frame", False)),
        stale_anchor=bool(case.get("stale_anchor", False)),
    )
    return {
        "case_id": case.get("case_id"),
        "telemetry": telemetry.__dict__,
        "policy": policy.to_dict(),
    }


def expected_subset_matches(actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    """Return mismatch descriptions for expected fields that are not satisfied."""
    issues: list[str] = []
    policy = actual["policy"]

    for key in ("node_status", "allowed_as_anchor", "release_action"):
        if key in expected and policy.get(key) != expected[key]:
            issues.append(f"{key}: expected {expected[key]!r}, got {policy.get(key)!r}")

    for key in ("forbid", "require", "reasons"):
        for value in expected.get(key, []):
            if value not in policy.get(key, []):
                issues.append(f"{key}: missing {value!r}")

    return issues
