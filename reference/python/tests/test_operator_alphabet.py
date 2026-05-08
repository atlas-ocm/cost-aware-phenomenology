"""Tests for the operator alphabet."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.operator_alphabet import get_operator, is_risk_in_typical_range, operator_names


def test_thirteen_operators():
    names = operator_names()
    assert len(names) == 13


def test_known_operators_present():
    for name in [
        "Fixation",
        "Inversion",
        "Break",
        "Hold",
        "Pump",
        "Transfer",
        "Closure",
        "Boundary",
        "Cleanup",
        "Reframe",
        "Compression",
        "Separation",
        "Return",
    ]:
        assert get_operator(name) is not None, f"Missing operator: {name}"


def test_risk_in_range():
    assert is_risk_in_typical_range("Fixation", 15) is True
    assert is_risk_in_typical_range("Fixation", 80) is False
    assert is_risk_in_typical_range("Inversion", 75) is True
