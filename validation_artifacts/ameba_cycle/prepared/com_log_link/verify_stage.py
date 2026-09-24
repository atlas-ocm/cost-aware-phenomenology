"""Deterministic verify stage for cap-com-log-link-04 (driver-written, outside the tree).

Same shape as verify_stage3.py: packet from the coding receipt, the diff, the oracle text and a recheck of
the declared checks; verifier chosen deterministically and never the coding model.
"""
import json, os, pathlib, subprocess, sys, time
SCR = pathlib.Path(__file__).resolve().parent
REPO = "F:/VibeCoding/CAP-wt-ameba-cycle"
TASK = "cap-com-log-link-04"
ORACLE = SCR / "oracle_link.py"
CHECKS = [
    ["python", "-B", str(ORACLE).replace("\\", "/")],
    ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "reference/python/tests/test_candidate_gate.py",
     "reference/python/tests/test_adjustment_layer_schema.py", "reference/python/tests/test_schemas_valid.py"],
    ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "reference/python/tests/test_budget_calculus.py"],
]

rec_path = SCR / "out_coding" / f"{TASK}.json"
if not rec_path.exists():
    print(json.dumps({"stage": "verify", "status": "NO_CODING_RECEIPT", "path": str(rec_path)}))
    sys.exit(0)
rec = json.loads(rec_path.read_text(encoding="utf-8"))

def git(*a):
    return subprocess.run(["git", "--no-pager", *a], cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout

diff = git("diff"); stat = git("diff", "--stat"); names = git("diff", "--name-only")
untracked = git("ls-files", "--others", "--exclude-standard")
untracked_content = ""
for rel in [u for u in untracked.splitlines() if u.strip()]:
    p = pathlib.Path(REPO) / rel
    if p.is_file():
        untracked_content += f"\n--- new file {rel} ---\n" + p.read_text(encoding="utf-8", errors="replace")
verifier = "glm53_flash" if rec.get("fallback_used") else "deepseek_v41_flash"

def att(a):
    if not a:
        return None
    keep = ("model_requested", "model_served", "provider", "model_identity_status",
            "wall_s", "turns", "output_tokens", "postcondition", "checks")
    return {k: a.get(k) for k in keep}

reported = {"decision": rec.get("decision"), "fallback_used": rec.get("fallback_used"),
            "seam_used": rec.get("seam_used"), "final_postcondition": rec.get("final_postcondition"),
            "baseline_checks": rec.get("baseline"), "first_attempt": att(rec.get("first_attempt")),
            "fallback_attempt": att(rec.get("fallback_attempt")), "trail": rec.get("trail")}

env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
rechecks = []
for cmd in CHECKS:
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    rechecks.append({"cmd": " ".join(cmd), "exit": p.returncode, "tail": (p.stdout + p.stderr).strip()[-600:]})

packet = [{"id": f"{TASK}-verify", "packet": {
    "question": ("Does this change add only an optional com_log_ref (string, minLength 1) to adjustment_step in "
                 "spec/adjustment_layer.schema.json, a new module cap/candidate_gate.py whose gate_candidate_step(step, "
                 "com_log, active_operator_risks, risk_weight_source) reads the gate inputs from the linked COM-Log record "
                 "and the cycle state, records risk_weight_source and estimate_status without upgrading an assignment to a "
                 "measurement, returns not_computed with a reason for any missing link or input, never returns admissible "
                 "without every input, marks numeric_pass_is_full_admissibility False with the three unchecked items, and "
                 "otherwise delegates to operator_admissibility with the lowercased telemetry state; plus tests; with no docs, "
                 "examples, other spec files or other modules touched?"),
    "postcondition": {"value": ("The driver's oracle (evidence carrier oracle_link.py) exits 0; the three declared pytest "
                                "checks exit 0; changed files are exactly spec/adjustment_layer.schema.json, "
                                "reference/python/tests/test_adjustment_layer_schema.py and the two new files "
                                "reference/python/cap/candidate_gate.py and reference/python/tests/test_candidate_gate.py; "
                                "the worked example still validates; existing tests unchanged in meaning.")},
    "reported": reported,
    "evidence": [
        {"path": "git diff --stat", "content": stat or "(empty)"},
        {"path": "git diff --name-only", "content": names or "(empty)"},
        {"path": "git ls-files --others --exclude-standard", "content": untracked or "(none)"},
        {"path": "git diff", "content": diff or "(empty)"},
        {"path": "new files (untracked) full content", "content": untracked_content or "(none)"},
        {"path": "oracle_link.py (driver's ephemeral check, outside the tree)", "content": ORACLE.read_text(encoding="utf-8")},
        {"path": "recheck: the declared checks re-run by this stage on the current tree", "content": json.dumps(rechecks, indent=1)},
    ]}}]
(SCR / "packets4.json").write_text(json.dumps(packet, indent=1, ensure_ascii=False), encoding="utf-8")

out = SCR / "out_verdicts"
cmd = [sys.executable, os.path.expanduser("~/.claude/nomcp/nomcp.py"), "verdicts", str(SCR / "packets4.json"),
       str(out), "--verifier", verifier, "--deadline", "480"]
t0 = time.monotonic()
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
summary = {"stage": "verify", "verifier": verifier, "rechecks": rechecks, "shim_exit": r.returncode,
           "wall_s": round(time.monotonic() - t0, 1), "stdout_tail": r.stdout[-800:], "stderr_tail": r.stderr[-800:]}
vp = out / f"{TASK}-verify.json"
if vp.exists():
    v = json.loads(vp.read_text(encoding="utf-8"))
    summary["verdict_receipt"] = {k: v.get(k) for k in ("id", "model", "verdict", "reason", "issues", "cited",
                                                        "missing", "final_error_kind", "attempts", "wall_s", "timeout_s")}
print(json.dumps(summary, indent=1, ensure_ascii=False))
