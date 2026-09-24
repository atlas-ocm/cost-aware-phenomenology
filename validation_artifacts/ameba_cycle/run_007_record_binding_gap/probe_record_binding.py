"""Oracle and probe for the execution-record binding step (driver-written, deterministic, no model calls).

usage: python probe_record_binding.py <repo_root> <scratch_base> [--expect-closed]

Builds <scratch_base> (outside the tree) with copies of every file the shipped example record references,
then validates the unmodified example and mutated copies of it against that base, with revisions resolved
in <repo_root>. Every case carries an expectation: ACCEPT (no problem at all) or REFUSE with a named
anchor that at least one problem string must contain, so a refusal for the wrong reason does not count.
Observation mode (default) prints what the validator does and exits 0. With --expect-closed the script
exits 0 only when every expectation holds; at 26535dc / 2731484 it exits 1 because the gap cases are
accepted, so it is red on the baseline for the named reason.

What a green run means: the named links between the record and its stored carriers are checked (the
exit line of a stored result, the criterion's command, the re-observed revision, specific fields of the
receipt). It does not establish full provenance of the execution.

Revision 2 (after the review of 2731484): named defects per case, three positive controls (unmodified
example; a receipt in the router's shape whose fields match; a short SHA of the same commit), and the
case "right words in wrong receipt fields", which a text-containment rule would wrongly accept.
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


def put(rel, data):
    target = base / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return rel


ex = example["execution"]
decision, model_served, input_sha = ex["decision"], ex["actor"]["model_served"], ex["inputs"][0]["sha256"]
revision_after = example["observation_after"]["revision_after"]


def router_receipt(dec, served, packet_sha, notes=""):
    """A receipt in the shape the NoMCP router writes: the fields rule 4 reads, and nothing else counts."""
    body = {
        "task_id": "example", "variant": "coding", "decision": dec, "fallback_used": False,
        "first_attempt": {"model_requested": served, "model_served": served, "turns": 1, "output_tokens": 1, "wall_s": 1.0},
        "inputs": {"packet": {"sha256": packet_sha, "size": 1}, "check_files": []},
        "notes": notes,
    }
    return json.dumps(body, indent=2).encode("utf-8") + b"\n"


failed_result = put("examples/transition_execution_record/check_result_c1_failed.txt",
                    b"cmd=python -m pytest -q reference/python/tests/test_example.py\nexit=1\n1 failed\n")
stray = put("examples/transition_execution_record/stray_notes.txt",
            b"not a receipt: no decision, no input hash, no model identity\n")
matching = put("examples/transition_execution_record/receipt_router_matching.json",
               router_receipt(decision, model_served, input_sha))
wrong_fields = put("examples/transition_execution_record/receipt_words_in_wrong_fields.json",
                   router_receipt("EXCEPTION", "some-other-model", "0" * 64,
                                  notes=f"decision {decision}; served {model_served}; input {input_sha}"))

ACCEPT = "ACCEPT"
cases = []


def case(label, mutate, expectation):
    rec = copy.deepcopy(example)
    mutate(rec)
    cases.append((label, rec, expectation))


case("positive_unmodified_example", lambda r: None, ACCEPT)


def _matching(r):
    r["execution"]["receipt_ref"] = matching
    r["verdict"]["provenance_established"] = True


case("positive_router_shaped_receipt_fields_match", _matching, ACCEPT)
case("positive_short_sha_of_the_same_commit",
     lambda r: r["checks"][0].__setitem__("revision_checked", revision_after[:7]), ACCEPT)
case("control_missing_result_file",
     lambda r: r["checks"][0].__setitem__("result_ref", "examples/transition_execution_record/no_such_result.txt"),
     ("REFUSE", "reference not found"))
case("gap1_result_file_says_exit_1_record_says_pass",
     lambda r: r["checks"][0].__setitem__("result_ref", failed_result), ("REFUSE", "checks[0].exit_code"))
case("gap2_check_at_other_existing_revision",
     lambda r: r["checks"][0].__setitem__("revision_checked", OTHER_EXISTING_REVISION),
     ("REFUSE", "checks[0].revision_checked"))
case("gap3_check_command_differs_from_criterion",
     lambda r: r["checks"][0].__setitem__("command", "echo not-the-criterion-command"),
     ("REFUSE", "checks[0].command"))


def _stray(r):
    r["execution"]["receipt_ref"] = stray
    r["verdict"]["provenance_established"] = True


case("gap4_stray_text_file_as_receipt_provenance_true", _stray, ("REFUSE", "execution.receipt_ref"))


def _wrong_fields(r):
    r["execution"]["receipt_ref"] = wrong_fields
    r["verdict"]["provenance_established"] = True


case("gap5_right_words_in_wrong_receipt_fields", _wrong_fields, ("REFUSE", "execution.receipt_ref"))

all_hold = True
for label, record, expectation in cases:
    problems = validate_execution_record(record, base, repo)
    observed = "REFUSED" if problems else "OK"
    if expectation == ACCEPT:
        holds = not problems
        expected = "ACCEPT"
    else:
        anchor = expectation[1]
        holds = any(anchor in problem for problem in problems)
        expected = f"REFUSE[{anchor}]"
    all_hold = all_hold and holds
    print(f"case={label} observed={observed} expected={expected} holds={holds} problems={json.dumps(problems, ensure_ascii=True)}")

if expect_closed:
    print("probe_record_binding: " + ("every expectation holds" if all_hold else "at least one expectation fails"))
    sys.exit(0 if all_hold else 1)
print("probe_record_binding: observation mode, exit 0")
