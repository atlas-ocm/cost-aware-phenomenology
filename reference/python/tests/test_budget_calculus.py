"""Property-based tests for budget_calculus.

Covers the numeric contracts declared in:
- 02_subsystems/transition_cost.md (risk-weight bands, TotalRisk formula)
- 02_subsystems/observer_budget.md (budget bands, RTF, modes,
  AllowedTotalRisk formula, anti-drama)

Tests are written as invariants rather than golden values so a future
calibration of bands keeps the contract green as long as the structure
holds.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.budget_calculus import (
    BUDGET_BANDS,
    MODE_PREFERRED_ZONE,
    MODE_RTF_RANGE,
    RISK_BANDS,
    RISK_NOT_RECOMMENDED_THRESHOLD,
    allowed_total_risk,
    classify_budget_state,
    classify_risk_zone,
    cycle_decision,
    importance_does_not_change_budget,
    is_cycle_admissible,
    mode_preferred_zone,
    mode_rtf_default,
    permitted_risk_zones_for_budget,
    total_risk,
)


# -- Risk-zone classification --


@pytest.mark.parametrize("risk_weight", [10, 15, 20, 25, 30])
def test_conservation_band_classifies_as_conservation(risk_weight):
    assert classify_risk_zone(risk_weight) == "conservation"


@pytest.mark.parametrize("risk_weight", [40, 45, 50, 55, 60])
def test_nominal_band_classifies_as_nominal(risk_weight):
    assert classify_risk_zone(risk_weight) == "nominal"


@pytest.mark.parametrize("risk_weight", [70, 75, 80, 85, 90])
def test_expansion_band_classifies_as_expansion(risk_weight):
    assert classify_risk_zone(risk_weight) == "expansion"


@pytest.mark.parametrize("risk_weight", [91, 95, 99, 100])
def test_above_threshold_classifies_as_not_recommended(risk_weight):
    assert classify_risk_zone(risk_weight) == "not_recommended"


@pytest.mark.parametrize("risk_weight", [31, 35, 39, 61, 65, 69])
def test_off_band_gaps_classify_as_not_recommended(risk_weight):
    """Doc does not name 31-39 or 61-69. Treat as not_recommended rather
    than allowing a silent 5th zone."""
    assert classify_risk_zone(risk_weight) == "not_recommended"


def test_risk_zones_are_pairwise_disjoint():
    """No risk weight in [0, 100] should classify into more than one zone."""
    zones = [classify_risk_zone(rw) for rw in range(0, 101)]
    assert all(z is not None for z in zones)


def test_risk_zone_classification_is_monotone_within_a_band():
    """Sweep each band: every integer in the band returns the same zone."""
    for zone_name, (low, high) in RISK_BANDS.items():
        for rw in range(low, high + 1):
            assert classify_risk_zone(rw) == zone_name


def test_risk_weight_out_of_range_rejected():
    with pytest.raises(ValueError):
        classify_risk_zone(-1)
    with pytest.raises(ValueError):
        classify_risk_zone(101)


# -- Budget-state classification --


@pytest.mark.parametrize("budget", [0, 5, 10, 20, 29])
def test_critical_band_classifies_as_critical(budget):
    assert classify_budget_state(budget) == "critical"


@pytest.mark.parametrize("budget", [30, 35, 40, 45, 50])
def test_depleted_band_classifies_as_depleted(budget):
    assert classify_budget_state(budget) == "depleted"


@pytest.mark.parametrize("budget", [60, 65, 70, 75, 80])
def test_partial_band_classifies_as_partial(budget):
    assert classify_budget_state(budget) == "partial"


def test_full_budget_classifies_as_full():
    assert classify_budget_state(100) == "full"


def test_budget_off_band_gaps_attach_conservatively():
    """51-59 attach to Depleted (conservative, still recovering); 81-99
    attach to Partial (conservative, not yet at nominal capacity). Never
    produce a nameless state. The choice is the safer one: over-restrict
    rather than under-restrict permitted zones."""
    for b in (51, 55, 59):
        assert classify_budget_state(b) == "depleted"
    for b in (81, 90, 99):
        assert classify_budget_state(b) == "partial"


def test_budget_out_of_range_rejected():
    with pytest.raises(ValueError):
        classify_budget_state(-1)
    with pytest.raises(ValueError):
        classify_budget_state(101)


# -- TotalRisk additivity and monotonicity --


def test_total_risk_of_empty_cycle_is_zero():
    assert total_risk([]) == 0.0


def test_total_risk_is_sum_of_components():
    assert total_risk([20, 30, 50]) == pytest.approx(100.0)


def test_total_risk_additive_over_partition():
    a = [10, 20, 30]
    b = [15, 25]
    assert total_risk(a + b) == pytest.approx(total_risk(a) + total_risk(b))


def test_adding_operator_does_not_decrease_total_risk():
    rng = random.Random(42)
    for _ in range(50):
        n = rng.randint(0, 8)
        active = [rng.randint(0, 100) for _ in range(n)]
        candidate = rng.randint(0, 100)
        before = total_risk(active)
        after = total_risk(active + [candidate])
        assert after >= before


def test_total_risk_rejects_out_of_range_component():
    with pytest.raises(ValueError):
        total_risk([50, 150])


# -- AllowedTotalRisk --


def test_allowed_total_risk_formula():
    assert allowed_total_risk(80, 0.75) == pytest.approx(60.0)
    assert allowed_total_risk(100, 1.0) == pytest.approx(100.0)
    assert allowed_total_risk(0, 0.5) == pytest.approx(0.0)


def test_allowed_total_risk_monotone_in_budget():
    rtf = 0.7
    rng = random.Random(7)
    for _ in range(50):
        a, b = sorted(rng.sample(range(0, 101), 2))
        assert allowed_total_risk(a, rtf) <= allowed_total_risk(b, rtf)


def test_allowed_total_risk_monotone_in_rtf():
    budget = 80.0
    rng = random.Random(8)
    for _ in range(50):
        a, b = sorted([rng.random(), rng.random()])
        assert allowed_total_risk(budget, a) <= allowed_total_risk(budget, b)


def test_allowed_total_risk_rejects_bad_inputs():
    with pytest.raises(ValueError):
        allowed_total_risk(-1, 0.5)
    with pytest.raises(ValueError):
        allowed_total_risk(101, 0.5)
    with pytest.raises(ValueError):
        allowed_total_risk(50, 1.5)
    with pytest.raises(ValueError):
        allowed_total_risk(50, -0.1)


# -- is_cycle_admissible --


def test_admissible_when_total_risk_within_budget():
    assert is_cycle_admissible([20, 20], 100, 0.7) is True


def test_inadmissible_when_total_risk_exceeds_budget():
    assert is_cycle_admissible([60, 60], 50, 0.5) is False


def test_admissibility_boundary_equality_passes():
    """TotalRisk == AllowedTotalRisk satisfies <= and so is admissible."""
    assert is_cycle_admissible([50.0], 100.0, 0.5) is True


# -- Mode RTF and preferred zone --


@pytest.mark.parametrize("mode", ["conservative", "nominal", "expansion"])
def test_mode_rtf_default_in_range(mode):
    low, high = MODE_RTF_RANGE[mode]
    default = mode_rtf_default(mode)
    assert low <= default <= high


def test_mode_rtf_ranges_progress_monotonically():
    """Conservative -> Nominal -> Expansion modes have non-decreasing
    RTF bands."""
    assert MODE_RTF_RANGE["conservative"][1] <= MODE_RTF_RANGE["nominal"][1]
    assert MODE_RTF_RANGE["nominal"][1] <= MODE_RTF_RANGE["expansion"][1]


def test_mode_preferred_zone_matches_doc():
    assert mode_preferred_zone("conservative") == "conservation"
    assert mode_preferred_zone("nominal") == "nominal"
    assert mode_preferred_zone("expansion") is None


# -- Permitted risk zones for budget --


def test_critical_budget_permits_no_new_operators():
    assert permitted_risk_zones_for_budget("critical") == frozenset()


def test_depleted_budget_permits_only_conservation():
    assert permitted_risk_zones_for_budget("depleted") == frozenset(
        {"conservation"}
    )


def test_partial_budget_excludes_expansion():
    permitted = permitted_risk_zones_for_budget("partial")
    assert "expansion" not in permitted
    assert "conservation" in permitted
    assert "nominal" in permitted


def test_full_budget_permits_all_named_zones():
    assert permitted_risk_zones_for_budget("full") == frozenset(
        {"conservation", "nominal", "expansion"}
    )


def test_permitted_zones_widen_monotonically_as_budget_recovers():
    """As budget recovers from Critical -> Depleted -> Partial -> Full, the
    permitted-zone set never shrinks."""
    states = ["critical", "depleted", "partial", "full"]
    previous: frozenset[str] = frozenset()
    for state in states:
        current = permitted_risk_zones_for_budget(state)
        assert previous <= current, f"shrunk at {state}"
        previous = current


# -- Cycle decision --


def test_cycle_decision_admits_when_within_budget():
    assert cycle_decision(20, [10, 20], 100, 0.7) == "admit"


def test_cycle_decision_pauses_when_critical():
    assert cycle_decision(10, [], 20, 0.7) == "pause"


def test_cycle_decision_defers_highest_risk_candidate():
    """When candidate is the new highest-risk operator and inadmissible,
    the doc's first option is defer."""
    assert cycle_decision(90, [20, 30], 50, 0.5) == "defer"


