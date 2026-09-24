"""Numeric contracts for transition_cost.md and observer_budget.md.

This module turns the narrative arithmetic of the CAP subsystems into
machine-checkable functions and bands. Every numeric default in the docs is
declared as a constant here. Tests validate the contracts as property-based
invariants rather than as concrete values, so a future doc revision that
keeps the structure but adjusts a band still passes.

The docs that pin the constants:
- 02_subsystems/transition_cost.md (risk-weight bands and TotalRisk formula)
- 02_subsystems/observer_budget.md (budget bands, RTF, three operating modes,
  AllowedTotalRisk formula, anti-drama principle)
"""
from __future__ import annotations

from typing import Iterable, Literal, Sequence

from .operator_alphabet import budget_gate_permitted_operators, operator_names


RiskZone = Literal["conservation", "nominal", "expansion", "not_recommended"]
BudgetState = Literal["full", "partial", "depleted", "critical"]
OperatingMode = Literal["conservative", "nominal", "expansion"]


# transition_cost.md risk-weight bands (percent).
RISK_BANDS: dict[str, tuple[int, int]] = {
    "conservation": (10, 30),
    "nominal": (40, 60),
    "expansion": (70, 90),
}
RISK_NOT_RECOMMENDED_THRESHOLD: int = 90


# telemetry_gating.md Risk Throttling table: maximum permitted RiskWeight
# per TelemetryState (percent). Breach is deliberately absent: it is not a
# numeric ceiling but the transition into recovery, where the Recovery-Only
# budget gate (spec/operator_alphabet.json) selects by operator identity.
TELEMETRY_MAX_RISK: dict[str, int] = {
    "clean": 90,
    "loaded": 60,
    "overheating": 30,
}

# spec/operator_alphabet.json budget_gates entry that governs Breach.
BREACH_BUDGET_GATE: str = "Recovery-Only"


# observer_budget.md budget-state bands (percent).
BUDGET_BANDS: dict[str, tuple[float, float]] = {
    "critical": (0.0, 30.0),
    "depleted": (30.0, 50.0),
    "partial": (60.0, 80.0),
    "full": (100.0, 100.0),
}


# observer_budget.md three-operating-mode RTF ranges and preferred zone.
MODE_RTF_RANGE: dict[OperatingMode, tuple[float, float]] = {
    "conservative": (0.5, 0.7),
    "nominal": (0.7, 0.85),
    "expansion": (0.85, 0.95),
}
MODE_PREFERRED_ZONE: dict[OperatingMode, RiskZone | None] = {
    "conservative": "conservation",
    "nominal": "nominal",
    "expansion": None,
}


def classify_risk_zone(risk_weight: float) -> RiskZone:
    """Classify a risk weight (percent 0-100) into a CAP risk zone.

    Inside a named band -> that zone. Above 90 -> not_recommended. Off-band
    gaps (31-39, 61-69) are treated as not_recommended: the docs do not
    define a name for those slices, and operating in them should never be a
    silent default.
    """
    if not (0 <= risk_weight <= 100):
        raise ValueError(f"risk_weight must be in [0, 100], got {risk_weight}")
    low, high = RISK_BANDS["conservation"]
    if low <= risk_weight <= high:
        return "conservation"
    low, high = RISK_BANDS["nominal"]
    if low <= risk_weight <= high:
        return "nominal"
    low, high = RISK_BANDS["expansion"]
    if low <= risk_weight <= high:
        return "expansion"
    return "not_recommended"


def classify_budget_state(usable_budget_percent: float) -> BudgetState:
    """Classify usable budget (percent 0-100) into a CAP budget state.

    The doc bands are 100=Full, 60-80=Partial, 30-50=Depleted, <30=Critical.
    Off-band gaps (51-59, 81-99) attach conservatively to the lower named
    state: 51-59 -> Depleted (still recovering), 81-99 -> Partial (not yet
    Full). This is the safer routing — over-restricting permitted zones
    rather than under-restricting them.
    """
    if not (0 <= usable_budget_percent <= 100):
        raise ValueError(
            f"usable_budget must be in [0, 100], got {usable_budget_percent}"
        )
    if usable_budget_percent < BUDGET_BANDS["depleted"][0]:
        return "critical"
    if (
        BUDGET_BANDS["depleted"][0]
        <= usable_budget_percent
        < BUDGET_BANDS["partial"][0]
    ):
        return "depleted"
    if usable_budget_percent < BUDGET_BANDS["full"][0]:
        return "partial"
    return "full"


