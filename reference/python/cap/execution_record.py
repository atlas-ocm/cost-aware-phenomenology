"""Resolution validator for the CAP executed-transition record.

The schema (spec/transition_execution.schema.json) constrains the SHAPE of an
executed-transition record; it cannot see the repository. This module closes
that gap: it resolves every reference the record points at, re-derives every
input hash, resolves every git revision, and checks criterion coverage, so a
record that merely looks complete is reported as incomplete.

The record binds four steps:

- before: the observed state, the object revision, the candidate, and the
  postcondition, which was defined before execution;
- during: the actor, the tool, the hashed inputs, and the stored receipt;
- after: re-observation of the object plus per-criterion checks that carry
  result references;
- feedback: divergence between expectation and observation, with measured
  costs kept apart from estimates.

Two questions are separated deliberately. "Does the required state exist
now?" is answered from the after step: the checks are run against the
re-observed revision, and verdict.postcondition_met requires every criterion
to have a passing check. "Which execution led to it?" is answered from the
during step: the actor identity, the hashed inputs, and the stored receipt. A
record may answer one and not the other, so the two are reported independently
rather than collapsed into a single verdict.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any

import jsonschema

from .schemas import load_schema

SCHEMA_NAME = "transition_execution.schema"


def _mapping(value: Any) -> dict[str, Any]:
    """The value as a mapping, or an empty mapping when it is not one."""
    return value if isinstance(value, dict) else {}


def _sequence(value: Any) -> list[Any]:
    """The value as a list, or an empty list when it is not one."""
    return value if isinstance(value, list) else []


def _non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _revision_exists(repo_dir: Path, revision: str) -> bool:
    """True when `revision` resolves to a commit in `repo_dir`.

    Resolution is delegated to git itself, so short hashes, tags and refs are
    accepted exactly as git accepts them, and an unknown revision is a
    non-zero exit rather than an exception.
    """
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_dir), "cat-file", "-e", f"{revision}^{{commit}}"],
            capture_output=True,
        )
    except OSError:
        return False
    return completed.returncode == 0


def validate_execution_record(
    record: dict, base_dir: Path, repo_dir: Path | None = None
) -> list[str]:
    """Validate an executed-transition record against its schema and the repository.

    The record binds four steps (before / during / after / feedback) and
    separates two questions: does the required state exist now, and which
    execution led to it. This function resolves both against the repository:

    1. schema: the record is validated against
       spec/transition_execution.schema.json, one problem per schema error;
    2. references: candidate_ref, mirror_frame_before_ref,
       mirror_frame_after_ref, receipt_ref, estimated_ref, checks[].result_ref,
       expected_evidence_results[].result_ref and execution.inputs[].ref must
       each name an existing file under base_dir;
    3. hashes: every execution.inputs[] sha256 must equal the sha256 of the
       bytes of the file its ref names;
    4. revisions: object.revision_before, object.revision_after,
       observation_after.revision_after and every checks[].revision_checked
       must resolve to a commit in repo_dir. Revisions are not checked when
       repo_dir is None.

    Two coverage rules the schema cannot express are enforced as well: every
    checks[].criterion_id must name a criterion of postcondition.criteria, and
    when verdict.postcondition_met is true every criterion must have at least
    one check with status "pass".

    Returns a list of problem strings, empty when the record is sound. It never
    raises on a bad record: a non-dict, empty or garbled record yields problems.
    """
    problems: list[str] = []

    validator = jsonschema.Draft202012Validator(load_schema(SCHEMA_NAME))
    try:
        schema_errors = list(validator.iter_errors(record))
    except Exception as exc:  # pragma: no cover - defensive, jsonschema is stable
        problems.append(f"record: schema validation failed: {exc}")
        schema_errors = []
    for error in schema_errors:
        path = ".".join(str(part) for part in error.absolute_path)
        problems.append(f"{path}: {error.message}" if path else error.message)

    if not isinstance(record, dict):
        # Only the schema can say anything about a non-object instance.
        return problems

    base = Path(base_dir)

    candidate = _mapping(record.get("candidate"))
    observation_after = _mapping(record.get("observation_after"))
    execution = _mapping(record.get("execution"))
    costs = _mapping(record.get("costs"))
    checks = _sequence(record.get("checks"))
    inputs = _sequence(execution.get("inputs"))

    # -- references: every ref must name an existing file under base_dir --
    references: list[tuple[str, str]] = []
    for key in ("candidate_ref", "mirror_frame_before_ref"):
        value = candidate.get(key)
        if _non_empty_str(value):
            references.append((f"candidate.{key}", value))
    value = observation_after.get("mirror_frame_after_ref")
    if _non_empty_str(value):
        references.append(("observation_after.mirror_frame_after_ref", value))
    value = execution.get("receipt_ref")
    if _non_empty_str(value):
        references.append(("execution.receipt_ref", value))
    value = costs.get("estimated_ref")
    if _non_empty_str(value):
        references.append(("costs.estimated_ref", value))
    for index, entry in enumerate(inputs):
        value = _mapping(entry).get("ref")
        if _non_empty_str(value):
            references.append((f"execution.inputs[{index}].ref", value))
    for index, entry in enumerate(checks):
        value = _mapping(entry).get("result_ref")
        if _non_empty_str(value):
            references.append((f"checks[{index}].result_ref", value))
    for index, entry in enumerate(_sequence(record.get("expected_evidence_results"))):
        value = _mapping(entry).get("result_ref")
        if _non_empty_str(value):
            references.append((f"expected_evidence_results[{index}].result_ref", value))

    for label, ref in references:
        if not (base / ref).is_file():
            problems.append(f"{label}: reference not found: {ref}")

    # -- hashes: sha256 must match the bytes of the file the ref names --
    for index, entry in enumerate(inputs):
        entry_map = _mapping(entry)
        ref = entry_map.get("ref")
        recorded = entry_map.get("sha256")
        if not _non_empty_str(ref) or not isinstance(recorded, str):
            continue
        target = base / ref
        if not target.is_file():
            # Already reported as an unresolved reference; there is nothing
            # to hash.
            continue
        try:
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
        except OSError as exc:
            problems.append(
                f"execution.inputs[{index}].sha256: unreadable input {ref}: {exc}"
            )
            continue
        if recorded != digest:
            problems.append(
                f"execution.inputs[{index}].sha256: mismatch for {ref}: "
                f"recorded {recorded}, computed {digest}"
            )

    # -- revisions: each revision must resolve to a commit in repo_dir --
    if repo_dir is not None:
        revisions: list[tuple[str, str]] = []
        obj = _mapping(record.get("object"))
        for key in ("revision_before", "revision_after"):
            value = obj.get(key)
            if _non_empty_str(value):
                revisions.append((f"object.{key}", value))
        value = observation_after.get("revision_after")
        if _non_empty_str(value):
            revisions.append(("observation_after.revision_after", value))
        for index, entry in enumerate(checks):
            value = _mapping(entry).get("revision_checked")
            if _non_empty_str(value):
                revisions.append((f"checks[{index}].revision_checked", value))

        for label, revision in revisions:
            if not _revision_exists(repo_dir, revision):
                problems.append(f"{label}: unresolved revision: {revision}")

    # -- coverage: checks name real criteria, and a met postcondition is covered --
    criterion_ids: list[str] = []
    for entry in _sequence(_mapping(record.get("postcondition")).get("criteria")):
        value = _mapping(entry).get("id")
        if _non_empty_str(value) and value not in criterion_ids:
            criterion_ids.append(value)

    passing: set[str] = set()
    for index, entry in enumerate(checks):
        entry_map = _mapping(entry)
        criterion_id = entry_map.get("criterion_id")
        if _non_empty_str(criterion_id) and criterion_id not in criterion_ids:
            problems.append(
                f"checks[{index}].criterion_id: unknown criterion id: {criterion_id}"
            )
        if entry_map.get("status") == "pass" and _non_empty_str(criterion_id):
            passing.add(criterion_id)

    if _mapping(record.get("verdict")).get("postcondition_met") is True:
        for criterion_id in criterion_ids:
            if criterion_id not in passing:
                problems.append(
                    f"verdict.postcondition_met: uncovered criterion {criterion_id} "
                    "has no passing check"
                )

    return problems
