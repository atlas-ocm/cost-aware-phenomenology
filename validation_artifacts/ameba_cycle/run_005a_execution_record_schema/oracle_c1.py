"""Ephemeral oracle for cap-execution-record-05a: the schema, the example and the schema-level invariants only.
No validator is required here. Run from the repository root; exit 0 iff every assertion holds."""
import copy
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, "reference/python")
import jsonschema  # noqa: E402

ROOT = pathlib.Path(".").resolve()
schema_path = ROOT / "spec" / "transition_execution.schema.json"
assert schema_path.is_file(), "spec/transition_execution.schema.json missing"
schema = json.loads(schema_path.read_text(encoding="utf-8"))
jsonschema.Draft202012Validator.check_schema(schema)
assert schema.get("$id") == "urn:cap:schema:transition-execution:v0.1", schema.get("$id")
V = jsonschema.Draft202012Validator(schema)
ex_path = ROOT / "examples" / "transition_execution_record_example.json"
ex = json.loads(ex_path.read_text(encoding="utf-8-sig"))

# 1. the example validates; its references exist; its input hash is the real hash; its revisions are the named ones
assert not list(V.iter_errors(ex)), [e.message for e in V.iter_errors(ex)]
for ref in (ex["candidate"]["candidate_ref"], ex["candidate"]["mirror_frame_before_ref"], ex["execution"]["receipt_ref"],
            ex["costs"]["estimated_ref"]):
    assert (ROOT / ref).is_file(), ref
assert ex["candidate"]["candidate_ref"] == "examples/adjustment_candidate_transition_example.json"
assert ex["candidate"]["mirror_frame_before_ref"] == "examples/mirror_frame_example.json"
assert ex["execution"]["receipt_ref"] == "examples/transition_execution_record/executor_receipt.json"
assert ex["costs"]["estimated_ref"] == ex["candidate"]["candidate_ref"]
assert len(ex["execution"]["inputs"]) >= 1
for item in ex["execution"]["inputs"]:
    assert (ROOT / item["ref"]).is_file(), item
    assert hashlib.sha256((ROOT / item["ref"]).read_bytes()).hexdigest() == item["sha256"], ("sha256 mismatch", item["ref"])
assert len(ex["checks"]) >= 1
for chk in ex["checks"]:
    assert (ROOT / chk["result_ref"]).is_file(), chk
    assert chk["revision_checked"] == "602fa63a42ac51b66af3f8d4157b1f1d9ceead8a"
assert ex["object"]["revision_before"] == "e65b9af4b28d3c97950c667448a32c24adc44a0e"
assert ex["object"]["revision_after"] == "602fa63a42ac51b66af3f8d4157b1f1d9ceead8a"
assert ex["observation_after"]["revision_after"] == ex["object"]["revision_after"]
assert ex["execution"]["actor"]["identity_independently_verified"] is False
assert ex["execution"]["actor"]["identity_source"] == "claude_cli_modelUsage"
assert ex["costs"]["measured"]["money"] == "unknown"
assert ex["verdict"]["postcondition_met"] is True and ex["verdict"]["provenance_established"] is True
crit_ids = {c["id"] for c in ex["postcondition"]["criteria"]}
assert {c["criterion_id"] for c in ex["checks"]} <= crit_ids
stand = ROOT / "examples" / "transition_execution_record"
assert sorted(p.name for p in stand.iterdir()) == ["check_result_c1.txt", "executor_receipt.json"], sorted(p.name for p in stand.iterdir())
rcpt = json.loads((stand / "executor_receipt.json").read_text(encoding="utf-8-sig"))
assert {"run_id", "decision", "model_requested", "model_served"} <= set(rcpt)
assert (stand / "check_result_c1.txt").read_text(encoding="utf-8").rstrip().endswith("1 passed")

# 2. schema-level invariants
bad = copy.deepcopy(ex); bad["checks"][0]["status"] = "fail"; bad["checks"][0]["exit_code"] = 1; bad["verdict"]["postcondition_met"] = True
assert list(V.iter_errors(bad)), "postcondition_met true with a failing check must be rejected"
bad = copy.deepcopy(ex); bad["execution"].pop("receipt_ref", None); bad["verdict"]["provenance_established"] = True
assert list(V.iter_errors(bad)), "provenance_established true without receipt_ref must be rejected"
bad = copy.deepcopy(ex); bad["execution"]["inputs"] = []; bad["verdict"]["provenance_established"] = True
assert list(V.iter_errors(bad)), "provenance_established true with no inputs must be rejected"
bad = copy.deepcopy(ex); bad["checks"][0]["exit_code"] = 1
assert list(V.iter_errors(bad)), "a passing check with exit_code 1 must be rejected"
bad = copy.deepcopy(ex); bad["postcondition"]["defined_before_execution"] = False
assert list(V.iter_errors(bad)), "defined_before_execution false must be rejected"
bad = copy.deepcopy(ex); del bad["costs"]["measured"]["money"]
assert list(V.iter_errors(bad)), "missing money must be rejected"
ok = copy.deepcopy(ex); ok["costs"]["measured"]["money"] = 0.25
assert not list(V.iter_errors(ok)), "a numeric money must be accepted"
bad = copy.deepcopy(ex); bad["costs"]["measured"]["money"] = "cheap"
assert list(V.iter_errors(bad)), "money 'cheap' must be rejected"
bad = copy.deepcopy(ex); del bad["execution"]["actor"]["identity_independently_verified"]
assert list(V.iter_errors(bad)), "identity_independently_verified is required"
bad = copy.deepcopy(ex); bad["extra"] = 1
assert list(V.iter_errors(bad)), "additionalProperties false at root"
bad = copy.deepcopy(ex); bad["checks"][0]["extra"] = 1
assert list(V.iter_errors(bad)), "additionalProperties false in a check"
bad = copy.deepcopy(ex); bad["checks"][0]["status"] = "maybe"
assert list(V.iter_errors(bad)), "status enum"
bad = copy.deepcopy(ex); bad["execution"]["inputs"][0]["sha256"] = "xyz"
assert list(V.iter_errors(bad)), "sha256 pattern"
bad = copy.deepcopy(ex); bad["postcondition"]["criteria"] = []
assert list(V.iter_errors(bad)), "criteria minItems 1"
bad = copy.deepcopy(ex); bad["schema_version"] = "0.2"
assert list(V.iter_errors(bad)), "schema_version const"
# an unresolvable reference is NOT a schema concern (documented boundary): the schema accepts it
bad = copy.deepcopy(ex); bad["candidate"]["candidate_ref"] = "examples/does_not_exist.json"
assert not list(V.iter_errors(bad)), "the schema alone cannot resolve references; that is the validator's job"

print("oracle_c1: all assertions hold")