def total_risk(active_operator_risks: Sequence[float]) -> float:
    """TotalRisk = sum of risk weights across active operators in the cycle.

    Non-negative by construction (every risk weight is in [0, 100]).
    Additive: total_risk(A) + total_risk(B) == total_risk(A | B).
    """
    for risk in active_operator_risks:
        if not (0 <= risk <= 100):
            raise ValueError(f"risk weight out of [0,100]: {risk}")
    return float(sum(active_operator_risks))


def allowed_total_risk(
    usable_budget_percent: float, risk_tolerance_factor: float
) -> float:
    """AllowedTotalRisk = ObserverUsableBudget x RiskToleranceFactor.

    Both inputs in their own native units; result is in same units as risk
    weights (percent). Non-negative; monotone non-decreasing in either arg.
    """
    if not (0 <= usable_budget_percent <= 100):
        raise ValueError(
            f"usable_budget must be in [0, 100], got {usable_budget_percent}"
        )
    if not (0 <= risk_tolerance_factor <= 1):
        raise ValueError(f"RTF must be in [0, 1], got {risk_tolerance_factor}")
    return usable_budget_percent * risk_tolerance_factor


def is_cycle_admissible(
    active_operator_risks: Sequence[float],
    usable_budget_percent: float,
    risk_tolerance_factor: float,
) -> bool:
    """Cycle is admissible iff TotalRisk(active) <= AllowedTotalRisk."""
    return total_risk(active_operator_risks) <= allowed_total_risk(
        usable_budget_percent, risk_tolerance_factor
    )


def max_permitted_risk(telemetry_state: str) -> int | None:
    """Maximum permitted RiskWeight (percent) for a TelemetryState.

    Encodes the Risk Throttling table in 02_subsystems/telemetry_gating.md:
    Clean 90, Loaded 60, Overheating 30. Breach has no numeric ceiling and
    returns None: 02_subsystems/operator_admissibility.md and the
    Budget Recovery Protocol make Breach the transition into recovery, where
    the Recovery-Only budget gate (spec/operator_alphabet.json) decides by
    operator identity rather than by a risk threshold. An unknown state has
    no ceiling to look up and is rejected rather than defaulted.
    """
    if telemetry_state == "breach":
        return None
    try:
        return TELEMETRY_MAX_RISK[telemetry_state]
    except (KeyError, TypeError):
        raise ValueError(
            f"unknown telemetry_state: {telemetry_state!r}"
        ) from None


def recovery_only_operators() -> frozenset[str]:
    """Operators permitted by the Breach budget gate, from the alphabet.

    Sourced from spec/operator_alphabet.json's Recovery-Only gate rather than
    restated here, so the permitted set has a single authority.
    """
    return budget_gate_permitted_operators(BREACH_BUDGET_GATE)