def test_cycle_decision_downgrades_when_candidate_is_not_highest():
    """Candidate is not the new top; inadmissible -> downgrade."""
    assert cycle_decision(15, [40, 50, 60], 50, 0.5) == "downgrade"


# -- Anti-drama: importance does not modify budget --


def test_importance_does_not_increase_budget():
    """Anti-drama discipline: a high-importance score must not raise the
    usable-budget input."""
    rng = random.Random(11)
    for _ in range(50):
        budget = rng.uniform(0, 100)
        importance = rng.uniform(0, 1)
        assert importance_does_not_change_budget(importance, budget) == budget


# -- Smoke: doc constants are well-formed --


def test_risk_bands_are_well_ordered():
    cons_low, cons_high = RISK_BANDS["conservation"]
    nom_low, nom_high = RISK_BANDS["nominal"]
    exp_low, exp_high = RISK_BANDS["expansion"]
    assert cons_low <= cons_high < nom_low <= nom_high < exp_low <= exp_high
    assert exp_high <= RISK_NOT_RECOMMENDED_THRESHOLD


def test_budget_bands_are_well_ordered():
    crit_low, crit_high = BUDGET_BANDS["critical"]
    dep_low, dep_high = BUDGET_BANDS["depleted"]
    par_low, par_high = BUDGET_BANDS["partial"]
    full_low, full_high = BUDGET_BANDS["full"]
    assert crit_low <= crit_high <= dep_low <= dep_high
    assert dep_high <= par_low <= par_high <= full_low <= full_high
