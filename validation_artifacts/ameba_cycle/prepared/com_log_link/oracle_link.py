"""Ephemeral, packet-local oracle for cap-com-log-link-04 (driver-written, outside the tree).

Assertions come from the operator's decision of 2026-09-24: link a candidate step to a COM-Log record and the
current cycle state; inputs for the numeric gate are the COM-Log fields (operator, risk_weight_percent,
telemetry_state, allowed_total_risk_percent); active operators come from the cycle state; the RiskWeight's
source and estimate status are recorded and never become a measurement by being written down; missing inputs
never yield a positive result; a numeric PASS is not full admissibility. Run from the repository root.
"""
import copy
import json
import sys

sys.path.insert(0, "reference/python")
import jsonschema  # noqa: E402
from cap.candidate_gate import (  # noqa: E402
    RISK_WEIGHT_SOURCES,
    UNCHECKED_BY_NUMERIC_GATE,
    gate_candidate_step,
)

# 1. schema: an optional com_log_ref on a route step; everything else unchanged
schema = json.load(open("spec/adjustment_layer.schema.json", encoding="utf-8"))
example = json.load(open("examples/adjustment_candidate_transition_example.json", encoding="utf-8-sig"))
V = jsonschema.Draft202012Validator(schema)
assert not list(V.iter_errors(example)), "worked example must still validate"
ex_link = copy.deepcopy(example); ex_link["candidate"]["route"][1]["com_log_ref"] = "com_log:2026-09-24:step2"
assert not list(V.iter_errors(ex_link)), "optional com_log_ref must be accepted"
ex_bad = copy.deepcopy(example); ex_bad["candidate"]["route"][1]["extra"] = "x"
assert list(V.iter_errors(ex_bad)), "additionalProperties must still be false on a step"
ex_empty = copy.deepcopy(example); ex_empty["candidate"]["route"][1]["com_log_ref"] = ""
assert list(V.iter_errors(ex_empty)), "an empty com_log_ref must be rejected"
assert "com_log_ref" not in schema["$defs"]["adjustment_step"]["required"]

# 2. the gate record on a linked step
step = {"order": 2, "action": "apply the candidate patch", "mutability": "candidate_patch",
        "reversibility": "reversible", "reason": "r", "com_log_ref": "com_log:2026-09-24:step2"}
com = {"domain": "Work", "node": "n", "current_status": ["Open"],
       "recommended_operator": {"operator": "Fixation", "risk_weight_percent": 20},
       "target_status": ["Fixed"], "next_physical_step": "s",
       "telemetry_state": "Breach", "allowed_total_risk_percent": 45, "budget_gate": "Recovery-Only"}
assert set(RISK_WEIGHT_SOURCES) == {"engineering_default", "model_estimate", "human_estimate", "measured"}
r = gate_candidate_step(step, com, [10], "engineering_default")
assert r["verdict"] == "admissible", r
assert r["step_order"] == 2 and r["com_log_ref"] == "com_log:2026-09-24:step2"
assert r["operator"] == "Fixation" and r["risk_weight_percent"] == 20
assert r["telemetry_state"] == "Breach" and r["allowed_total_risk_percent"] == 45
assert r["active_operator_risks"] == [10]
assert r["risk_weight_source"] == "engineering_default" and r["estimate_status"] == "assigned"
assert r["numeric_pass_is_full_admissibility"] is False
assert set(UNCHECKED_BY_NUMERIC_GATE) <= set(r["unchecked"])
assert {"preconditions", "causal_alignment_with_split_point", "reversibility_under_telemetry"} <= set(r["unchecked"])

# 3. acceptance behaviours through the link
com_boundary = dict(com, recommended_operator={"operator": "Boundary", "risk_weight_percent": 20})
assert gate_candidate_step(step, com_boundary, [], "engineering_default")["verdict"] == "blocked_recovery_only"
assert gate_candidate_step(step, com, [20, 10], "engineering_default")["verdict"] == "blocked_by_budget"   # 50 > 45
assert gate_candidate_step(step, com, [20, 5], "engineering_default")["verdict"] == "admissible"          # 45 == 45

# 4. missing inputs never give a positive result
no_link = {k: v for k, v in step.items() if k != "com_log_ref"}
assert gate_candidate_step(no_link, com, [10], "engineering_default")["verdict"] == "not_computed"
assert gate_candidate_step(step, None, [10], "engineering_default")["verdict"] == "not_computed"
for missing in ("allowed_total_risk_percent", "telemetry_state", "recommended_operator"):
    com_m = {k: v for k, v in com.items() if k != missing}
    assert gate_candidate_step(step, com_m, [10], "engineering_default")["verdict"] == "not_computed", missing
assert gate_candidate_step(step, com, None, "engineering_default")["verdict"] == "not_computed"
nc = gate_candidate_step(step, None, [10], "engineering_default")
assert nc["reason"], "a not_computed record names what was missing"

# 5. provenance is recorded, never upgraded
assert gate_candidate_step(step, com, [10], "measured")["estimate_status"] == "measured"
assert gate_candidate_step(step, com, [10], "model_estimate")["estimate_status"] == "assigned"
unk = gate_candidate_step(step, com, [10], None)
assert unk["risk_weight_source"] == "unknown" and unk["estimate_status"] == "unknown"
try:
    gate_candidate_step(step, com, [10], "vibes")
except ValueError:
    pass
else:
    raise AssertionError("an unknown risk_weight_source must raise ValueError")

# 6. the non-Breach path through the link uses the same contract
com_clean = dict(com, telemetry_state="Clean", budget_gate="Allowed")
assert gate_candidate_step(step, com_clean, [], "model_estimate")["verdict"] == "admissible"
com_loaded = dict(com_clean, recommended_operator={"operator": "Inversion", "risk_weight_percent": 80}, telemetry_state="Loaded")
assert gate_candidate_step(step, com_loaded, [], "model_estimate")["verdict"] == "blocked_by_telemetry"

# 7. an invalid present value is refused, not reported as not_computed
com_bad = dict(com, recommended_operator={"operator": "Teleport", "risk_weight_percent": 20})
try:
    gate_candidate_step(step, com_bad, [10], "engineering_default")
except ValueError:
    pass
else:
    raise AssertionError("unknown operator must raise ValueError")

print("oracle_link: all assertions hold")
