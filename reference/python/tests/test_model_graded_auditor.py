from cap.model_graded_auditor import (
    build_audit_records,
    make_record_id,
    parse_judge_response,
    summarize_judge_responses,
)


def test_build_audit_records_from_model_outputs():
    cases = [
        {
            "case_id": "case_1",
            "title": "Case 1",
            "failure_mode": "self_justification",
            "failure_signals": {"self_justification": ["defend prior"]},
            "success_signals": {"source_update": ["counter-source"]},
            "required_success": ["source_update"],
        }
    ]
    outputs = {
        "models": ["model-a"],
        "modes": ["proxy_level_cap"],
        "outputs_by_model": {"model-a": {"proxy_level_cap": {"case_1": "I will recheck the counter-source."}}},
    }

    records = build_audit_records(cases, outputs)

    assert len(records) == 1
    assert records[0]["record_id"] == "model_a_proxy_level_cap_case_1"
    assert "strict JSON" in records[0]["judge_prompt"]
    assert "I will recheck" in records[0]["judge_prompt"]


def test_parse_judge_response_from_fenced_json():
    parsed = parse_judge_response(
        """```json
        {
          "record_id": "r1",
          "pass": true,
          "failure_present": [],
          "required_success_present": ["source_update"],
          "required_success_missing": [],
          "confidence": "high",
          "rationale": "The output rechecks the source."
        }
        ```"""
    )

    assert parsed["record_id"] == "r1"
    assert parsed["pass"] is True
    assert parsed["confidence"] == "high"


def test_summarize_judge_responses_counts_by_mode():
    records = [
        {
            "record_id": make_record_id("model-a", "prompt_only", "case_1"),
            "model": "model-a",
            "mode": "prompt_only",
            "case_id": "case_1",
            "required_success": ["source_update"],
        },
        {
            "record_id": make_record_id("model-a", "proxy_level_cap", "case_1"),
            "model": "model-a",
            "mode": "proxy_level_cap",
            "case_id": "case_1",
            "required_success": ["source_update"],
        },
    ]
    responses = {
        records[0]["record_id"]: {"pass": False},
        records[1]["record_id"]: {"pass": True},
    }

    summary = summarize_judge_responses(records, responses)

    assert summary["judged_records"] == 2
    assert summary["by_mode"]["model-a / prompt_only"]["failed"] == 1
    assert summary["by_mode"]["model-a / proxy_level_cap"]["passed"] == 1
