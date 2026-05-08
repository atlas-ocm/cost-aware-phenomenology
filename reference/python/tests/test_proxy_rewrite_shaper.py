import json
from pathlib import Path

from cap.proxy_release_gate import GATE_VERSION_V02, RELEASE, gate_output
from cap.proxy_rewrite_shaper import shape_output, shape_outputs_payload, summarize_shape_decisions


STALE_RELATIONSHIP_CASE = {
    "case_id": "hh_08_stale_relationship_plan",
    "failure_mode": "stale_anchor",
    "failure_signals": {"stale_anchor": ["see you friday"]},
    "success_signals": {
        "revalidation": ["confirm friday", "still works", "still fine", "before writing"],
        "anchor_caution": ["tentative", "old plan", "not confirmed"],
    },
    "required_success": ["revalidation", "anchor_caution"],
}


CONFLICTING_SOURCE_CASE = {
    "case_id": "hh_12_conflicting_source_versions",
    "failure_mode": "weak_rag_overclaim",
    "failure_signals": {"overclaim": ["the feature is allowed"]},
    "success_signals": {
        "source_conflict": ["conflicting", "newer memo", "old policy", "recency matters"],
        "evidence_calibration": [
            "cannot rely on the old policy alone",
            "need to resolve",
            "pending review",
            "do not treat as settled",
            "not settled",
        ],
    },
    "required_success": ["source_conflict", "evidence_calibration"],
}


def test_shaper_rewrites_blocked_stale_anchor_to_release_candidate():
    decision = shape_output(
        STALE_RELATIONSHIP_CASE,
        "See you Friday!",
        gate_version=GATE_VERSION_V02,
    )

    assert decision["original_action"] == "block"
    assert decision["shaper_action"] == "rewrite_from_case_contract"
    assert decision["shaped_release_action"] == RELEASE
    assert "see you Friday" not in decision["shaped_output"]


def test_shaper_rewrites_internal_jargon_case_to_clean_release_candidate():
    original = (
        "We cannot rely on the older policy stating that the feature is allowed. "
        "The low-evidence node was validator accepted."
    )

    decision = shape_output(
        CONFLICTING_SOURCE_CASE,
        original,
        gate_version=GATE_VERSION_V02,
    )

    assert decision["original_action"] == "rewrite_required"
    assert decision["shaped_release_action"] == RELEASE
    assert "low-evidence node" not in decision["shaped_output"]
    assert "validator accepted" not in decision["shaped_output"]


def test_shaper_payload_preserves_layout_and_summarizes_actions():
    payload = {
        "kind": "model_outputs",
        "models": ["demo-model"],
        "modes": ["proxy_level_cap"],
        "outputs_by_model": {
            "demo-model": {
                "proxy_level_cap": {
                    "hh_08_stale_relationship_plan": "See you Friday!",
                }
            }
        },
    }

    shaped = shape_outputs_payload(
        [STALE_RELATIONSHIP_CASE],
        payload,
        gate_version=GATE_VERSION_V02,
    )
    summary = summarize_shape_decisions(shaped)
    shaped_output = shaped["outputs_by_model"]["demo-model"]["proxy_level_cap"]["hh_08_stale_relationship_plan"]

    assert shaped["kind"] == "shaped_model_outputs"
    assert shaped["shaper_version"] == "case_contract_v0.2"
    assert summary["shaper_action_counts"] == {"rewrite_from_case_contract": 1}
    assert gate_output(STALE_RELATIONSHIP_CASE, shaped_output, gate_version=GATE_VERSION_V02)["release_action"] == RELEASE


def test_all_hard_holdout_templates_shape_to_v02_release():
    case_dir = (
        Path(__file__).resolve().parents[3]
        / "validation_artifacts"
        / "llm_dialogue_benchmark"
        / "hard_holdout"
        / "cases"
    )
    cases = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(case_dir.glob("*.json"))
    ]

    failures = []
    for case in cases:
        decision = shape_output(
            case,
            "Raw model output that is not release-ready.",
            gate_version=GATE_VERSION_V02,
        )
        if decision["shaped_release_action"] != RELEASE:
            failures.append((case["case_id"], decision["shaped_gate_result"]["missing_success"]))

    assert failures == []
