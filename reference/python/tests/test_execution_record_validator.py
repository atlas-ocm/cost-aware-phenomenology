"""Executable tests for the executed-transition record validator.

The schema tests (test_transition_execution_schema.py) pin the SHAPE of an
executed-transition record. These tests pin the RESOLUTION the schema cannot
perform: every reference names an existing file, every input hash re-derives,
every revision resolves in the repository, and every criterion is covered by a
check when the verdict claims the postcondition was met.

    SCHEMA-VALID != RESOLVED

A record whose references, hashes and revisions all point nowhere is still
schema-valid; the validator added here is what reports it. Each rule below has
a test that mutates a copy of the worked example and confirms the validator
names the offence, plus the control that the pristine example is sound.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.execution_record import validate_execution_record  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_PATH = ROOT / "examples" / "transition_execution_record_example.json"
SCRIPT = ROOT / "reference" / "python" / "scripts" / "validate_execution_record.py"

UNKNOWN_REVISION = "deadbeef" * 5


def _load_example() -> dict:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8-sig"))


def _problems(record: dict, repo_dir: Path | None = None) -> list[str]:
    return validate_execution_record(record, base_dir=ROOT, repo_dir=repo_dir)


def _named(problems: list[str], needle: str) -> list[str]:
    return [problem for problem in problems if needle in problem]


# -- control: the worked example resolves --


def test_example_resolves_with_repo():
    assert _problems(_load_example(), repo_dir=ROOT) == []


def test_example_resolves_without_repo():
    assert _problems(_load_example()) == []


# -- references: every ref must name an existing file --


def test_unresolvable_candidate_ref_is_named():
    record = _load_example()
    record["candidate"]["candidate_ref"] = "examples/no_such_candidate.json"
    problems = _problems(record, repo_dir=ROOT)
    assert _named(problems, "candidate_ref") and _named(
        problems, "examples/no_such_candidate.json"
    ), problems


def test_unresolvable_receipt_ref_is_named():
    record = _load_example()
    record["execution"]["receipt_ref"] = (
        "examples/transition_execution_record/no_such_receipt.json"
    )
    problems = _problems(record, repo_dir=ROOT)
    assert _named(problems, "receipt_ref") and _named(
        problems, "examples/transition_execution_record/no_such_receipt.json"
    ), problems


def test_unresolvable_check_result_ref_is_named():
    record = _load_example()
    record["checks"][0]["result_ref"] = (
        "examples/transition_execution_record/no_such_check_result.txt"
    )
    problems = _problems(record, repo_dir=ROOT)
    assert _named(problems, "result_ref") and _named(
        problems, "examples/transition_execution_record/no_such_check_result.txt"
    ), problems


def test_unresolvable_input_ref_is_named():
    record = _load_example()
    record["execution"]["inputs"][0]["ref"] = "examples/no_such_input.json"
    problems = _problems(record, repo_dir=ROOT)
    assert _named(problems, "ref") and _named(
        problems, "examples/no_such_input.json"
    ), problems


# -- hashes: the recorded sha256 must re-derive --


def test_wrong_input_sha256_is_named():
    record = _load_example()
    ref = record["execution"]["inputs"][0]["ref"]
    record["execution"]["inputs"][0]["sha256"] = "0" * 64
    problems = _problems(record, repo_dir=ROOT)
    assert _named(problems, "sha256") and _named(problems, ref), problems


# -- revisions: each revision must resolve in the repository --


def test_unknown_revision_before_is_named():
    record = _load_example()
    record["object"]["revision_before"] = UNKNOWN_REVISION
    problems = _problems(record, repo_dir=ROOT)
    assert _named(problems, "revision") and _named(problems, UNKNOWN_REVISION), problems


def test_unknown_revision_after_is_named():
    record = _load_example()
    unknown = "1" * 40
    record["object"]["revision_after"] = unknown
    problems = _problems(record, repo_dir=ROOT)
    assert _named(problems, "revision") and _named(problems, unknown), problems


def test_unknown_revision_checked_is_named():
    record = _load_example()
    unknown = "2" * 40
    record["checks"][0]["revision_checked"] = unknown
    problems = _problems(record, repo_dir=ROOT)
    assert _named(problems, "revision") and _named(problems, unknown), problems


def test_unknown_revisions_are_ignored_without_repo():
    """Without a repository there is nothing to resolve revisions against."""
    record = _load_example()
    record["object"]["revision_before"] = UNKNOWN_REVISION
    record["object"]["revision_after"] = "1" * 40
    record["observation_after"]["revision_after"] = "2" * 40
    record["checks"][0]["revision_checked"] = "3" * 40
    assert _problems(record) == []


# -- coverage: checks name real criteria and cover a met postcondition --


def test_uncovered_criterion_is_named_when_postcondition_met():
    record = _load_example()
    assert record["verdict"]["postcondition_met"] is True
    record["postcondition"]["criteria"].append(
        {
            "id": "c2",
            "statement": "A second criterion that no check ever covered.",
            "check_command": "python -m pytest -q reference/python/tests/test_example.py",
        }
    )
    problems = _problems(record, repo_dir=ROOT)
    coverage = _named(problems, "postcondition_met")
    assert _named(coverage, "c2"), problems
    assert not _named(coverage, "c1"), problems


def test_uncovered_criterion_is_not_reported_when_postcondition_not_met():
    """The coverage rule is conditional: an unmet postcondition is a verdict,
    not a resolution defect."""
    record = _load_example()
    record["verdict"]["postcondition_met"] = False
    record["postcondition"]["criteria"].append(
        {
            "id": "c2",
            "statement": "A second criterion that no check ever covered.",
            "check_command": "python -m pytest -q reference/python/tests/test_example.py",
        }
    )
    assert _problems(record, repo_dir=ROOT) == []


def test_check_naming_unknown_criterion_is_named():
    record = _load_example()
    record["checks"][0]["criterion_id"] = "c9"
    problems = _problems(record, repo_dir=ROOT)
    assert _named(problems, "unknown") and _named(problems, "c9"), problems


# -- bad records are reported, never raised --


def test_schema_violation_is_reported_not_raised():
    record = _load_example()
    record["unexpected_field"] = "x"
    problems = _problems(record, repo_dir=ROOT)
    assert problems
    assert _named(problems, "unexpected_field"), problems


def test_empty_record_yields_problems():
    problems = validate_execution_record({}, base_dir=ROOT)
    assert problems
    assert all(isinstance(problem, str) for problem in problems)


def test_non_object_record_yields_problems():
    problems = validate_execution_record(["not", "a", "record"], base_dir=ROOT)
    assert problems


# -- CLI --


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=ROOT,
    )


def test_cli_exits_zero_and_prints_ok_on_the_example():
    completed = _run_cli(str(EXAMPLE_PATH), "--repo", ".")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip() == "OK"


def test_cli_names_candidate_ref_on_a_broken_copy(tmp_path):
    """References stay relative to the repository root, so the broken copy
    keeps the example's refs and breaks exactly one of them."""
    record = _load_example()
    record["candidate"]["candidate_ref"] = "examples/no_such_candidate.json"
    broken = tmp_path / "broken_transition_execution_record.json"
    broken.write_text(json.dumps(record, indent=2), encoding="utf-8")

    completed = _run_cli(str(broken))
    assert completed.returncode != 0, completed.stdout + completed.stderr
    assert "candidate_ref" in completed.stdout, completed.stdout


def test_cli_exits_two_on_an_unreadable_record(tmp_path):
    completed = _run_cli(str(tmp_path / "no_such_record.json"))
    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert completed.stdout.strip(), "an unreadable record must print one problem"
