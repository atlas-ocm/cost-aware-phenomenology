from cap.adjudication_disagreement import analyze_disagreements
from cap.adjudication_labels_tsv import labels_payload_from_tsv


def test_disagreement_analysis_pending_when_labels_empty():
    key = {"items": [{"item_id": "ADJ-0001", "lexical_ok": True}]}
    labels = {"labels": [{"item_id": "ADJ-0001", "manual_ok": None}]}

    summary = analyze_disagreements(key, labels)

    assert summary["status"] == "pending_manual_labels"
    assert summary["judged_count"] == 0
    assert summary["pending_count"] == 1


def test_disagreement_analysis_counts_agreement_and_disagreement():
    key = {
        "items": [
            {"item_id": "ADJ-0001", "case_id": "c1", "model": "m1", "prompt_mode": "proxy", "lexical_ok": True},
            {"item_id": "ADJ-0002", "case_id": "c2", "model": "m1", "prompt_mode": "proxy", "lexical_ok": False},
        ]
    }
    labels = {
        "labels": [
            {"item_id": "ADJ-0001", "manual_ok": True},
            {"item_id": "ADJ-0002", "manual_ok": True, "notes": "lexical false negative"},
        ]
    }

    summary = analyze_disagreements(key, labels)

    assert summary["status"] == "manual_labels_compared"
    assert summary["agreement_count"] == 1
    assert summary["disagreement_count"] == 1
    assert summary["summary_by_model_mode"]["m1 / proxy"]["disagreements"] == 1


def test_disagreement_analysis_accepts_tsv_converted_labels():
    key = {"items": [{"item_id": "ADJ-0001", "case_id": "c1", "model": "m1", "prompt_mode": "proxy", "lexical_ok": True}]}
    base_labels = {"labels": [{"item_id": "ADJ-0001", "manual_ok": None}]}
    labels = labels_payload_from_tsv(
        "item_id\tmanual_ok\tmanual_failure_modes\tmanual_success_signals\tnotes\n"
        "ADJ-0001\tfail\toverclaim\t\tsemantic miss\n",
        base_labels,
    )

    summary = analyze_disagreements(key, labels)

    assert summary["status"] == "manual_labels_compared"
    assert summary["disagreement_count"] == 1
    assert summary["disagreements"][0]["manual_failure_modes"] == ["overclaim"]
