"""Ephemeral, packet-local oracle for cap-admissibility-02 (driver-written, outside the tree).

Every assertion is taken from existing repository text, not from any implementation:
- 02_subsystems/telemetry_gating.md, "Risk Throttling" table: Clean 90 / Loaded 60 / Overheating 30 / Breach 0.
- 02_subsystems/operator_admissibility.md, "The Admissibility Rule": the telemetry ceiling is checked first,
  then cycle.TotalRisk + RiskWeight(operator) > AllowedTotalRisk blocks by budget.
- validation_artifacts/com_grammar/cases/cgm_03_risk_throttle_downgrade_applied.json: Inversion 80% under
  Overheating with AllowedTotalRisk 30% is blocked; Hold 10% then Fixation 20% are admissible (30 = ceiling).
- operator_admissibility.md worked example: Loaded, AllowedTotalRisk 60: Inversion 80 blocked (80 > 60);
  Fixation 25 + Boundary 35 = 60 admissible; a further 50 would exceed the budget.
- telemetry_gating.md Breach row: Pause only.
Run from the repository root. Exit 0 iff every assertion holds.
"""
import sys

sys.path.insert(0, "reference/python")
from cap.budget_calculus import (  # noqa: E402
    TELEMETRY_MAX_RISK,
    max_permitted_risk,
    operator_admissibility,
)

assert TELEMETRY_MAX_RISK == {"clean": 90, "loaded": 60, "overheating": 30, "breach": 0}, TELEMETRY_MAX_RISK
assert max_permitted_risk("clean") == 90
assert max_permitted_risk("loaded") == 60
assert max_permitted_risk("overheating") == 30
assert max_permitted_risk("breach") == 0

# cgm_03: telemetry-blocked downgrade to a two-operator sequence at the ceiling
assert operator_admissibility(80, [], 30, "overheating") == "blocked_by_telemetry"
assert operator_admissibility(10, [], 30, "overheating") == "admissible"
assert operator_admissibility(20, [10], 30, "overheating") == "admissible"
assert operator_admissibility(25, [10], 30, "overheating") == "blocked_by_budget"

# worked example: Loaded telemetry, AllowedTotalRisk 60
assert operator_admissibility(80, [], 60, "loaded") == "blocked_by_telemetry"
assert operator_admissibility(25, [], 60, "loaded") == "admissible"
assert operator_admissibility(35, [25], 60, "loaded") == "admissible"
assert operator_admissibility(50, [25, 35], 60, "loaded") == "blocked_by_budget"

# Breach: pause only
assert operator_admissibility(10, [], 30, "breach") == "blocked_by_telemetry"
assert operator_admissibility(0, [], 30, "breach") == "admissible"

# ordering: the telemetry ceiling is checked before the budget gate
assert operator_admissibility(80, [], 100, "overheating") == "blocked_by_telemetry"

# equality at the ceiling and at the budget is admissible (<=), as in the existing is_cycle_admissible
assert operator_admissibility(60, [], 60, "loaded") == "admissible"

# invalid inputs are refused, matching the module's existing ValueError discipline
for bad in ({"risk_weight": 101}, {"telemetry_state": "sunny"}, {"allowed_total_risk": -1}):
    kw = {"risk_weight": 10, "active_operator_risks": [], "allowed_total_risk": 30, "telemetry_state": "clean"}
    kw.update(bad)
    try:
        operator_admissibility(**kw)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for %r" % (bad,))

print("oracle_admissibility: all assertions hold")
