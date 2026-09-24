"""Probe: which claims of an executed-transition record does validate_execution_record NOT bind to the
stored machine results? Driver-run, deterministic, no model calls.

usage: python probe_record_binding.py <repo_root> <scratch_base> [--expect-closed]

Builds <scratch_base> (outside the tree) holding copies of every file the shipped example record
references, then validates mutated copies of the example against that base with revisions resolved
in <repo_root>. Each gap case keeps the record schema-valid and self-consistent while the stored
result contradicts it. Without --expect-closed the exit code is 0 and every case is reported as an
observation (OK = the validator accepted the record; REFUSED = it named a problem). With
--expect-closed the script is the oracle for the binding step: it exits 1 unless every case is
REFUSED, so it is red on the baseline for the named reason (the four gap cases are accepted).
"""
import copy
import json
import pathlib
import shutil
import sys

repo = pathlib.Path(sys.argv[1]).resolve()
base = pathlib.Path(sys.argv[2]).resolve()
expect_closed = "--expect-closed" in sys.argv
sys.path.insert(0, str(repo / "reference" / "python"))
from cap.execution_record import validate_execution_record  # noqa: E402

EXAMPLE = "examples/transition_execution_record_example.json"
OTHER_EXISTING_REVISION = "e65b9af4"  # origin/main base of the research branch; exists, is not revision_after
example = json.loads((repo / EXAMPLE).read_text(encoding="utf-8-sig"))


def refs(rec):
    out = [rec["candidate"]["candidate_ref"], rec["candidate"]["mirror_frame_before_ref"], rec["costs"]["estimated_ref"]]
    if rec["observation_after"].get("mirror_frame_after_ref"):
        out.append(rec["observation_after"]["mirror_frame_after_ref"])
    if rec["execution"].get("receipt_ref"):
        out.append(rec["execution"]["receipt_ref"])
    out += [i["ref"] for i in rec["execution"]["inputs"]]
    out += [c["result_ref"] for c in rec["checks"]]
    out += [e["result_ref"] for e in rec["expected_evidence_results"] if e.get("result_ref")]
    return out


if base.exists():
    shutil.rmtree(base)
for rel in sorted(set(refs(example))):
    dst = base / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(repo / rel, dst)

# materials for the gap cases, all outside the tree
failed_result = "examples/transition_execution_record/check_result_c1_failed.txt"
(base / failed_result).write_bytes(b"cmd=python -m pytest -q reference/python/tests/test_example.py\nexit=1\n1 failed\n")
stray = "examples/transition_execution_record/stray_notes.txt"
(base / stray).write_bytes(b"not a receipt: no decision, no input hash, no model identity\n")

criterion_command = example["postcondition"]["criteria"][0]["check_command"]
cases = []

rec = copy.deepcopy(example)
rec["checks"][0]["result_ref"] = "examples/transition_execution_record/no_such_result.txt"
cases.append(("control_missing_result_file", rec))

rec = copy.deepcopy(example)
rec["checks"][0]["result_ref"] = failed_result  # stored result says exit=1 / failed; record says pass, exit_code 0
cases.append(("gap1_result_file_says_exit_1_record_says_pass", rec))

rec = copy.deepcopy(example)
rec["checks"][0]["revision_checked"] = OTHER_EXISTING_REVISION  # resolvable, but not the re-observed revision
cases.append(("gap2_check_at_other_existing_revision", rec))

rec = copy.deepcopy(example)
rec["checks"][0]["command"] = "echo not-the-criterion-command"  # differs from criteria[0].check_command
assert rec["checks"][0]["command"] != criterion_command
cases.append(("gap3_check_command_differs_from_criterion", rec))

rec = copy.deepcopy(example)
rec["execution"]["receipt_ref"] = stray  # exists, is text, carries nothing of the execution
rec["verdict"]["provenance_established"] = True
cases.append(("gap4_stray_text_file_as_receipt_provenance_true", rec))

all_refused = True
for label, record in cases:
    problems = validate_execution_record(record, base, repo)
    observed = "REFUSED" if problems else "OK"
    all_refused = all_refused and bool(problems)
    print(f"case={label} observed={observed} expected_when_bound=REFUSED problems={json.dumps(problems, ensure_ascii=True)}")

if expect_closed:
    print("probe_record_binding: " + ("all cases refused" if all_refused else "at least one gap case accepted"))
    sys.exit(0 if all_refused else 1)
print("probe_record_binding: observation mode, exit 0")
