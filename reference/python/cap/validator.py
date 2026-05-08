"""Full CAP validator. Runs JSON Schema + CAP-specific consistency checks."""
from __future__ import annotations

from typing import Any

from .operator_alphabet import is_risk_in_typical_range, operator_names
from .schemas import validate_com_log


def validate(com_log: dict[str, Any]) -> dict[str, Any]:
    """Full CAP validation. Returns dict with 'valid' bool and 'errors' list."""
    errors = validate_com_log(com_log)

    # Additional CAP-specific checks beyond JSON Schema
    rec = com_log.get("recommended_operator", {})
    op_name = rec.get("operator")
    risk = rec.get("risk_weight_percent")

    if op_name and risk is not None:
        if op_name not in operator_names():
            errors.append(
                f"recommended_operator.operator: '{op_name}' is not in the operator alphabet"
            )
        elif not is_risk_in_typical_range(op_name, risk):
            errors.append(
                f"recommended_operator: risk_weight {risk}% is outside typical range for {op_name}"
            )

    # Budget-gate consistency check
    if com_log.get("telemetry_state") == "Breach":
        if com_log.get("budget_gate") not in ("Recovery-Only", None):
            errors.append(
                "budget_gate: telemetry_state=Breach requires budget_gate=Recovery-Only"
            )

    return {"valid": len(errors) == 0, "errors": errors}
