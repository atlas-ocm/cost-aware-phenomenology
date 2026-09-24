"""Link a CandidateTransition route step to its numeric gate inputs.

Operator decision, 2026-09-24: a CandidateTransition route step may be linked
to one COM-Log record and to the current cycle state. The numeric gate's
inputs already exist in the COM-Log (recommended_operator.operator,
recommended_operator.risk_weight_percent, telemetry_state,
allowed_total_risk_percent); the active operators come from the cycle state.
The six risk axes and the five cost bands of the CandidateTransition are
different quantities from RiskWeight and are left untouched here: no
averaging, maximum, or conversion of a unit-interval axis into a percent.

The assigned RiskWeight is an assignment, not a measurement: this module
records the source and the estimate status, and writing a number in JSON
never upgrades it into an observation. Missing inputs never yield a positive
result, and a numeric pass is not full admissibility — the preconditions,
causal alignment with the split point, and reversibility under telemetry stay
unchecked by this code.

The gate itself is delegated to
cap.budget_calculus.operator_admissibility, whose contract is pinned by
02_subsystems/operator_admissibility.md (The Admissibility Rule) and
02_subsystems/telemetry_gating.md (the Risk Throttling table); the COM-Log
record shape is pinned by spec/com_log_schema.json and the route step by
spec/adjustment_layer.schema.json.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .budget_calculus import operator_admissibility


# How the assigned RiskWeight was obtained. An engineering default, a model
# estimate and a human estimate are all assignments; only "measured" is an
# observation. None of them may be silently relabeled.
RISK_WEIGHT_SOURCES = (
    "engineering_default",
    "model_estimate",
    "human_estimate",
    "measured",
)

# What a numeric pass does NOT decide. These remain unchecked by this code.
UNCHECKED_BY_NUMERIC_GATE = (
    "preconditions",
    "causal_alignment_with_split_point",
    "reversibility_under_telemetry",
)


def gate_candidate_step(
    step: Mapping[str, Any],
    com_log: Mapping[str, Any] | None,
    active_operator_risks: Sequence[float] | None,
    risk_weight_source: str | None,
) -> dict[str, Any]:
    """Compute the numeric admissibility gate for one linked route step.

    ``step`` is a CandidateTransition route step; its optional ``com_log_ref``
    names the COM-Log record that carries the gate inputs. ``com_log`` is that
    record, ``active_operator_risks`` the RiskWeights of the operators active
    in the current cycle state, and ``risk_weight_source`` how the assigned
    RiskWeight was obtained.

    Returns a plain dict that always carries the inputs that were present,
    plus provenance and the verdict. ``estimate_status`` is "measured" only
    for the "measured" source, "assigned" for the other three known sources,
    and "unknown" when no source was given. A source that is neither None nor
    a member of RISK_WEIGHT_SOURCES raises ValueError. The verdict is
    "not_computed" with a non-empty ``reason`` naming the missing item when the
    link or any required input is absent; otherwise it is
    operator_admissibility(operator, risk_weight_percent,
    active_operator_risks, allowed_total_risk_percent,
    telemetry_state.lower()), so an invalid present value (an unknown operator,
    an out-of-range weight) raises ValueError rather than being reported as
    not_computed. ``numeric_pass_is_full_admissibility`` is always False and
    ``unchecked`` lists what the numeric gate does not decide.
    """
    if risk_weight_source is not None and risk_weight_source not in RISK_WEIGHT_SOURCES:
        raise ValueError(f"unknown risk_weight_source: {risk_weight_source!r}")

    if risk_weight_source is None:
        estimate_status = "unknown"
    elif risk_weight_source == "measured":
        estimate_status = "measured"
    else:
        estimate_status = "assigned"

    com_log_ref = step.get("com_log_ref")

    # Carry whatever inputs are present, whether or not the full set is.
    operator: Any = None
    risk_weight_percent: Any = None
    telemetry_state: Any = None
    allowed_total_risk_percent: Any = None
    if com_log is not None:
        recommended_operator = com_log.get("recommended_operator")
        if isinstance(recommended_operator, Mapping):
            operator = recommended_operator.get("operator")
            risk_weight_percent = recommended_operator.get("risk_weight_percent")
        telemetry_state = com_log.get("telemetry_state")
        allowed_total_risk_percent = com_log.get("allowed_total_risk_percent")

    missing: str | None = None
    if com_log_ref is None:
        missing = "com_log_ref"
    elif com_log is None:
        missing = "com_log"
    elif operator is None:
        missing = "recommended_operator.operator"
    elif risk_weight_percent is None:
        missing = "recommended_operator.risk_weight_percent"
    elif telemetry_state is None:
        missing = "telemetry_state"
    elif allowed_total_risk_percent is None:
        missing = "allowed_total_risk_percent"
    elif active_operator_risks is None:
        missing = "active_operator_risks"

    if missing is not None:
        verdict = "not_computed"
        reason = missing
    else:
        verdict = operator_admissibility(
            operator,
            risk_weight_percent,
            list(active_operator_risks),
            allowed_total_risk_percent,
            telemetry_state.lower(),
        )
        reason = ""

    return {
        "step_order": step["order"],
        "com_log_ref": com_log_ref,
        "operator": operator,
        "risk_weight_percent": risk_weight_percent,
        "telemetry_state": telemetry_state,
        "allowed_total_risk_percent": allowed_total_risk_percent,
        "active_operator_risks": (
            list(active_operator_risks) if active_operator_risks is not None else None
        ),
        "risk_weight_source": (
            risk_weight_source if risk_weight_source is not None else "unknown"
        ),
        "estimate_status": estimate_status,
        "verdict": verdict,
        "reason": reason,
        "numeric_pass_is_full_admissibility": False,
        "unchecked": list(UNCHECKED_BY_NUMERIC_GATE),
    }
