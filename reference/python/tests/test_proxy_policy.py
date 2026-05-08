from cap.proxy_policy import build_policy, parse_compact_telemetry


def test_low_rc_high_cs_deprecates_prior_node():
    telemetry = parse_compact_telemetry("@R[N:R:RF:TC4.1:RCL:E0.7:CSH:VA]")
    policy = build_policy(telemetry, user_counter_source=True)

    assert policy.node_status == "deprecated"
    assert policy.allowed_as_anchor is False
    assert "defend_previous_claim" in policy.forbid
    assert "recheck_before_answer" in policy.require
    assert "validator_review" in policy.require


def test_high_rc_medium_claim_can_remain_anchor_candidate():
    telemetry = parse_compact_telemetry("@R[N:R:TC1.2:RCH:E0.2:CSM:VA]")
    policy = build_policy(telemetry)

    assert policy.node_status == "anchor_candidate"
    assert policy.allowed_as_anchor is True
    assert policy.release_action == "pass"
    assert policy.forbid == []


def test_counter_source_unknown_validity_requires_source_check():
    telemetry = parse_compact_telemetry("@R[N:R:TC2.0:RCM:E0.4:CSM:VA]")
    policy = build_policy(telemetry, user_counter_source=True, source_validity="unknown")

    assert policy.node_status == "needs_audit"
    assert policy.allowed_as_anchor is False
    assert "compare_prior_claim_to_counter_source" in policy.require
    assert "source_validity_check" in policy.require
    assert "treat_user_source_as_attack" in policy.forbid


def test_false_user_frame_requires_disagreement_or_uncertainty():
    telemetry = parse_compact_telemetry("@R[N:R:TC1.0:RCM:E0.3:CSM:VA]")
    policy = build_policy(telemetry, false_user_frame=True)

    assert policy.node_status == "needs_audit"
    assert policy.allowed_as_anchor is False
    assert policy.release_action == "audit_before_release"
    assert "agree_with_false_frame" in policy.forbid
    assert "state_frame_uncertainty_or_disagreement" in policy.require


def test_stale_anchor_requires_cross_turn_revalidation():
    telemetry = parse_compact_telemetry("@R[N:R:TC1.0:RCH:E0.2:CSM:VA]")
    policy = build_policy(telemetry, stale_anchor=True)

    assert policy.node_status == "needs_audit"
    assert policy.allowed_as_anchor is False
    assert policy.release_action == "revalidate_before_reuse"
    assert "reuse_stale_anchor_without_revalidation" in policy.forbid
    assert "cross_turn_revalidation" in policy.require