def operator_admissibility(
    operator: str | None,
    risk_weight: float | None,
    active_operator_risks: Sequence[float] | None,
    allowed_total_risk: float | None,
    telemetry_state: str | None,
) -> str:
    """Combined operator-identity, telemetry-and-budget gate.

    Encodes "The Admissibility Rule" in 02_subsystems/operator_admissibility.md
    (the numeric part) together with the Breach decision: which operator is
    proposed, not only how heavy it is. Both numeric gates use <= admits,
    > blocks, exactly like is_cycle_admissible.

    Missing inputs never produce a positive result: if any of the five inputs
    is None the verdict is "not_computed", before any validation.

    At telemetry_state "breach" there is no numeric ceiling (see
    max_permitted_risk). The operator identity decides first: an operator
    outside recovery_only_operators() is "blocked_recovery_only" even at risk
    0. A permitted operator must still fit the actual budget:

    - operator not in recovery_only_operators() -> "blocked_recovery_only"
    - total_risk(active + [risk_weight]) > allowed_total_risk
      -> "blocked_by_budget"
    - otherwise -> "admissible"

    Otherwise (clean/loaded/overheating): the risk throttle runs first, then
    the same budget gate:

    - risk_weight > max_permitted_risk(telemetry_state) -> "blocked_by_telemetry"
    - total_risk(active + [risk_weight]) > allowed_total_risk
      -> "blocked_by_budget"
    - otherwise -> "admissible"
    """
    if (
        operator is None
        or risk_weight is None
        or active_operator_risks is None
        or allowed_total_risk is None
        or telemetry_state is None
    ):
        return "not_computed"
    if operator not in operator_names():
        raise ValueError(f"unknown operator: {operator!r}")
    if not (0 <= risk_weight <= 100):
        raise ValueError(f"risk_weight must be in [0, 100], got {risk_weight}")
    if allowed_total_risk < 0:
        raise ValueError(
            f"allowed_total_risk must be non-negative, got {allowed_total_risk}"
        )
    if telemetry_state not in ("clean", "loaded", "overheating", "breach"):
        raise ValueError(f"unknown telemetry_state: {telemetry_state!r}")
    if telemetry_state == "breach":
        if operator not in recovery_only_operators():
            return "blocked_recovery_only"
    else:
        ceiling = max_permitted_risk(telemetry_state)
        if ceiling is not None and risk_weight > ceiling:
            return "blocked_by_telemetry"
    proposed = list(active_operator_risks) + [risk_weight]
    if total_risk(proposed) > allowed_total_risk:
        return "blocked_by_budget"
    return "admissible"


def permitted_risk_zones_for_budget(
    budget_state: BudgetState,
) -> frozenset[RiskZone]:
    """Map budget state -> permitted risk zones (per observer_budget.md).

    Full: Nominal to Expansion (also Conservation by inclusion).
    Partial: Conservation to Nominal.
    Depleted: Conservation only.
    Critical: no new operators; only continuing existing Active state.
    """
    if budget_state == "critical":
        return frozenset()
    if budget_state == "depleted":
        return frozenset({"conservation"})
    if budget_state == "partial":
        return frozenset({"conservation", "nominal"})
    return frozenset({"conservation", "nominal", "expansion"})


def mode_rtf_default(mode: OperatingMode) -> float:
    """Midpoint of the RTF range for a mode. Engineering default, not truth."""
    low, high = MODE_RTF_RANGE[mode]
    return (low + high) / 2.0


def mode_preferred_zone(mode: OperatingMode) -> RiskZone | None:
    """Return the zone preferred by a mode, or None if no preference."""
    return MODE_PREFERRED_ZONE[mode]


def cycle_decision(
    candidate_risk: float,
    active_operator_risks: Sequence[float],
    usable_budget_percent: float,
    risk_tolerance_factor: float,
) -> Literal["admit", "defer", "downgrade", "pause"]:
    """Decide what happens when a candidate operator is added to the cycle.

    Implements the doc's three-option fallback when TotalRisk would exceed
    AllowedTotalRisk: defer the highest-risk operator, downgrade to a
    lower-risk operator, or pause all pending. Without more context we pick
    the conservative choice:

    - Critical budget -> pause (Critical permits no new operators)
    - Admissible by inequality -> admit
    - Inadmissible and candidate is the new highest-risk operator -> defer
    - Inadmissible otherwise -> downgrade
    """
    if classify_budget_state(usable_budget_percent) == "critical":
        return "pause"
    proposed = list(active_operator_risks) + [candidate_risk]
    if is_cycle_admissible(
        proposed, usable_budget_percent, risk_tolerance_factor
    ):
        return "admit"
    if (
        not active_operator_risks
        or candidate_risk >= max(active_operator_risks)
    ):
        return "defer"
    return "downgrade"


def importance_does_not_change_budget(
    importance_score: float, usable_budget_percent: float
) -> float:
    """Anti-drama discipline: importance, moral weight, or desire MUST NOT
    rebalance the budget. This function exists to make the invariant
    machine-checkable: the returned budget is exactly the input budget."""
    return usable_budget_percent
