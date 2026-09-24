"""Ephemeral, packet-local oracle for cap-recovery-only-03 (driver-written, outside the tree).

Assertions come from: the operator's decision of 2026-09-24 (Breach = Recovery-Only, operator identity
required, missing inputs never positive, the zero-risk simplification removed); spec/operator_alphabet.json
budget_gates "Recovery-Only" ("only Fixation, Hold, Cleanup permitted"); 02_subsystems/telemetry_gating.md
(ceilings Clean 90 / Loaded 60 / Overheating 30); 02_subsystems/operator_admissibility.md (telemetry check
before budget; <= admits); validation_artifacts/com_grammar case cgm_03 and the corrected cgm_07
(Fixation 20, Hold 10, Cleanup 15 as the case's example values).
Run from the repository root. Exit 0 iff every assertion holds.
"""
import json
import sys

sys.path.insert(0, "reference/python")
from cap.budget_calculus import (  # noqa: E402
    BREACH_BUDGET_GATE,
    TELEMETRY_MAX_RISK,
    max_permitted_risk,
    operator_admissibility,
    recovery_only_operators,
)
from cap.operator_alphabet import budget_gate_permitted_operators  # noqa: E402

# 1. the Recovery-Only operator set is machine-readable in the alphabet and matches its description
alphabet = json.load(open("spec/operator_alphabet.json", encoding="utf-8"))
gate = next(g for g in alphabet["budget_gates"] if g["name"] == "Recovery-Only")
assert gate["permitted_operators"] == ["Fixation", "Hold", "Cleanup"], gate
assert budget_gate_permitted_operators("Recovery-Only") == frozenset({"Fixation", "Hold", "Cleanup"})
assert recovery_only_operators() == frozenset({"Fixation", "Hold", "Cleanup"})
assert BREACH_BUDGET_GATE == "Recovery-Only"
# other gates without a machine-readable list are refused, not guessed
try:
    budget_gate_permitted_operators("Allowed")
except ValueError:
    pass
else:
    raise AssertionError("a gate without permitted_operators must raise ValueError")

# 2. Breach has no numeric ceiling; it is a mode
assert "breach" not in TELEMETRY_MAX_RISK
assert TELEMETRY_MAX_RISK == {"clean": 90, "loaded": 60, "overheating": 30}, TELEMETRY_MAX_RISK
assert max_permitted_risk("breach") is None
assert max_permitted_risk("overheating") == 30
try:
    max_permitted_risk("sunny")
except ValueError:
    pass
else:
    raise AssertionError("unknown state must raise ValueError")

# 3. acceptance: an admissible stabilizer at Breach with enough budget passes the numeric check
assert operator_admissibility("Fixation", 20, [10], 45, "breach") == "admissible"
assert operator_admissibility("Cleanup", 15, [20, 10], 45, "breach") == "admissible"   # 45 == 45 admits

# 4. acceptance: an operator outside Recovery-Only is blocked even with a small weight
assert operator_admissibility("Boundary", 15, [], 100, "breach") == "blocked_recovery_only"
assert operator_admissibility("Inversion", 80, [], 100, "breach") == "blocked_recovery_only"
assert operator_admissibility("Reframe", 10, [], 100, "breach") == "blocked_recovery_only"

# 5. acceptance: a stabilizer over budget is blocked
assert operator_admissibility("Cleanup", 15, [20, 10], 30, "breach") == "blocked_by_budget"

# 6. acceptance: missing inputs never give a positive result
assert operator_admissibility("Fixation", 20, [10], None, "breach") == "not_computed"
assert operator_admissibility("Fixation", 20, None, 45, "breach") == "not_computed"
assert operator_admissibility("Fixation", None, [], 45, "breach") == "not_computed"
assert operator_admissibility(None, 20, [], 45, "breach") == "not_computed"
assert operator_admissibility("Fixation", 20, [], 45, None) == "not_computed"

# 7. non-Breach behaviour unchanged, now with operator identity: cgm_03 and the worked example
assert operator_admissibility("Inversion", 80, [], 30, "overheating") == "blocked_by_telemetry"
assert operator_admissibility("Hold", 10, [], 30, "overheating") == "admissible"
assert operator_admissibility("Fixation", 20, [10], 30, "overheating") == "admissible"
assert operator_admissibility("Fixation", 25, [10], 30, "overheating") == "blocked_by_budget"
assert operator_admissibility("Inversion", 80, [], 60, "loaded") == "blocked_by_telemetry"
assert operator_admissibility("Fixation", 25, [], 60, "loaded") == "admissible"
assert operator_admissibility("Boundary", 35, [25], 60, "loaded") == "admissible"
assert operator_admissibility("Break", 50, [25, 35], 60, "loaded") == "blocked_by_budget"
assert operator_admissibility("Boundary", 15, [], 100, "clean") == "admissible"      # no whitelist outside Breach
assert operator_admissibility("Inversion", 80, [], 100, "overheating") == "blocked_by_telemetry"  # ceiling before budget

# 8. the old simplification is gone: a zero-risk non-recovery operator is still blocked at Breach
assert operator_admissibility("Boundary", 0, [], 100, "breach") == "blocked_recovery_only"

# 9. invalid (present but wrong) inputs are refused with ValueError, not reported as not_computed
for bad in ({"operator": "Teleport"}, {"risk_weight": 101}, {"allowed_total_risk": -1}, {"telemetry_state": "sunny"}):
    kw = {"operator": "Fixation", "risk_weight": 20, "active_operator_risks": [],
          "allowed_total_risk": 45, "telemetry_state": "clean"}
    kw.update(bad)
    try:
        operator_admissibility(**kw)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for %r" % (bad,))

print("oracle_recovery: all assertions hold")
