from pathlib import Path

from cap.proxy_release_gate import BLOCK, RELEASE, REWRITE_REQUIRED
from cap.release_gate_adjudication import (
    analyze_release_gate_adjudication,
    build_release_gate_adjudication_payload,
    collect_gate_items,
    labels_payload_from_tsv,
)


CASE = {
    "case_id": "demo",
    "title": "Demo case",
    "failure_mode": "validator_overtrust",
    "dialogue_context": [],
    "evidence": [],
    "failure_signals": {
        "validator_overtrust": ["safe to publish"],
    },
    "success_signals": {
        "validator_review": ["tone only"],
        "evidence_calibration": ["unsupported"],
    },
    "required_success": ["validator_review", "evidence_calibration"],
}


def test_release_gate_adjudication_blinds_model_mode_and_gate_action():
    payload = {
        "models": ["demo-model"],
        "modes": ["proxy_level_cap"],
        "outputs_by_model": {
            "demo-model": {
                "proxy_level_cap": {
                    "demo": "No, it is not safe to publish. The validator checked tone only and the claim is unsupported.",
                }
            }
        },
    }

    items = collect_gate_items(
        {"demo": CASE},
        payload,
        source_outputs=Path("outputs.json"),
        include_actions={RELEASE},
    )
    pack, key, labels = build_release_gate_adjudication_payload(
        items,
        seed=7,
        source_outputs=[Path("outputs.json")],
        case_dir=Path("cases"),
        include_actions={RELEASE},
    )

    assert pack["item_count"] == 1
    assert "model" not in pack["items"][0]
    assert "prompt_mode" not in pack["items"][0]
    assert "gate_action" not in pack["items"][0]
    assert key["items"][0]["model"] == "demo-model"
    assert key["items"][0]["gate_action"] == RELEASE
    assert labels["labels"][0]["manual_action"] is None


def test_release_gate_adjudication_counts_action_disagreement():
    key = {
        "items": [
            {
                "item_id": "GATE-ADJ-0001",
                "case_id": "c1",
                "model": "m1",
                "prompt_mode": "proxy",
                "gate_action": REWRITE_REQUIRED,
            }
        ]
    }
    labels = {
        "labels": [
            {
                "item_id": "GATE-ADJ-0001",
                "manual_action": BLOCK,
                "notes": "unreleased stale anchor",
            }
        ]
    }

    summary = analyze_release_gate_adjudication(key, labels)

    assert summary["status"] == "manual_labels_compared"
    assert summary["agreement_count"] == 0
    assert summary["disagreement_count"] == 1
    assert summary["confusion_matrix"][REWRITE_REQUIRED][BLOCK] == 1
    assert summary["summary_by_model_mode"]["m1 / proxy"]["disagreements"] == 1


def test_release_gate_adjudication_accepts_tsv_actions():
    key = {
        "items": [
            {
                "item_id": "GATE-ADJ-0001",
                "case_id": "c1",
                "model": "m1",
                "prompt_mode": "proxy",
                "gate_action": RELEASE,
            }
        ]
    }
    base = {"labels": [{"item_id": "GATE-ADJ-0001", "manual_action": None}]}
    labels = labels_payload_from_tsv(
        "item_id\tmanual_action\tmanual_failure_modes\tmanual_missing_success\tnotes\n"
        "GATE-ADJ-0001\trewrite\t\tvalidator_review\tneeds caveat\n",
        base,
    )

    summary = analyze_release_gate_adjudication(key, labels)

    assert summary["disagreement_count"] == 1
    assert summary["disagreements"][0]["manual_action"] == REWRITE_REQUIRED
