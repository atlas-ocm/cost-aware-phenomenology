"""Tests for the Anchor Decay schema."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "spec" / "anchor_decay.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "anchor_decay_example.json"


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


def test_ad_01_fresh_requires_last_verified_at():
    case = _load_example()
    case["stage"] = "fresh"
    case["current_authority"] = "full"
    case.pop("last_verified_at", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "ADEC-01: fresh requires last_verified_at"


def test_ad_02_expired_requires_valid_until():
    case = _load_example()
    case["stage"] = "expired"
    case["current_authority"] = "none"
    case.pop("valid_until", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "ADEC-02: expired requires valid_until"


def test_ad_02_expired_with_valid_until_is_valid():
    case = _load_example()
    case["stage"] = "expired"
    case["current_authority"] = "none"
    case["valid_until"] = "2025-12-31T00:00:00.000Z"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_ad_03_deprecated_requires_superseded_by_or_reason():
    case = _load_example()
    case["stage"] = "deprecated"
    case["current_authority"] = "audit_only"
    case.pop("superseded_by", None)
    case.pop("deprecation_reason", None)
    errors = list(_validator().iter_errors(case))
    assert errors, "ADEC-03: deprecated requires superseded_by or deprecation_reason"


def test_ad_03_deprecated_with_superseded_by_is_valid():
    case = _load_example()
    case["stage"] = "deprecated"
    case["current_authority"] = "audit_only"
    case["superseded_by"] = "anchor_release_gate_policy_v02"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_ad_05_fresh_must_have_authority_full():
    case = _load_example()
    case["stage"] = "fresh"
    case["current_authority"] = "reduced"
    errors = list(_validator().iter_errors(case))
    assert errors, "ADEC-05: fresh stage must have current_authority=full"


def test_ad_05_stale_must_have_reduced_or_watch_authority():
    case = _load_example()
    case["stage"] = "stale"
    case["current_authority"] = "full"
    errors = list(_validator().iter_errors(case))
    assert errors, "ADEC-05: stale must have reduced or watch authority"


def test_ad_05_deprecated_must_have_audit_only_authority():
    case = _load_example()
    case["stage"] = "deprecated"
    case["current_authority"] = "full"
    case["superseded_by"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_ad_05_expired_must_have_authority_none():
    case = _load_example()
    case["stage"] = "expired"
    case["current_authority"] = "full"
    case["valid_until"] = "2025-01-01T00:00:00.000Z"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_ad_06_domain_volatility_required():
    case = _load_example()
    del case["domain_volatility"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_stage_rejected():
    case = _load_example()
    case["stage"] = "forever_young"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_decay_driver_rejected():
    case = _load_example()
    case["decay_drivers"] = ["time_decay"]
    errors = list(_validator().iter_errors(case))
    assert errors


def test_unknown_authority_level_rejected():
    case = _load_example()
    case["current_authority"] = "godlike"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_additional_property_rejected():
    case = _load_example()
    case["secret"] = "x"
    errors = list(_validator().iter_errors(case))
    assert errors


def test_aging_stage_with_full_authority_and_watch_is_valid():
    case = _load_example()
    case["stage"] = "aging"
    case["current_authority"] = "watch"
    errors = sorted(_validator().iter_errors(case), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]
