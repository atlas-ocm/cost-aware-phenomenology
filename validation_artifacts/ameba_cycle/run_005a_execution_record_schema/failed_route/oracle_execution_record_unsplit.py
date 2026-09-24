"""Ephemeral, packet-local oracle for cap-execution-record-05 (driver-written, outside the tree).

Assertions come from the operator's statement of 2026-09-24: an executed transition must bind (1) the observed
B, the object and its revision, the chosen candidate and a postcondition defined before execution; (2) who,
with which tool and inputs, actually executed, and the stored call result; (3) a re-observation of the same
object and a check of every criterion on the obtained state with references to the actual check results;
(4) divergence fed back and measured costs kept apart from estimates. The operator's probe (a pass record with
unresolvable references passes JSON Schema) becomes an assertion: the schema alone accepts it, the validator
rejects it. Run from the repository root.
"""
import copy
import hashlib
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, "reference/python")
import jsonschema  # noqa: E402
from cap.execution_record import validate_execution_record  # noqa: E402

ROOT = pathlib.Path(".").resolve()
schema = json.load(open("spec/transition_execution.schema.json", encoding="utf-8"))
jsonschema.Draft202012Validator.check_schema(schema)
V = jsonschema.Draft202012Validator(schema)
ex = json.load(open("examples/transition_execution_record_example.json", encoding="utf-8-sig"))

# 1. the example validates and every reference, hash and revision resolves
assert not list(V.iter_errors(ex)), [e.message for e in V.iter_errors(ex)]
assert validate_execution_record(ex, ROOT, ROOT) == [], validate_execution_record(ex, ROOT, ROOT)
for ref in (ex["candidate"]["candidate_ref"], ex["candidate"]["mirror_frame_before_ref"], ex["execution"]["receipt_ref"],
            ex["costs"]["estimated_ref"]):
    assert (ROOT / ref).is_file(), ref
for item in ex["execution"]["inputs"]:
    assert hashlib.sha256((ROOT / item["ref"]).read_bytes()).hexdigest() == item["sha256"], item
for chk in ex["checks"]:
    assert (ROOT / chk["result_ref"]).is_file(), chk

# 2. the operator's probe: an unresolvable reference passes the schema and fails the validator
bad = copy.deepcopy(ex); bad["candidate"]["candidate_ref"] = "examples/does_not_exist.json"
assert not list(V.iter_errors(bad))
probs = validate_execution_record(bad, ROOT, ROOT)
assert probs and any("candidate_ref" in p for p in probs), probs

# 3. a wrong input hash is rejected by the validator
bad2 = copy.deepcopy(ex); bad2["execution"]["inputs"][0]["sha256"] = "0" * 64
assert any("sha256" in p for p in validate_execution_record(bad2, ROOT, ROOT))

# 4. an unknown revision is rejected by the validator (git-backed)
bad3 = copy.deepcopy(ex); bad3["object"]["revision_after"] = "0" * 40
assert any("revision" in p for p in validate_execution_record(bad3, ROOT, ROOT))
bad3b = copy.deepcopy(ex); bad3b["checks"][0]["revision_checked"] = "0" * 40
assert any("revision" in p for p in validate_execution_record(bad3b, ROOT, ROOT))

# 5. postcondition_met true with a failing check is rejected by the schema itself
bad4 = copy.deepcopy(ex); bad4["checks"][0]["status"] = "fail"; bad4["checks"][0]["exit_code"] = 1
bad4["verdict"]["postcondition_met"] = True
assert list(V.iter_errors(bad4))

# 6. a criterion without any passing check cannot be postcondition_met (validator)
bad5 = copy.deepcopy(ex)
bad5["postcondition"]["criteria"].append({"id": "c_extra", "statement": "an uncovered criterion", "check_command": "true"})
assert any("c_extra" in p for p in validate_execution_record(bad5, ROOT, ROOT))

# 7. a check that names an unknown criterion is rejected (validator)
bad5b = copy.deepcopy(ex); bad5b["checks"][0]["criterion_id"] = "c_nonexistent"
assert any("c_nonexistent" in p for p in validate_execution_record(bad5b, ROOT, ROOT))

# 8. provenance_established true requires a receipt reference and at least one hashed input (schema)
bad6 = copy.deepcopy(ex); bad6["execution"].pop("receipt_ref", None); bad6["verdict"]["provenance_established"] = True
assert list(V.iter_errors(bad6))
bad6b = copy.deepcopy(ex); bad6b["execution"]["inputs"] = []; bad6b["verdict"]["provenance_established"] = True
assert list(V.iter_errors(bad6b))

# 9. a passing check must have exit code 0 (schema); postcondition is locked as defined before execution
bad7 = copy.deepcopy(ex); bad7["checks"][0]["exit_code"] = 1
assert list(V.iter_errors(bad7))
bad8 = copy.deepcopy(ex); bad8["postcondition"]["defined_before_execution"] = False
assert list(V.iter_errors(bad8))

# 10. measured costs are kept apart from estimates: money is required and is "unknown" or a number
bad9 = copy.deepcopy(ex); del bad9["costs"]["measured"]["money"]
assert list(V.iter_errors(bad9))
ok9 = copy.deepcopy(ex); ok9["costs"]["measured"]["money"] = "unknown"
assert not list(V.iter_errors(ok9))
bad9b = copy.deepcopy(ex); bad9b["costs"]["measured"]["money"] = "cheap"
assert list(V.iter_errors(bad9b))
assert ex["costs"]["estimated_ref"] == ex["candidate"]["candidate_ref"]

# 11. identity provenance is explicit and never implied
assert ex["execution"]["actor"]["identity_independently_verified"] is False
bad10 = copy.deepcopy(ex); del bad10["execution"]["actor"]["identity_independently_verified"]
assert list(V.iter_errors(bad10))

# 12. additionalProperties is false at the root and inside checks
bad11 = copy.deepcopy(ex); bad11["extra"] = 1
assert list(V.iter_errors(bad11))
bad12 = copy.deepcopy(ex); bad12["checks"][0]["extra"] = 1
assert list(V.iter_errors(bad12))

# 13. the CLI exits 0 on the example and non-zero on a broken copy
r = subprocess.run([sys.executable, "reference/python/scripts/validate_execution_record.py",
                    "examples/transition_execution_record_example.json", "--repo", "."],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
assert r.returncode == 0, r.stdout + r.stderr
tmp = pathlib.Path("examples") / "_oracle_tmp_broken_record.json"
try:
    tmp.write_text(json.dumps(bad), encoding="utf-8")
    r2 = subprocess.run([sys.executable, "reference/python/scripts/validate_execution_record.py", str(tmp), "--repo", "."],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r2.returncode != 0
finally:
    if tmp.exists():
        tmp.unlink()

print("oracle_execution_record: all assertions hold")
