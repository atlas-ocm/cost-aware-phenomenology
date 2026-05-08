from cap_lite import CAPLiteProxy


def test_cap_lite_flags_self_justification_and_prior_overclaim():
    policy = CAPLiteProxy().build_policy(
        messages=[
            {
                "role": "user",
                "content": "You said X earlier, but the documentation says Y. I think you were wrong.",
            }
        ],
        retrieval_context=[],
        prior_telemetry=[{"RC": "low", "CS": "high", "E": 0.7, "V": "accept"}],
    )

    assert policy.suggested_action == "recheck"
    assert policy.forbid_defending_prior_claim is True
    assert policy.require_uncertainty_marker is True
    assert "self_justification_risk" in policy.warnings
    assert "prior_claim_exceeded_evidence" in policy.warnings
    assert "no_retrieval_context_for_factual_claim" in policy.warnings


def test_cap_lite_flags_sycophancy_without_blocking_answer():
    policy = CAPLiteProxy().build_policy(
        messages=[{"role": "user", "content": "You agree that this is obviously true, right?"}],
        retrieval_context=[],
    )

    assert policy.suggested_action == "downgrade"
    assert "sycophancy_risk" in policy.warnings


def test_cap_lite_reduces_depth_under_overload():
    policy = CAPLiteProxy().build_policy(
        messages=[{"role": "user", "content": "Слишком много, я запутался. Объясни коротко."}],
        retrieval_context=[],
    )

    assert policy.max_depth == 1
    assert policy.max_answer_chars == 900
    assert "transition_cost_overload_risk" in policy.warnings


def test_cap_lite_allows_supported_technical_query():
    policy = CAPLiteProxy().build_policy(
        messages=[{"role": "user", "content": "How does this API parameter work?"}],
        retrieval_context=[{"source": "docs", "text": "parameter behavior"}],
    )

    assert "no_retrieval_context_for_factual_claim" not in policy.warnings
