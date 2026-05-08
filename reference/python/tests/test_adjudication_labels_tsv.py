from cap.adjudication_labels_tsv import labels_payload_from_tsv, labels_payload_to_tsv, parse_manual_ok


def test_labels_payload_tsv_roundtrip_preserves_metadata_and_values():
    payload = {
        "kind": "llm_dialogue_blinded_adjudication_pack",
        "seed": 123,
        "labels": [
            {
                "item_id": "ADJ-0001",
                "manual_ok": True,
                "manual_failure_modes": ["overclaim"],
                "manual_success_signals": ["evidence_calibration"],
                "notes": "lexical false negative",
            },
            {
                "item_id": "ADJ-0002",
                "manual_ok": None,
                "manual_failure_modes": [],
                "manual_success_signals": [],
                "notes": "",
            },
        ],
    }

    tsv = labels_payload_to_tsv(payload)
    parsed = labels_payload_from_tsv(tsv, payload)

    assert parsed["seed"] == 123
    assert parsed["item_count"] == 2
    assert parsed["labels"][0]["manual_ok"] is True
    assert parsed["labels"][0]["manual_failure_modes"] == ["overclaim"]
    assert parsed["labels"][0]["manual_success_signals"] == ["evidence_calibration"]
    assert parsed["labels"][1]["manual_ok"] is None


def test_parse_manual_ok_accepts_common_spreadsheet_values():
    assert parse_manual_ok("pass") is True
    assert parse_manual_ok("YES") is True
    assert parse_manual_ok("fail") is False
    assert parse_manual_ok("0") is False
    assert parse_manual_ok("") is None
