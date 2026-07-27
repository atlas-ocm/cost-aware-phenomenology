"""Executable tests for the candidate-surface validator.

`check_candidates.py` passing once in a session is evidence about that session.
These tests make it evidence about every future run:

    CANDIDATE VALIDATOR EXISTS != CANDIDATE VALIDATOR WILL RUN NEXT TIME

Every tamper case below mutates a COPY of spec/aice/candidates/ in tmp_path and
asserts the validator rejects it. A validator that silently stopped checking a
rule would keep exit 0 here and fail these tests instead.

The candidate surface remains non-canonical: nothing in this file touches the
AICE registry, the schema, the defined-code count, or the example count.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "reference" / "python" / "scripts" / "aice" / "check_candidates.py"
CAND_DIR = ROOT / "spec" / "aice" / "candidates"


def run_validator(root):
    """Run check_candidates.py against a repo root. Returns (exit_code, output)."""
    script = root / "reference" / "python" / "scripts" / "aice" / "check_candidates.py"
    proc = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


@pytest.fixture
def repo(tmp_path):
    """A minimal copy of the repo laid out the way the validator expects."""
    dst_cand = tmp_path / "spec" / "aice" / "candidates"
    dst_cand.parent.mkdir(parents=True)
    shutil.copytree(CAND_DIR, dst_cand)
    shutil.copy(ROOT / "spec" / "aice" / "registry.json",
                tmp_path / "spec" / "aice" / "registry.json")
    dst_script = tmp_path / "reference" / "python" / "scripts" / "aice"
    dst_script.mkdir(parents=True)
    shutil.copy(SCRIPT, dst_script / "check_candidates.py")
    return tmp_path


def a_dossier(repo, needle):
    """The first candidate file whose text contains `needle`."""
    for p in sorted((repo / "spec" / "aice" / "candidates").glob("*.md")):
        if p.name != "README.md" and needle in p.read_text(encoding="utf-8"):
            return p
    raise AssertionError(f"no candidate dossier contains {needle!r}")


def test_pristine_copy_passes(repo):
    """The control: an unmutated copy must pass, or every tamper below is vacuous."""
    code, out = run_validator(repo)
    assert code == 0, out


def test_promoted_marker_removal_is_caught(repo):
    """A promoted dossier that loses its marker is the AICE-619 shape in miniature."""
    p = a_dossier(repo, "promotion_status")
    text = p.read_text(encoding="utf-8")
    p.write_text(re.sub(r"promotion_status\s*[|:]?\s*`?PROMOTED`?", "promotion_status | PENDING",
                        text), encoding="utf-8")
    code, out = run_validator(repo)
    assert code != 0 and "PROMOTED" in out, out


def test_duplicate_machine_name_is_caught(repo):
    """Two active candidates may not claim one identity."""
    p = a_dossier(repo, "`ATTEMPT_CONSUMPTION_OUTCOME_EVIDENCE_GAP`")
    q = a_dossier(repo, "`FORENSIC_ESCALATION_DIRECT_EXPERIMENT_BYPASS`")
    q.write_text(q.read_text(encoding="utf-8").replace(
        "`FORENSIC_ESCALATION_DIRECT_EXPERIMENT_BYPASS`",
        "`ATTEMPT_CONSUMPTION_OUTCOME_EVIDENCE_GAP`"), encoding="utf-8")
    assert p.exists()
    code, out = run_validator(repo)
    assert code != 0 and "more than one candidate" in out, out


def test_missing_withdrawal_reason_is_caught(repo):
    """A withdrawn dossier must say why; retention without a reason is not a record."""
    # Select on the status FIELD: other dossiers mention the status in prose.
    p = a_dossier(repo, "| status | `WITHDRAWN_TRIGGER_FALSIFIED` |")
    text = re.sub(r"retract", "xxxxxxx", p.read_text(encoding="utf-8"), flags=re.I)
    text = re.sub(r"withdrawal reason", "xxxxxxx", text, flags=re.I)
    p.write_text(text, encoding="utf-8")
    code, out = run_validator(repo)
    assert code != 0 and "retraction" in out, out


def test_readme_disk_divergence_is_caught(repo):
    """A dossier on disk but absent from Contents is an unlisted candidate."""
    (repo / "spec" / "aice" / "candidates" / "orphan-candidate.md").write_text(
        "# Orphan\n", encoding="utf-8")
    code, out = run_validator(repo)
    assert code != 0 and "orphan-candidate.md" in out, out


def test_unknown_lifecycle_is_caught(repo):
    """Only statuses the README documents may be used."""
    p = a_dossier(repo, "`PROPOSED`")
    p.write_text(p.read_text(encoding="utf-8").replace(
        "| status | `PROPOSED` |", "| status | `TOTALLY_MADE_UP` |"), encoding="utf-8")
    code, out = run_validator(repo)
    assert code != 0 and "lifecycle" in out, out


def test_legacy_machine_name_spelling_rejected_for_active_dossier(repo):
    """Grandfathering is for promoted dossiers only; new files must not drift back."""
    p = a_dossier(repo, "`FORENSIC_ESCALATION_DIRECT_EXPERIMENT_BYPASS`")
    p.write_text(p.read_text(encoding="utf-8").replace(
        "| machine_name |", "| machine name |"), encoding="utf-8")
    code, out = run_validator(repo)
    assert code != 0 and "grandfathered" in out, out


def test_legacy_spelling_still_allowed_for_promoted_dossier(repo):
    """The complement: grandfathering must actually grandfather, not just warn."""
    code, out = run_validator(repo)
    assert code == 0, out
    promoted = [p for p in (repo / "spec" / "aice" / "candidates").glob("*.md")
                if "promotion_status" in p.read_text(encoding="utf-8")]
    assert promoted, "expected at least one promoted dossier to exercise this rule"
    assert any(re.search(r"machine name", p.read_text(encoding="utf-8"), re.I)
               for p in promoted), "expected a promoted dossier using the legacy spelling"


def test_operator_indicated_number_not_presented_as_canonical(repo):
    """An operator's intended future number may never be self-declared as assigned."""
    p = a_dossier(repo, "operator_indicated_number")
    p.write_text(p.read_text(encoding="utf-8").replace(
        "| canonical_code | `UNASSIGNED` |", "| canonical_code | `AICE-622` |"),
        encoding="utf-8")
    code, out = run_validator(repo)
    assert code != 0 and "UNASSIGNED" in out, out


