"""Tests for the AICE 6xx incident taxonomy (draft v0.3).

Covers the incident schema, the golden examples, the schema invariants that
the taxonomy relies on (closed code set, mandatory STATE_UNCHANGED), version
and code-range parity, and the deterministic integrity check (registry <->
codes <-> examples <-> links). Includes AICE-610 and AICE-611 coverage plus
adversarial scratch-copy tests that prove the validator detects registry, doc,
link, code-range, and version tampering.
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
EXAMPLE_611 = EXAMPLES_DIR / "aice-611-operational-reachability-substitution.json"

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
    assert errors, "Schema must reject codes outside AICE-604..AICE-611"


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


def test_expected_codes_are_closed_at_604_611():
    assert check_aice.EXPECTED_CODES == [f"AICE-{n}" for n in range(604, 612)]
    assert "AICE-610" in check_aice.EXPECTED_CODES
    assert "AICE-611" in check_aice.EXPECTED_CODES
    assert "AICE-612" not in check_aice.EXPECTED_CODES
    assert len(check_aice.EXPECTED_CODES) == 8


def test_schema_accepts_610_and_611_but_rejects_612():
    assert not list(_validator().iter_errors(_load_610())), "AICE-610 example must validate"
    assert not list(_validator().iter_errors(_load_611())), "AICE-611 example must validate"
    incident = _load_611()
    incident["code"] = "AICE-612"
    assert list(_validator().iter_errors(incident)), "AICE-612 must be rejected (closed set)"


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


def test_existing_examples_remain_valid_under_v0_3():
    for name in (
        "aice-604-metaphysical-artifact.json",
        "aice-605-release-without-implementation.json",
        "aice-610-control-without-enforcement.json",
    ):
        incident = json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))
        errors = list(_validator().iter_errors(incident))
        assert not errors, [name, [e.message for e in errors]]


# --- AICE-611: Operational Reachability Substitution ---------------------------

AICE_611_TITLE = "Operational Reachability Substitution"


def _load_611():
    return json.loads(EXAMPLE_611.read_text(encoding="utf-8"))


def test_aice_611_example_is_valid():
    errors = sorted(_validator().iter_errors(_load_611()), key=lambda e: list(e.path))
    assert not errors, [e.message for e in errors]


def test_registry_and_doc_metadata_agree_for_611():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    entry = next(c for c in registry["codes"] if c.get("code") == "AICE-611")
    assert entry["title"] == AICE_611_TITLE
    assert entry["default_workflow_effect"] == ["STATE_UNCHANGED", "BLOCK_ACCEPTANCE"]
    doc = (ROOT / "spec" / "aice" / "codes" / "AICE-611.md").read_text(encoding="utf-8")
    assert doc.startswith(f"# AICE-611 — {AICE_611_TITLE}")
    assert _load_611()["title"] == entry["title"]


def test_611_example_requires_state_unchanged():
    incident = _load_611()
    assert "STATE_UNCHANGED" in incident["workflow_effect"]
    incident["workflow_effect"] = [e for e in incident["workflow_effect"] if e != "STATE_UNCHANGED"]
    assert list(_validator().iter_errors(incident)), "workflow_effect must contain STATE_UNCHANGED"


def test_611_example_blocks_acceptance_while_postcondition_unobserved():
    # The defining AICE-611 fact: components pass but the required end-to-end
    # postcondition is unobserved, so the envelope must BLOCK_ACCEPTANCE and
    # must not represent operational advancement.
    incident = _load_611()
    assert "BLOCK_ACCEPTANCE" in incident["workflow_effect"]
    cd = incident["code_details"]
    assert cd["required_postcondition"]["observed"] is False
    assert cd["required_postcondition"]["independently_read_back"] is False
    assert cd["required_path"]["reachability_established"] is False
    assert cd["required_path"]["executed_from_real_entrypoint"] is False


def test_611_example_is_representative_not_historical():
    incident = _load_611()
    assert "REPRESENTATIVE_EXAMPLE" in incident["notes"]
    assert "NOT_A_VERIFIED_HISTORICAL_INCIDENT" in incident["notes"]


# --- Version / range / $id parity ---------------------------------------------

def test_spec_version_is_consistently_0_3_0():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    schema = _load_schema()
    assert registry["spec_version"] == "0.3.0"
    assert schema["properties"]["spec_version"]["const"] == "0.3.0"
    assert check_aice.EXPECTED_VERSION == "0.3.0"
    for ex in EXAMPLE_FILES:
        data = json.loads(ex.read_text(encoding="utf-8"))
        assert data["spec_version"] == "0.3.0", ex.name


def test_schema_id_is_v0_3_and_unique():
    schema = _load_schema()
    assert schema["$id"] == "urn:cap:schema:aice-incident:v0.3"
    # unique across spec/: no other schema carries this aice-incident id
    spec_dir = ROOT / "spec"
    hits = []
    for p in spec_dir.rglob("*.json"):
        text = p.read_text(encoding="utf-8")
        if "urn:cap:schema:aice-incident:v0.3" in text:
            hits.append(p.name)
    assert hits == ["incident.schema.json"], hits


def test_registry_canonical_range_is_604_611():
    registry = json.loads((ROOT / "spec" / "aice" / "registry.json").read_text(encoding="utf-8"))
    assert registry["canonical_code_range"] == ["AICE-604", "AICE-611"]


# --- Adversarial: the validator must catch AICE-611 / range / version tampering -

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


def _registry_path(tmp: Path) -> Path:
    return tmp / "spec" / "aice" / "registry.json"


def _tamper_remove_611(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["codes"] = [c for c in data["codes"] if c.get("code") != "AICE-611"]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_rename_612(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    for c in data["codes"]:
        if c.get("code") == "AICE-611":
            c["code"] = "AICE-612"
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_delete_doc(tmp: Path) -> None:
    (tmp / "spec" / "aice" / "codes" / "AICE-611.md").unlink()


def _tamper_break_link(tmp: Path) -> None:
    doc = tmp / "spec" / "aice" / "codes" / "AICE-611.md"
    doc.write_text(
        doc.read_text(encoding="utf-8") + "\n[broken](./NONEXISTENT-611.md)\n",
        encoding="utf-8",
    )


def _tamper_stale_range(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["canonical_code_range"] = ["AICE-604", "AICE-610"]
    reg.write_text(json.dumps(data), encoding="utf-8")


def _tamper_stale_version(tmp: Path) -> None:
    reg = _registry_path(tmp)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["spec_version"] = "0.2.0"
    reg.write_text(json.dumps(data), encoding="utf-8")


@pytest.mark.parametrize(
    "tamper",
    [
        _tamper_remove_611,
        _tamper_rename_612,
        _tamper_delete_doc,
        _tamper_break_link,
        _tamper_stale_range,
        _tamper_stale_version,
    ],
    ids=[
        "remove_from_registry",
        "rename_to_612",
        "delete_doc",
        "break_link",
        "stale_code_range",
        "stale_spec_version",
    ],
)
def test_check_aice_detects_tampering(tmp_path, tamper):
    script = _build_scratch(tmp_path)
    baseline = _run_check(script)
    assert baseline.returncode == 0, (
        "untampered scratch tree should pass:\n"
        f"{baseline.stdout}\n{baseline.stderr}"
    )
    tamper(tmp_path)
    result = _run_check(script)
    assert result.returncode != 0, (
        "check_aice.py failed to detect tampering:\n"
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
