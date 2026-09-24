"""Ephemeral oracle for cap-execution-record-05b: the reference-resolving validator and its CLI.
Assumes spec/transition_execution.schema.json and examples/transition_execution_record_example.json exist
(added by 05a). Run from the repository root; exit 0 iff every assertion holds."""
import copy
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, "reference/python")
from cap.execution_record import validate_execution_record  # noqa: E402

ROOT = pathlib.Path(".").resolve()
ex = json.loads((ROOT / "examples" / "transition_execution_record_example.json").read_text(encoding="utf-8-sig"))

# 1. the example is sound: no problems, with and without the git check
assert validate_execution_record(ex, ROOT, ROOT) == [], validate_execution_record(ex, ROOT, ROOT)
assert validate_execution_record(ex, ROOT, None) == []

# 2. the operator's probe: an unresolvable reference passes the schema but the validator names it
bad = copy.deepcopy(ex); bad["candidate"]["candidate_ref"] = "examples/does_not_exist.json"
probs = validate_execution_record(bad, ROOT, ROOT)
assert probs and any("candidate_ref" in p and "does_not_exist" in p for p in probs), probs
bad = copy.deepcopy(ex); bad["execution"]["receipt_ref"] = "examples/nope.json"
assert any("receipt_ref" in p for p in validate_execution_record(bad, ROOT, ROOT))
bad = copy.deepcopy(ex); bad["checks"][0]["result_ref"] = "examples/nope.txt"
assert any("result_ref" in p for p in validate_execution_record(bad, ROOT, ROOT))
bad = copy.deepcopy(ex); bad["execution"]["inputs"][0]["ref"] = "examples/nope.json"
assert any("nope.json" in p for p in validate_execution_record(bad, ROOT, ROOT))

# 3. a wrong input hash is named
bad = copy.deepcopy(ex); bad["execution"]["inputs"][0]["sha256"] = "0" * 64
assert any("sha256" in p for p in validate_execution_record(bad, ROOT, ROOT))

# 4. unknown revisions are named when a repo is given, and not checked when it is not
bad = copy.deepcopy(ex); bad["object"]["revision_after"] = "0" * 40
assert any("revision" in p for p in validate_execution_record(bad, ROOT, ROOT))
assert validate_execution_record(bad, ROOT, None) == []
bad = copy.deepcopy(ex); bad["checks"][0]["revision_checked"] = "0" * 40
assert any("revision" in p for p in validate_execution_record(bad, ROOT, ROOT))
bad = copy.deepcopy(ex); bad["object"]["revision_before"] = "0" * 40
assert any("revision" in p for p in validate_execution_record(bad, ROOT, ROOT))

# 5. criterion coverage and identity
bad = copy.deepcopy(ex)
bad["postcondition"]["criteria"].append({"id": "c_extra", "statement": "an uncovered criterion", "check_command": "true"})
assert any("c_extra" in p for p in validate_execution_record(bad, ROOT, ROOT))
bad = copy.deepcopy(ex); bad["checks"][0]["criterion_id"] = "c_nonexistent"
assert any("c_nonexistent" in p for p in validate_execution_record(bad, ROOT, ROOT))

# 6. schema errors become problems, never exceptions
bad = copy.deepcopy(ex); bad["extra"] = 1
assert validate_execution_record(bad, ROOT, ROOT), "schema violation must be reported"
assert isinstance(validate_execution_record({}, ROOT, ROOT), list)
assert validate_execution_record({}, ROOT, ROOT)

# 7. the CLI: 0 on the example, non-zero on a broken copy, prints OK / problems
r = subprocess.run([sys.executable, "reference/python/scripts/validate_execution_record.py",
                    "examples/transition_execution_record_example.json", "--repo", "."],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
assert r.returncode == 0, r.stdout + r.stderr
assert "OK" in r.stdout
tmp = ROOT / "examples" / "_oracle_tmp_broken_record.json"
try:
    broken = copy.deepcopy(ex); broken["candidate"]["candidate_ref"] = "examples/does_not_exist.json"
    tmp.write_text(json.dumps(broken), encoding="utf-8")
    r2 = subprocess.run([sys.executable, "reference/python/scripts/validate_execution_record.py", str(tmp), "--repo", "."],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r2.returncode != 0
    assert "candidate_ref" in (r2.stdout + r2.stderr)
finally:
    if tmp.exists():
        tmp.unlink()

print("oracle_c2: all assertions hold")