def test_candidate_indicating_reserved_600_is_rejected(repo):
    """AICE-600 is held for Ontological Lockdown; no other class may point at it."""
    p = a_dossier(repo, "operator_indicated_number")
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"(operator_indicated_number \| )`AICE-\d{3}`", r"\1`AICE-600`", text)
    p.write_text(text, encoding="utf-8")
    code, out = run_validator(repo)
    assert code != 0 and "AICE-600" in out and "reserved" in out.lower(), out


def test_reserved_title_mention_does_not_confer_ownership(repo):
    """The bypass: naming the reserved class is not being it.

    A candidate that merely mentions 'Ontological Lockdown' — in a differential,
    a comparison row, even a negation — must not thereby earn the right to
    AICE-600. Ownership is read off the dossier's own identity fields.
    """
    p = a_dossier(repo, "operator_indicated_number")
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"(operator_indicated_number \| )`AICE-\d{3}`", r"\1`AICE-600`", text)
    # The phrase appears, but in a row about something this dossier is NOT.
    text = text.replace(
        "## Identity",
        "## Identity\n\nThis class is unrelated to Ontological Lockdown.\n", 1)
    p.write_text(text, encoding="utf-8")
    code, out = run_validator(repo)
    assert code != 0 and "AICE-600" in out, out


def test_candidate_claiming_canonical_600_is_rejected(repo):
    """Reserved is not defined: claiming the number needs a promotion episode."""
    p = a_dossier(repo, "| canonical_code | `UNASSIGNED` |")
    p.write_text(p.read_text(encoding="utf-8").replace(
        "| canonical_code | `UNASSIGNED` |", "| canonical_code | `AICE-600` |"),
        encoding="utf-8")
    code, out = run_validator(repo)
    assert code != 0 and "AICE-600" in out, out


def test_candidate_validator_stays_out_of_the_canonical_checker():
    """The separation the canonical suite asserts, restated from this side."""
    checker = (ROOT / "reference" / "python" / "scripts" / "aice" / "check_aice.py").read_text(
        encoding="utf-8")
    assert "candidate" not in checker.lower()
    assert "check_candidates" not in checker
