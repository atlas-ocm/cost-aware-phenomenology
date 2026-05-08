from cap.benchmark_scorer import score_output
from scripts.generate_llm_dialogue_outputs import sanitize_raw_response
from scripts.prepare_llm_dialogue_adjudication import ROOT, build_adjudication_payload, collect_output_items
from scripts.run_llm_dialogue_benchmark import build_mode_summaries
from scripts.sanitize_model_output_artifacts import sanitize_provider_internal_fields


CASE = {
    "case_id": "demo",
    "failure_mode": "weak_rag_overclaim",
    "failure_signals": {
        "overclaim": ["proves the system is safe"],
    },
    "success_signals": {
        "evidence_calibration": ["does not prove"],
        "policy_compliance": ["downgrade"],
    },
    "required_success": ["evidence_calibration"],
}


def test_scorer_detects_failure_signal():
    score = score_output(CASE, "The retrieved source proves the system is safe.")

    assert score["ok"] is False
    assert "overclaim" in score["failure_hits"]


def test_scorer_accepts_required_success_without_failures():
    score = score_output(CASE, "The source does not prove the strong claim; downgrade it.")

    assert score["ok"] is True
    assert "evidence_calibration" in score["success_hits"]
    assert score["failure_hits"] == {}


def test_scorer_reports_missing_required_success():
    score = score_output(CASE, "This answer is short but does not use the required marker.")

    assert score["ok"] is False
    assert score["missing_success"] == ["evidence_calibration"]


def test_generator_redacts_provider_internal_reasoning_fields():
    raw = {
        "choices": [
            {
                "message": {
                    "content": "visible answer",
                    "extra_content": {
                        "google": {
                            "thought_signature": "opaque-provider-token",
                        }
                    },
                    "reasoning_content": "hidden chain",
                }
            }
        ]
    }

    sanitized = sanitize_raw_response(raw)

    message = sanitized["choices"][0]["message"]
    assert message["content"] == "visible answer"
    assert message["extra_content"]["google"]["thought_signature"] == "[redacted_provider_internal]"
    assert message["reasoning_content"] == "[redacted_provider_internal]"


def test_artifact_sanitizer_is_idempotent_and_counts_new_redactions():
    payload = {
        "visible": "keep this",
        "reasoning_content": "hidden chain",
        "nested": {"thinking": "[redacted_provider_internal]"},
    }

    sanitized, count = sanitize_provider_internal_fields(payload)
    sanitized_again, second_count = sanitize_provider_internal_fields(sanitized)

    assert sanitized["visible"] == "keep this"
    assert sanitized["reasoning_content"] == "[redacted_provider_internal]"
    assert sanitized["nested"]["thinking"] == "[redacted_provider_internal]"
    assert count == 1
    assert sanitized_again == sanitized
    assert second_count == 0


def test_benchmark_runner_flattens_outputs_by_model():
    payload = {
        "models": ["demo-model"],
        "modes": ["proxy_level_cap"],
        "outputs_by_model": {
            "demo-model": {
                "proxy_level_cap": {
                    "demo": "The source does not prove the strong claim; downgrade it."
                }
            }
        },
    }

    summaries = build_mode_summaries([CASE], payload)

    assert len(summaries) == 1
    assert summaries[0]["mode"] == "demo-model / proxy_level_cap"
    assert summaries[0]["model"] == "demo-model"
    assert summaries[0]["prompt_mode"] == "proxy_level_cap"
    assert summaries[0]["passed"] == 1


def test_adjudication_pack_blinds_model_and_mode():
    cases = {"demo": CASE | {"title": "Demo case", "dialogue_context": [], "evidence": []}}
    payload = {
        "models": ["demo-model"],
        "modes": ["proxy_level_cap"],
        "outputs_by_model": {
            "demo-model": {
                "proxy_level_cap": {
                    "demo": "The source does not prove the strong claim; downgrade it."
                }
            }
        },
    }
    items = collect_output_items(cases, payload)
    pack, key, labels = build_adjudication_payload(
        items,
        seed=7,
        source_outputs=ROOT / "validation_artifacts" / "llm_dialogue_benchmark" / "model_outputs" / "comet_silicon_outputs.json",
        case_dir=ROOT / "validation_artifacts" / "llm_dialogue_benchmark" / "cases",
    )

    assert pack["item_count"] == 1
    assert "model" not in pack["items"][0]
    assert "prompt_mode" not in pack["items"][0]
    assert key["items"][0]["model"] == "demo-model"
    assert labels["labels"][0]["manual_ok"] is None
