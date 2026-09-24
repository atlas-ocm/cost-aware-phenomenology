"""Oracle for the record-builder script (driver-written, deterministic, no model calls). The same oracle is the
postcondition of both paths of the Adjustment comparison (run 010).

usage: python probe_build_record.py <repo_root> [--expect-closed]

Expects reference/python/scripts/build_execution_record.py with the CLI
    build_execution_record.py <repo_root> <run_dir_rel> <spec_json> --out <path>
that builds a schema-0.2 executed-transition record from a run directory and a record spec, validates it
against <repo_root> (references, hashes, git revisions, coverage and the binding rules) and exits 0 only
when it built the record and the validator returned no problem; exit 2, naming the file, when a stored
check result does not hold exactly one exit= line or a required artifact is missing.

Cases (each an expectation; --expect-closed exits 0 only when all hold; on the baseline the script does not
exist, so the first case fails for that named reason):
  c1 build:        the script rebuilds run 009's record into a scratch file and exits 0;
  c2 equality:     the rebuilt record equals the committed run 009 record as JSON (key order irrelevant);
  c3 validity:     validate_execution_record(rebuilt, repo_root, repo_root) returns no problem;
  c4 exit line:    on a copy of the run directory whose c1 result file lost its exit= line, the script exits 2
                   and names that file.
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

repo = pathlib.Path(sys.argv[1]).resolve()
expect_closed = "--expect-closed" in sys.argv
sys.path.insert(0, str(repo / "reference" / "python"))
from cap.execution_record import validate_execution_record  # noqa: E402

SCRIPT = repo / "reference" / "python" / "scripts" / "build_execution_record.py"
RUN = "validation_artifacts/ameba_cycle/run_009_route_costs"
SPEC = f"{RUN}/record_spec.json"
COMMITTED = repo / RUN / "transition_execution_record.json"
scratch = pathlib.Path(tempfile.mkdtemp(prefix="cap-probe-build-"))
results = []


def report(label, holds, detail):
    results.append(holds)
    print(f"case={label} holds={holds} detail={json.dumps(detail, ensure_ascii=True)[:400]}")


def run(args, cwd):
    return subprocess.run([sys.executable, "-B", str(SCRIPT), *args], cwd=str(cwd), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


out = scratch / "rebuilt.json"
if not SCRIPT.is_file():
    report("c1_build", False, {"reason": "script does not exist", "path": str(SCRIPT)})
    rebuilt = None
else:
    p = run([str(repo), RUN, SPEC, "--out", str(out)], repo)
    ok = p.returncode == 0 and out.is_file()
    report("c1_build", ok, {"exit": p.returncode, "stdout_tail": p.stdout[-300:], "stderr_tail": p.stderr[-300:]})
    rebuilt = json.loads(out.read_text(encoding="utf-8-sig")) if ok else None

if rebuilt is None:
    report("c2_equality", False, {"reason": "nothing built"})
    report("c3_validity", False, {"reason": "nothing built"})
else:
    committed = json.loads(COMMITTED.read_text(encoding="utf-8-sig"))
    report("c2_equality", rebuilt == committed, {"equal": rebuilt == committed,
           "differing_top_level_keys": [k for k in set(rebuilt) | set(committed) if rebuilt.get(k) != committed.get(k)]})
    problems = validate_execution_record(rebuilt, repo, repo)
    report("c3_validity", not problems, {"problems": problems[:5]})

# c4: a copy of the run directory under a scratch base whose c1 result lost its exit= line
base = scratch / "base"
dst = base / RUN
shutil.copytree(repo / RUN, dst)
c1 = next((f for f in sorted((dst / "checks").glob("c1*.txt"))), None)
if SCRIPT.is_file() and c1 is not None:
    text = c1.read_text(encoding="utf-8", errors="replace")
    c1.write_text("\n".join(line for line in text.splitlines() if not line.startswith("exit=")) + "\n", encoding="utf-8")
    p = run([str(base), RUN, SPEC, "--out", str(scratch / "rebuilt_bad.json")], repo)
    named = c1.name in (p.stdout + p.stderr)
    report("c4_exit_line_named", p.returncode == 2 and named,
           {"exit": p.returncode, "names_file": named, "stdout_tail": p.stdout[-200:], "stderr_tail": p.stderr[-200:]})
else:
    report("c4_exit_line_named", False, {"reason": "script missing or no c1 result in the run copy"})

shutil.rmtree(scratch, ignore_errors=True)
all_hold = all(results)
if expect_closed:
    print("probe_build_record: " + ("every expectation holds" if all_hold else "at least one expectation fails"))
    sys.exit(0 if all_hold else 1)
print("probe_build_record: observation mode, exit 0")
