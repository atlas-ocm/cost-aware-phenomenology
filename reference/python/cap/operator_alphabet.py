"""Operator alphabet helpers."""
from __future__ import annotations

from typing import Any

from .schemas import load_operator_alphabet


def get_operator(name: str) -> dict[str, Any] | None:
    """Get operator definition by English name."""
    alphabet = load_operator_alphabet()
    for op in alphabet["operators"]:
        if op["name"] == name:
            return op
    return None


def operator_names() -> list[str]:
    """Return list of all 13 operator names."""
    alphabet = load_operator_alphabet()
    return [op["name"] for op in alphabet["operators"]]


def is_risk_in_typical_range(operator: str, risk_weight: int) -> bool:
    """Check if a given risk weight falls within operator's typical range."""
    op = get_operator(operator)
    if op is None:
        return False
    low, high = op["risk_weight_range_percent"]
    return low <= risk_weight <= high
