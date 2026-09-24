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
import json
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


def _resolve_revision(repo_dir: Path, revision: str) -> str | None:
    """Returns the full SHA of the revision, or None if it does not resolve."""
    if not _revision_exists(repo_dir, revision):
        return None
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", revision],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return completed.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


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

    Additionally, four binding rules ensure the record matches its stored carriers:
    1. exit line: check results must contain a single exit= line matching the
       recorded exit_code.
    2. command: the check command must match the criterion's check_command.
    3. revision: every checked revision must resolve and match the re-observed
       and object revisions.
    4. receipt fields: when provenance is established, the receipt must be a
       JSON object with matching decision, served model, and input hashes.

    Rules 5 and 6 bind the reported costs to the same router receipt. Rule 5
    binds costs.route to every attempt the receipt records, set-aside ones
    included: the attempts in order, their turn and output-token totals, and
    the router's total wall time. Rule 6 binds costs.measured to the figures of
    the closing attempt. Whole-route costs are the receipt's figures for every
    attempt; money, driver time and relay tokens are not bound by either rule.

    A passing record now means the named links between the record and its
    stored carriers are checked; full provenance of the execution is not
    established by this.

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

    # -- binding rules --

    # 1. exit line
    for index, entry in enumerate(checks):
        entry_map = _mapping(entry)
        ref = entry_map.get("result_ref")
        if not _non_empty_str(ref):
            continue
        target = base / ref
        if not target.is_file():
            continue
        try:
            lines = target.read_text(encoding="utf-8").splitlines()
            exit_lines = [l for l in lines if l.startswith("exit=")]
            if len(exit_lines) != 1:
                problems.append(f"checks[{index}].result_ref: no single exit= line in {ref}")
                continue

            import re
            match = re.match(r"^exit=(-?\d+)$", exit_lines[0])
            if not match:
                problems.append(f"checks[{index}].result_ref: no single exit= line in {ref}")
                continue

            stored_exit = int(match.group(1))
            recorded_exit = entry_map.get("exit_code")
            if recorded_exit is not None and stored_exit != recorded_exit:
                problems.append(f"checks[{index}].exit_code: recorded {recorded_exit}, stored result says {stored_exit}")
        except (OSError, ValueError):
            continue

    # 2. command
    criteria_map = {
        _mapping(c).get("id"): _mapping(c).get("check_command")
        for c in _sequence(_mapping(record.get("postcondition")).get("criteria"))
    }
    for index, entry in enumerate(checks):
        entry_map = _mapping(entry)
        cid = entry_map.get("criterion_id")
        cmd = entry_map.get("command")
        if _non_empty_str(cid) and _non_empty_str(cmd):
            expected_cmd = criteria_map.get(cid)
            if expected_cmd != cmd:
                problems.append(f"checks[{index}].command: differs from criterion {cid} check_command")

    # 3. revision
    if repo_dir is not None:
        obj = _mapping(record.get("object"))
        obs = _mapping(observation_after)

        rev_obj = _resolve_revision(repo_dir, obj.get("revision_after", ""))
        rev_obs = _resolve_revision(repo_dir, obs.get("revision_after", ""))

        if rev_obs and rev_obj and rev_obs != rev_obj:
            problems.append(f"observation_after.revision_after: {obs.get('revision_after')} is not object.revision_after {obj.get('revision_after')}")

        for index, entry in enumerate(checks):
            entry_map = _mapping(entry)
            rev_checked = entry_map.get("revision_checked")
            if not _non_empty_str(rev_checked):
                continue
            resolved_checked = _resolve_revision(repo_dir, rev_checked)
            if resolved_checked:
                if rev_obs and resolved_checked != rev_obs:
                    problems.append(f"checks[{index}].revision_checked: {rev_checked} is not the re-observed revision {obs.get('revision_after')}")

    # 4. receipt fields
    verdict = _mapping(record.get("verdict"))
    if verdict.get("provenance_established") is True:
        receipt_ref = execution.get("receipt_ref")
        if _non_empty_str(receipt_ref):
            target = base / receipt_ref
            if target.is_file():
                try:
                    receipt = json.loads(target.read_text(encoding="utf-8"))
                    if not isinstance(receipt, dict):
                        problems.append(f"execution.receipt_ref: not a JSON object: {receipt_ref}")
                    else:
                        # (a) decision
                        rec_decision = receipt.get("decision")
                        if rec_decision is None:
                            problems.append("execution.receipt_ref: receipt lacks decision")
                        elif rec_decision != execution.get("decision"):
                            problems.append(f"execution.receipt_ref: decision {execution.get('decision')} is not the receipt decision {rec_decision}")

                        # (b) model_served
                        fallback_used = receipt.get("fallback_used")
                        if not isinstance(fallback_used, bool):
                            problems.append("execution.receipt_ref: receipt lacks fallback_used")
                        else:
                            attempt = "fallback_attempt" if fallback_used else "first_attempt"
                            attempt_map = _mapping(receipt.get(attempt))
                            rec_model = attempt_map.get("model_served")
                            if rec_model is None:
                                problems.append(f"execution.receipt_ref: receipt lacks {attempt}.model_served")
                            elif rec_model != _mapping(execution.get("actor")).get("model_served"):
                                problems.append(f"execution.receipt_ref: model_served {_mapping(execution.get('actor')).get('model_served')} is not the receipt served model {rec_model}")

                        # (c) inputs
                        rec_inputs = _mapping(receipt.get("inputs"))
                        if not rec_inputs:
                            problems.append("execution.receipt_ref: receipt lacks inputs")
                        else:
                            packet_sha = _mapping(rec_inputs.get("packet")).get("sha256")
                            check_shas = [_mapping(f).get("sha256") for f in _sequence(rec_inputs.get("check_files"))]
                            allowed_shas = {packet_sha} | {s for s in check_shas if s}

                            for index, entry in enumerate(inputs):
                                entry_map = _mapping(entry)
                                sha = entry_map.get("sha256")
                                if _non_empty_str(sha) and sha not in allowed_shas:
                                    problems.append(f"execution.receipt_ref: input {sha} is not among the receipt inputs")
                except (json.JSONDecodeError, OSError):
                    problems.append(f"execution.receipt_ref: not a JSON object: {receipt_ref}")

    # 5 and 6 both read the record's stored router receipt, whichever schema
    # version the record carries; neither applies when the ref does not resolve
    # to a JSON object (rule 4 already reports that when provenance is claimed).
    receipt_doc: Any = None
    stored_receipt_ref = execution.get("receipt_ref")
    if _non_empty_str(stored_receipt_ref):
        stored_target = base / stored_receipt_ref
        if stored_target.is_file():
            try:
                loaded = json.loads(stored_target.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                loaded = None
            if isinstance(loaded, dict):
                receipt_doc = loaded

    # 5. route costs: every attempt the receipt records, set-aside ones included
    route_value = costs.get("route")
    if isinstance(route_value, dict) and receipt_doc is not None:
        route = route_value
        attempt_names = ["first_attempt"]
        if receipt_doc.get("fallback_used") is True:
            attempt_names.append("fallback_attempt")

        receipt_attempts: list[dict[str, Any]] = []
        absent_attempts: set[str] = set()
        for name in attempt_names:
            attempt = receipt_doc.get(name)
            if isinstance(attempt, dict):
                receipt_attempts.append(attempt)
            else:
                receipt_attempts.append({})
                absent_attempts.add(name)
                problems.append(f"costs.route: receipt lacks {name}")

        listed = _sequence(route.get("attempts"))
        if len(listed) != len(receipt_attempts):
            problems.append(
                f"costs.route.attempts: {len(listed)} listed, receipt has "
                f"{len(receipt_attempts)}"
            )
        else:
            for index, name in enumerate(attempt_names):
                if name in absent_attempts:
                    continue
                entry_map = _mapping(listed[index])
                attempt = receipt_attempts[index]
                for field in ("model_served", "turns", "output_tokens", "wall_s"):
                    if field not in attempt:
                        problems.append(f"costs.route: receipt lacks {name}.{field}")
                    elif entry_map.get(field) != attempt.get(field):
                        problems.append(
                            f"costs.route.attempts[{index}].{field}: recorded "
                            f"{entry_map.get(field)}, receipt says {attempt.get(field)}"
                        )

        def _attempt_sum(field: str) -> Any:
            total: Any = 0
            for attempt in receipt_attempts:
                value = attempt.get(field)
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    return None
                total += value
            return total

        turns_sum = _attempt_sum("turns")
        if turns_sum is not None and route.get("turns_total") != turns_sum:
            problems.append(
                f"costs.route.turns_total: recorded {route.get('turns_total')}, "
                f"receipt attempts sum to {turns_sum}"
            )
        tokens_sum = _attempt_sum("output_tokens")
        if tokens_sum is not None and route.get("output_tokens_total") != tokens_sum:
            problems.append(
                f"costs.route.output_tokens_total: recorded "
                f"{route.get('output_tokens_total')}, receipt attempts sum to {tokens_sum}"
            )
        if "total_wall_s" not in receipt_doc:
            problems.append("costs.route: receipt lacks total_wall_s")
        elif route.get("router_wall_s") != receipt_doc.get("total_wall_s"):
            problems.append(
                f"costs.route.router_wall_s: recorded {route.get('router_wall_s')}, "
                f"receipt says {receipt_doc.get('total_wall_s')}"
            )

    # 6. closing attempt: measured figures must be the receipt's closing attempt
    if receipt_doc is not None:
        closing_name = (
            "fallback_attempt"
            if receipt_doc.get("fallback_used") is True
            else "first_attempt"
        )
        closing = _mapping(receipt_doc.get(closing_name))
        measured = _mapping(costs.get("measured"))
        for record_field, receipt_field in (
            ("worker_turns", "turns"),
            ("worker_output_tokens", "output_tokens"),
            ("worker_wall_s", "wall_s"),
        ):
            recorded = measured.get(record_field)
            if recorded is None:
                continue
            if recorded != closing.get(receipt_field):
                problems.append(
                    f"costs.measured.{record_field}: recorded {recorded}, receipt "
                    f"closing attempt says {closing.get(receipt_field)}"
                )

    return problems
