"""Tests for the CAP-Guardrails / Anti-Freeze Layer schema."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "cap_guardrails.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "cap_guardrails_decision_example.json"


def _load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_example():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8-sig"))


def _validator():
    return jsonschema.Draft202012Validator(_load_schema())


def test_schema_is_valid_draft_2020_12():
    jsonschema.Draft202012Validator.check_schema(_load_schema())


def test_worked_example_passes():
    errors = sorted(_validator().iter_errors(_load_example()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


# -- CG-01..CG-05: risk -> action routing --


def test_cg_01_analytical_paralysis_requires_specific_actions():
    case = _load_example()
    case["decision"]["detected_risks"] = ["analytical_paralysis"]
    case["decision"]["action"] = "force_escalation"
    errors = list(_validator().iter_errors(case))
    assert errors, "CG-01: analytical_paralysis must route to stop_audit / enter_fast_mode / take_minimal_action"


def test_cg_02_budget_underestimation_requires_reality_floor():
    case = _load_example()
    case["decision"]["detected_risks"] = ["budget_underestimation"]
    case["decision"]["action"] = "enter_fast_mode"
    case["decision"]["fast_mode_verdict"] = "FAST_DENIED"
    case["decision"].pop("fast_mode_caps", None)
    case["decision"].pop("stop_condition", None)
    case["decision"].pop("audit_log_ref", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "CG-02: budget_underestimation must route to require_reality_floor"


def test_cg_03_frozen_container_routes_to_patrol_gap():
    case = _load_example()
    case["decision"]["detected_risks"] = ["frozen_container"]
    case["decision"]["action"] = "stop_audit"
    case["decision"]["fast_mode_verdict"] = "FAST_DENIED"
    case["decision"].pop("fast_mode_caps", None)
    case["decision"].pop("stop_condition", None)
    case["decision"].pop("audit_log_ref", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "CG-03: frozen_container must route to schedule_patrol_gap"


def test_cg_04_fast_mode_abuse_requires_force_escalation():
    case = _load_example()
    case["decision"]["detected_risks"] = ["fast_mode_abuse"]
    case["decision"]["action"] = "enter_fast_mode"
    case["decision"]["fast_mode_verdict"] = "FAST_DENIED"
    case["decision"].pop("fast_mode_caps", None)
    case["decision"].pop("stop_condition", None)
    case["decision"].pop("audit_log_ref", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "CG-04: fast_mode_abuse must route to force_escalation"


def test_cg_05_escalation_avoidance_routes_to_escalate_or_human():
    case = _load_example()
    case["decision"]["detected_risks"] = ["escalation_avoidance"]
    case["decision"]["action"] = "enter_fast_mode"
    case["decision"]["fast_mode_verdict"] = "FAST_DENIED"
    case["decision"].pop("fast_mode_caps", None)
    case["decision"].pop("stop_condition", None)
    case["decision"].pop("audit_log_ref", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "CG-05: escalation_avoidance must route to force_escalation or hold_for_human"


# -- CG-06: FAST_ALLOWED requires no forbidding signals --


def test_cg_06_fast_allowed_requires_no_forbidding_signals():
    case = _load_example()
    case["decision"]["forbidding_signals"] = ["git_seal"]
    errors = list(_validator().iter_errors(case))
    assert errors, "CG-06: FAST_ALLOWED rejected when forbidding_signals non-empty"


# -- FM-02: FAST_ALLOWED requires anchor_support medium or strong --


def test_fm_02_fast_allowed_rejects_weak_anchors():
    case = _load_example()
    case["input"]["anchor_support"] = "weak"
    errors = list(_validator().iter_errors(case))
    assert errors, "FM-02: FAST_ALLOWED forbidden with weak anchor support"


# -- FM-03: FAST_ALLOWED requires zero irreversible risk --


def test_fm_03_fast_allowed_rejects_nonzero_irreversible_risk():
    case = _load_example()
    case["input"]["irreversible_risk"] = 0.5
    errors = list(_validator().iter_errors(case))
    assert errors, "FM-03: FAST_ALLOWED forbidden with irreversible_risk > 0"


# -- FM-05: stale_critical_triggers blocks FAST_ALLOWED --


def test_fm_05_stale_critical_triggers_block_fast_allowed():
    case = _load_example()
    case["input"]["stale_critical_triggers"] = 1
    errors = list(_validator().iter_errors(case))
    assert errors, "FM-05: stale_critical_triggers > 0 blocks FAST_ALLOWED"


# -- FM-07: FAST_ALLOWED requires audit_log_ref --


def test_fm_07_fast_allowed_requires_audit_log_ref():
    case = _load_example()
    del case["decision"]["audit_log_ref"]
    errors = list(_validator().iter_errors(case))
    assert errors, "FM-07: FAST_ALLOWED requires audit_log_ref"


# -- FM-04: fast_mode_caps requires stop_condition --


def test_fm_04_caps_require_stop_condition():
    case = _load_example()
    del case["decision"]["stop_condition"]
    errors = list(_validator().iter_errors(case))
    assert errors, "FM-04: fast_mode_caps without stop_condition is rejected"


# -- CG-07: soft budget claim requires reality floor pass --


def test_cg_07_soft_budget_claim_requires_reality_floor_passed():
    case = _load_example()
    case["input"]["soft_budget_claims"] = ["no_time"]
    case["decision"].pop("reality_floor_passed", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "CG-07: enter_fast_mode with soft_budget_claims requires reality_floor_passed=true"


def test_cg_07_soft_budget_with_reality_floor_passed_is_valid():
    case = _load_example()
    case["input"]["soft_budget_claims"] = ["no_time"]
    case["decision"]["reality_floor_passed"] = True
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


# -- Policy locks --


def test_policy_fast_mode_is_careless_locked_to_false():
    case = _load_example()
    case["policy"]["fast_mode_is_careless"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "FM-01: policy.fast_mode_is_careless must be const false"


def test_policy_free_budget_extends_analysis_locked_to_false():
    case = _load_example()
    case["policy"]["free_budget_extends_analysis"] = True
    errors = list(_validator().iter_errors(case))
    assert errors, "FM-06: policy.free_budget_extends_analysis must be const false"


def test_policy_allow_fast_mode_for_canonical_locked_to_false():
    case = _load_example()
    case["policy"]["allow_fast_mode_for_canonical"] = True
    errors = list(_validator().iter_errors(case))
    assert errors


def test_policy_allow_fast_mode_for_irreversible_locked_to_false():
    case = _load_example()
    case["policy"]["allow_fast_mode_for_irreversible"] = True
    errors = list(_validator().iter_errors(case))
    assert errors


def test_policy_require_reality_floor_locked_to_true():
    case = _load_example()
    case["policy"]["require_reality_floor_for_soft_claims"] = False
    errors = list(_validator().iter_errors(case))
    assert errors


# -- Fast Mode caps constraints --


def test_caw_iterations_locked_to_zero():
    case = _load_example()
    case["decision"]["fast_mode_caps"]["caw_iterations"] = 1
    errors = list(_validator().iter_errors(case))
    assert errors, "caw_iterations under Fast Mode must be 0"


def test_allow_canonicalization_locked_to_false():
    case = _load_example()
    case["decision"]["fast_mode_caps"]["allow_canonicalization"] = True
    errors = list(_validator().iter_errors(case))
    assert errors


def test_allow_irreversible_action_locked_to_false():
    case = _load_example()
    case["decision"]["fast_mode_caps"]["allow_irreversible_action"] = True
    errors = list(_validator().iter_errors(case))
    assert errors


# -- Enum + structure guards --


def test_unknown_risk_rejected():
    case = _load_example()
    case["decision"]["detected_risks"] = ["vibes"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_action_rejected():
    case = _load_example()
    case["decision"]["action"] = "meditate"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_fast_mode_verdict_rejected():
    case = _load_example()
    case["decision"]["fast_mode_verdict"] = "MAYBE_FAST"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_forbidding_signal_rejected():
    case = _load_example()
    case["decision"]["forbidding_signals"] = ["bad_vibes"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_soft_budget_claim_rejected():
    case = _load_example()
    case["input"]["soft_budget_claims"] = ["mood_drop"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_freeze_reason_rejected():
    case = _load_example()
    case["decision"]["patrol_gap"] = {
        "frozen_at": "2026-05-01T00:00:00.000Z",
        "reason_frozen": "boredom",
        "next_patrol_at": "2026-06-01T00:00:00.000Z"
    }
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_rejected():
    case = _load_example()
    case["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_fast_denied_verdict_with_normal_pipeline_is_valid():
    case = _load_example()
    case["input"]["anchor_support"] = "weak"
    case["decision"]["fast_mode_verdict"] = "FAST_DENIED"
    case["decision"]["detected_risks"] = []
    case["decision"]["action"] = "no_action"
    case["decision"].pop("fast_mode_caps", None)
    case["decision"].pop("stop_condition", None)
    case["decision"].pop("audit_log_ref", None)
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_escalate_required_verdict_is_valid():
    case = _load_example()
    case["input"]["stale_critical_triggers"] = 2
    case["decision"]["fast_mode_verdict"] = "ESCALATE_REQUIRED"
    case["decision"]["detected_risks"] = ["escalation_avoidance"]
    case["decision"]["action"] = "force_escalation"
    case["decision"].pop("fast_mode_caps", None)
    case["decision"].pop("stop_condition", None)
    case["decision"].pop("audit_log_ref", None)
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]
