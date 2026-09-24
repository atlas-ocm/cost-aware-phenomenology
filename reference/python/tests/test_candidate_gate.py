"""Tests for the CandidateTransition route-step to COM-Log gate link.

Covers the operator decision of 2026-09-24 (cap/candidate_gate.py): a route
step linked to one COM-Log record and the current cycle state computes the
numeric admissibility gate through that link, records the RiskWeight's source
and estimate status without upgrading an assignment to a measurement, returns
not_computed for any missing input, never returns admissible without every
input present, and marks a numeric pass as not full admissibility.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.candidate_gate import (
    RISK_WEIGHT_SOURCES,
    UNCHECKED_BY_NUMERIC_GATE,
    gate_candidate_step,
)


def _step(**overrides):
    step = {
        "order": 2,
        "action": "apply the candidate patch",
        "mutability": "candidate_patch",
        "reversibility": "reversible",
        "reason": "r",
        "com_log_ref": "com_log:2026-09-24:step2",
    }
    step.update(overrides)
    return step


def _com_log(**overrides):
    com = {
        "domain": "Work",
        "node": "n",
        "current_status": ["Open"],
        "recommended_operator": {"operator": "Fixation", "risk_weight_percent": 20},
        "target_status": ["Fixed"],
        "next_physical_step": "s",
        "telemetry_state": "Breach",
        "allowed_total_risk_percent": 45,
        "budget_gate": "Recovery-Only",
    }
    com.update(overrides)
    return com


def test_risk_weight_sources_are_the_four_named_ones():
    assert set(RISK_WEIGHT_SOURCES) == {
        "engineering_default",
        "model_estimate",
        "human_estimate",
        "measured",
    }


def test_linked_step_at_breach_is_admissible_with_provenance():
    record = gate_candidate_step(_step(), _com_log(), [10], "engineering_default")
    assert record["verdict"] == "admissible"
    assert record["step_order"] == 2
    assert record["com_log_ref"] == "com_log:2026-09-24:step2"
    assert record["operator"] == "Fixation"
    assert record["risk_weight_percent"] == 20
    assert record["telemetry_state"] == "Breach"
    assert record["allowed_total_risk_percent"] == 45
    assert record["active_operator_risks"] == [10]
    assert record["risk_weight_source"] == "engineering_default"
    assert record["estimate_status"] == "assigned"
    assert record["reason"] == ""
    assert record["numeric_pass_is_full_admissibility"] is False
    assert set(UNCHECKED_BY_NUMERIC_GATE) <= set(record["unchecked"])
    assert {
        "preconditions",
        "causal_alignment_with_split_point",
        "reversibility_under_telemetry",
    } <= set(record["unchecked"])


def test_operator_outside_recovery_only_is_blocked_at_breach():
    com = _com_log(recommended_operator={"operator": "Boundary", "risk_weight_percent": 20})
    record = gate_candidate_step(_step(), com, [], "engineering_default")
    assert record["verdict"] == "blocked_recovery_only"


def test_over_budget_is_blocked_by_budget():
    record = gate_candidate_step(_step(), _com_log(), [20, 10], "engineering_default")
    assert record["verdict"] == "blocked_by_budget"  # 20 + 30 = 50 > 45


def test_equality_admits():
    record = gate_candidate_step(_step(), _com_log(), [20, 5], "engineering_default")
    assert record["verdict"] == "admissible"  # 20 + 25 = 45 == 45


def test_missing_com_log_ref_is_not_computed_with_reason():
    step = {k: v for k, v in _step().items() if k != "com_log_ref"}
    record = gate_candidate_step(step, _com_log(), [10], "engineering_default")
    assert record["verdict"] == "not_computed"
    assert record["reason"]
    assert record["com_log_ref"] is None


def test_none_com_log_is_not_computed_with_reason():
    record = gate_candidate_step(_step(), None, [10], "engineering_default")
    assert record["verdict"] == "not_computed"
    assert record["reason"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda com: {k: v for k, v in com.items() if k != "recommended_operator"},
        lambda com: dict(
            com,
            recommended_operator={
                k: v
                for k, v in com["recommended_operator"].items()
                if k != "operator"
            },
        ),
        lambda com: dict(
            com,
            recommended_operator={
                k: v
                for k, v in com["recommended_operator"].items()
                if k != "risk_weight_percent"
            },
        ),
        lambda com: {k: v for k, v in com.items() if k != "telemetry_state"},
        lambda com: {k: v for k, v in com.items() if k != "allowed_total_risk_percent"},
    ],
)
def test_each_missing_com_log_field_is_not_computed_with_reason(mutate):
    record = gate_candidate_step(_step(), mutate(_com_log()), [10], "engineering_default")
    assert record["verdict"] == "not_computed"
    assert record["reason"]


def test_missing_active_operator_risks_is_not_computed_with_reason():
    record = gate_candidate_step(_step(), _com_log(), None, "engineering_default")
    assert record["verdict"] == "not_computed"
    assert record["reason"]
    assert record["active_operator_risks"] is None


def test_not_computed_record_still_carries_present_inputs():
    record = gate_candidate_step(_step(), _com_log(), None, "engineering_default")
    assert record["operator"] == "Fixation"
    assert record["risk_weight_percent"] == 20
    assert record["telemetry_state"] == "Breach"
    assert record["allowed_total_risk_percent"] == 45


def test_measured_source_is_estimate_status_measured():
    record = gate_candidate_step(_step(), _com_log(), [10], "measured")
    assert record["estimate_status"] == "measured"
    assert record["risk_weight_source"] == "measured"


def test_other_known_sources_are_assigned():
    for source in ("engineering_default", "model_estimate", "human_estimate"):
        record = gate_candidate_step(_step(), _com_log(), [10], source)
        assert record["estimate_status"] == "assigned", source


def test_none_source_is_unknown_and_unknown():
    record = gate_candidate_step(_step(), _com_log(), [10], None)
    assert record["risk_weight_source"] == "unknown"
    assert record["estimate_status"] == "unknown"


def test_unknown_source_raises_value_error():
    with pytest.raises(ValueError):
        gate_candidate_step(_step(), _com_log(), [10], "vibes")


def test_clean_telemetry_through_the_link_is_admissible():
    com = _com_log(telemetry_state="Clean", budget_gate="Allowed")
    record = gate_candidate_step(_step(), com, [], "model_estimate")
    assert record["verdict"] == "admissible"
    assert record["telemetry_state"] == "Clean"


def test_inversion_at_loaded_is_blocked_by_telemetry():
    com = _com_log(
        telemetry_state="Loaded",
        budget_gate="Reduced",
        recommended_operator={"operator": "Inversion", "risk_weight_percent": 80},
    )
    record = gate_candidate_step(_step(), com, [], "model_estimate")
    assert record["verdict"] == "blocked_by_telemetry"


def test_unknown_operator_in_com_log_raises_value_error():
    com = _com_log(recommended_operator={"operator": "Teleport", "risk_weight_percent": 20})
    with pytest.raises(ValueError):
        gate_candidate_step(_step(), com, [10], "engineering_default")
