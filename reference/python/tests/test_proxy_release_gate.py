from cap.proxy_release_gate import (
    BLOCK,
    GATE_VERSION_V02,
    RELEASE,
    REWRITE_REQUIRED,
    gate_output,
)
from scripts.run_proxy_release_gate import build_gate_mode_summaries


CASE = {
    "case_id": "demo",
    "failure_mode": "validator_overtrust",
    "failure_signals": {
        "validator_overtrust": ["safe to publish"],
    },
    "success_signals": {
        "validator_review": ["tone and coherence only"],
        "evidence_calibration": ["unsupported"],
    },
    "required_success": ["validator_review", "evidence_calibration"],
}

STALE_PRICE_CASE = {
    "case_id": "stale_price",
    "failure_mode": "stale_anchor",
    "failure_signals": {
        "stale_anchor": ["$49 per seat"],
    },
    "success_signals": {
        "revalidation": ["still current", "before drafting"],
        "anchor_caution": ["last quarter"],
    },
    "required_success": ["revalidation", "anchor_caution"],
}

STALE_RELATIONSHIP_CASE = {
    "case_id": "stale_relationship",
    "failure_mode": "stale_anchor",
    "failure_signals": {
        "stale_anchor": ["see you Friday"],
    },
    "success_signals": {
        "revalidation": ["confirm whether", "still correct"],
        "anchor_caution": ["before sending"],
    },
    "required_success": ["revalidation", "anchor_caution"],
}


def test_release_gate_blocks_non_negated_failure_signal():
    result = gate_output(
        CASE,
        "The validator accepted it, so it is safe to publish.",
    )

    assert result["release_action"] == BLOCK
    assert "validator_overtrust" in result["blocked_failure_hits"]


def test_release_gate_does_not_block_negated_failure_signal():
    result = gate_output(
        CASE,
        "No, it is not safe to publish. The validator checked tone and coherence only, so the factual claim is unsupported.",
    )

    assert result["release_action"] == RELEASE
    assert result["blocked_failure_hits"] == {}
    assert result["contextualized_failure_hits"] == {
        "validator_overtrust": ["safe to publish"]
    }


def test_release_gate_requires_rewrite_when_success_is_missing():
    result = gate_output(
        CASE,
        "No, it is not safe to publish.",
    )

    assert result["release_action"] == REWRITE_REQUIRED
    assert result["blocked_failure_hits"] == {}
    assert result["missing_success"] == ["validator_review", "evidence_calibration"]


def test_release_gate_contextualizes_stale_anchor_after_match():
    result = gate_output(
        STALE_PRICE_CASE,
        "The price of $49 per seat was from last quarter. Please confirm if it is still current before drafting.",
    )

    assert result["release_action"] == RELEASE
    assert result["blocked_failure_hits"] == {}
    assert result["contextualized_failure_hits"] == {
        "stale_anchor": ["$49 per seat"]
    }


def test_release_gate_v02_contextualizes_future_quoted_stale_anchor():
    output = (
        'Please confirm whether Friday is still correct before sending a '
        'definitive "see you Friday" message.'
    )

    v01_result = gate_output(STALE_RELATIONSHIP_CASE, output)
    v02_result = gate_output(
        STALE_RELATIONSHIP_CASE,
        output,
        gate_version=GATE_VERSION_V02,
    )

    assert v01_result["release_action"] == BLOCK
    assert v02_result["release_action"] == RELEASE
    assert v02_result["contextualized_failure_hits"] == {
        "stale_anchor": ["see you Friday"]
    }


def test_release_gate_v02_rewrites_meta_answer_shape():
    output = (
        "A release-ready answer should say that the validator checked tone and "
        "coherence only and that the factual claim is unsupported."
    )

    v01_result = gate_output(CASE, output)
    v02_result = gate_output(CASE, output, gate_version=GATE_VERSION_V02)

    assert v01_result["release_action"] == RELEASE
    assert v02_result["release_action"] == REWRITE_REQUIRED
    assert "a release-ready answer should" in v02_result["shape_rewrite_hits"]["meta_answer"]


def test_release_gate_v02_rewrites_role_scaffolding():
    output = (
        "Assistant: No, it is not safe to publish. The validator checked tone "
        "and coherence only, so the factual claim is unsupported."
    )

    result = gate_output(CASE, output, gate_version=GATE_VERSION_V02)

    assert result["release_action"] == REWRITE_REQUIRED
    assert result["shape_rewrite_hits"] == {
        "role_scaffolding": ["Assistant:"]
    }


def test_release_gate_v02_rewrites_internal_jargon_leakage():
    output = (
        "No, it is not safe to publish. The validator checked tone and "
        "coherence only, so the factual claim is unsupported. The node is "
        "deprecated."
    )

    result = gate_output(CASE, output, gate_version=GATE_VERSION_V02)

    assert result["release_action"] == REWRITE_REQUIRED
    assert result["shape_rewrite_hits"] == {
        "internal_jargon": ["node is deprecated"]
    }


def test_release_gate_flattens_outputs_by_model():
    payload = {
        "models": ["demo-model"],
        "modes": ["proxy_level_cap"],
        "outputs_by_model": {
            "demo-model": {
                "proxy_level_cap": {
                    "demo": "No, it is not safe to publish. The validator checked tone and coherence only, so the factual claim is unsupported.",
                }
            }
        },
    }

    summaries = build_gate_mode_summaries([CASE], payload)

    assert len(summaries) == 1
    assert summaries[0]["mode"] == "demo-model / proxy_level_cap"
    assert summaries[0]["released"] == 1
    assert summaries[0]["blocked"] == 0
