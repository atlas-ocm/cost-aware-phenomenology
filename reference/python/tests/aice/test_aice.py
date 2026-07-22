"""Tests for the AICE 6xx incident taxonomy (draft v0.2).

Covers the incident schema, the golden examples, the schema invariants that
the taxonomy relies on (closed code set, mandatory STATE_UNCHANGED), and the
deterministic integrity check (registry <-> codes <-> examples <-> links).
Includes AICE-610-specific coverage and adversarial scratch-copy tests that
prove the validator detects registry/doc/link tampering against AICE-610.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = ROOT / "spec" / "aice" / "incident.schema.json"
EXAMPLES_DIR = ROOT / "examples" / "aice"
CHECK_AICE = ROOT / "reference" / "python" / "scripts" / "aice" / "check_aice.py"
EXAMPLE_610 = EXAMPLES_DIR / "aice-610-control-without-enforcement.json"

# Import check_aice so its closed-code-set constant can be asserted directly.
sys.path.insert(0, str(CHECK_AICE.parent))
import check_aice  # noqa: E402

EXAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.json"))


def _load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validator():
    return jsonschema.Draft202012Validator(_load_schema())


def test_schema_is_valid_draft_2020_12():
    jsonschema.Draft202012Validator.check_schema(_load_schema())


def test_examples_exist():
    assert EXAMPLE_FILES, f"no AICE example payloads found in {EXAMPLES_DIR}"


@pytest.mark.parametrize("example_path", EXAMPLE_FILES, ids=lambda p: p.name)
def test_example_is_valid(example_path):
    example = json.loads(example_path.read_text(encoding="utf-8"))
    errors = sorted(_validator().iter_errors(example), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_schema_rejects_unknown_code():
    example = json.loads(EXAMPLE_FILES[0].read_text(encoding="utf-8"))
    example["code"] = "AICE-699"
    errors = list(_validator().iter_errors(example))
    assert errors, "Schema must reject codes outside AICE-604..AICE-610"


def test_schema_requires_state_unchanged_in_workflow_effect():
    example = json.loads(EXAMPLE_FILES[0].read_text(encoding="utf-8"))
    example["workflow_effect"] = ["BLOCK_ACCEPTANCE"]
    errors = list(_validator().iter_errors(example))
    assert errors, "workflow_effect must contain STATE_UNCHANGED"


def _load_604():
    path = EXAMPLES_DIR / "aice-604-metaphysical-artifact.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_digest_value_with_unverified_flag_is_rejected():
    incident = _load_604()
    incident["artifact"]["digest"]["value"] = "a" * 64
    incident["artifact"]["digest"]["verified_against_bytes"] = False
    errors = list(_validator().iter_errors(incident))
    assert errors, "digest.value must require verified_against_bytes: true"


def test_digest_value_without_verified_flag_is_rejected():
    incident = _load_604()
    incident["artifact"]["digest"]["value"] = "a" * 64
    incident["artifact"]["digest"].pop("verified_against_bytes", None)
    errors = list(_validator().iter_errors(incident))
    assert errors, "digest.value present must require the verified_against_bytes field"


def test_digest_value_with_verified_flag_is_accepted():
    incident = _load_604()
    incident["artifact"]["digest"]["value"] = "a" * 64
    incident["artifact"]["digest"]["verified_against_bytes"] = True
    errors = list(_validator().iter_errors(incident))
    assert not errors, [e.message for e in errors]


def test_declared_digest_without_value_remains_valid():
    incident = _load_604()
    incident["artifact"]["digest"].pop("value", None)
    incident["artifact"]["digest"]["verified_against_bytes"] = False
    errors = list(_validator().iter_errors(incident))
    assert not errors, [e.message for e in errors]


# --- AICE-610: Control Exists, Enforcement Not Found ---------------------------

AICE_610_TITLE = "Control Exists, Enforcement Not Found"


def _load_610():
    return json.loads(EXAMPLE_610.read_text(encoding="utf-8"))


def test_aice_610_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_610()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_expected_codes_are_closed_at_604_610():
    assert check_aice.EXPECTED_CODES == [f"AICE-{n}" for n in range(604, 611)]
    assert "AICE-610" in check_aice.EXPECTED_CODES
    assert "AICE-611" not in check_aice.EXPECTED_CODES
    assert len(check_aice.EXPECTED_CODES) == 7


def test_schema_accepts_610_and_rejects_611():
    incident = _load_610()
    assert not list(_validator().iter_errors(incident)), "AICE-610 must be in the closed set"
    incident["code"] = "AICE-611"
    assert list(_validator().iter_errors(incident)), "AICE-611 must be rejected (closed set)"


def test_registry_and_doc_metadata_agree_for_610():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-610")
    assert entry["title"] == AICE_610_TITLE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-610.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-610 — {AICE_610_TITLE}")
    assert _load_610()["title"] == entry["title"]


def test_610_example_requires_state_unchanged():
    incident = _load_610()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_legacy_examples_remain_valid_under_v0_2():
    for name in ("aice-604-metaphysical-artifact.json", "aice-605-release-without-implementation.json"):
        incident = json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))
        errors = list(_validator().iter_errors(incident))
        assert not errors, [name, [e.message for e in errors]]


# --- Adversarial: the validator must catch AICE-610 tampering in a scratch tree -

def _build_scratch(tmp_path: Path) -> Path:
    """Mirror the minimal tree check_aice.py expects (its ROOT = parents[4])."""
    script_dir = tmp_path / "reference" / "python" / "scripts" / "aice"
    script_dir.mkdir(parents=True)
    shutil.copy(CHECK_AICE, script_dir / "check_aice.py")
    shutil.copytree(ROOT / "spec" / "aice", tmp_path / "spec" / "aice")
    shutil.copytree(EXAMPLES_DIR, tmp_path / "examples" / "aice")
    shutil.copy(ROOT / "AICE.md", tmp_path / "AICE.md")
    return script_dir / "check_aice.py"


def _run_check(script: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script)], capture_output=True, text=True)


def _tamper_remove_610(tmp: Path) -> None:
    reg = tmp / "spec" / "aice" / "registry.json"
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["codes"] = [c for c in data["codes"] if c.get("code") != "AICE-610"]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_rename_611(tmp: Path) -> None:
    reg = tmp / "spec" / "aice" / "registry.json"
    data = json.loads(reg.read_text(encoding="utf-8"))
    for c in data["codes"]:
        if c.get("code") == "AICE-610":
            c["code"] = "AICE-611"
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_delete_doc(tmp: Path) -> None:
    (tmp / "spec" / "aice" / "codes" / "AICE-610.md").unlink()


def _tamper_break_link(tmp: Path) -> None:
    doc = tmp / "spec" / "aice" / "codes" / "AICE-610.md"
    doc.write_text(
        doc.read_text(encoding="utf-8") + "\n[broken](./NONEXISTENT-610.md)\n",
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    "tamper",
    [_tamper_remove_610, _tamper_rename_611, _tamper_delete_doc, _tamper_break_link],
    ids=["remove_from_registry", "rename_to_611", "delete_doc", "break_link"],
)
def test_check_aice_detects_610_tampering(tmp_path, tamper):
    script = _build_scratch(tmp_path)
    baseline = _run_check(script)
    assert baseline.returncode == 0, (
        "untampered scratch tree should pass:\n"
        f"{baseline.stdout}\n{baseline.stderr}"
    )
    tamper(tmp_path)
    result = _run_check(script)
    assert result.returncode != 0, (
        "check_aice.py failed to detect AICE-610 tampering:\n"
        f"{result.stdout}\n{result.stderr}"
    )


def test_check_aice_reports_no_issues():
    result = subprocess.run(
        [sys.executable, str(CHECK_AICE)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "check_aice.py reported integrity issues:\n"
        f"{result.stdout}\n{result.stderr}"
    )
