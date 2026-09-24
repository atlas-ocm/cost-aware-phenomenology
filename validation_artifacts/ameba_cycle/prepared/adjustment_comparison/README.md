# Run 010 — Adjustment against a fixed baseline path: design fixed before either route runs

Status: design only, written before any packet of this comparison was routed. It
answers the operator's step 3 of 2026-09-25: fix the baseline path, the same
required postcondition and the full-cost method beforehand, then compare.

## 0. The question

Does the Adjustment layer (Mirror Frame → CandidateTransition → packet informed by
them) help reach the same verified postcondition at a lower full cost than the
executor route alone? One pair of runs is a probe, not a result.

## 1. The subject change (the same for both paths)

A repository script `reference/python/scripts/build_execution_record.py` that
builds a schema-0.2 executed-transition record from a run directory and a record
spec, so that any driver (the cloud included) can produce records without this
session's scratch tools. Inputs on the branch: the run directory of run 009
(`mirror_frame.json`, `candidate_transition.json`, `coding_packet.json`,
`nomcp_coding_receipt.json`, `nomcp_verdict_receipt.json`, `checks/*.txt`) and its
`record_spec.json` (the spec the driver used, committed with run 009).

## 2. The postcondition (identical for both paths, defined here)

Oracle `validation_artifacts/ameba_cycle/prepared/adjustment_comparison/probe_build_record.py <repo_root> [--expect-closed]`:

1. `python reference/python/scripts/build_execution_record.py <repo_root> validation_artifacts/ameba_cycle/run_009_route_costs validation_artifacts/ameba_cycle/run_009_route_costs/record_spec.json --out <scratch>/rebuilt.json` exits 0;
2. the rebuilt record, loaded as JSON, equals the committed
   `run_009_route_costs/transition_execution_record.json` loaded as JSON (deep
   equality; key order irrelevant);
3. `validate_execution_record(rebuilt, repo_root, repo_root)` returns no problems;
4. the script exits non-zero and names the file when a check result has no single
   `exit=` line (probe: a copy of the run dir with one result file truncated).

Declared checks for both packets: the oracle with `--expect-closed`; the full
suite (`python -m pytest -q -p no:cacheprovider reference/python/tests`); and
`git status --porcelain` limited to the one new file (checked by the driver on
the diff, not by the router). Both packets forbid touching anything but the new
script. Red on the baseline for the named reason: the script does not exist.

## 3. The two paths (fixed here)

- **A — baseline, executor route alone.** Packet A states the goal, the CLI
  shape (`<repo_root> <run_dir_rel> <spec_json> --out <path>`), the existence of
  the schema, the validator and the run-009 artifacts, and the declared checks.
  It does not enumerate derivation rules, does not carry observed facts, does not
  state forbidden outcomes beyond the file scope. No Mirror Frame, no
  CandidateTransition.
- **B — Adjustment path.** A Mirror Frame observes the run-009 artifacts and the
  validator's rules (how exit codes, commands, revisions, inputs, attempts, totals
  and the closing attempt are derived; the spec's keys; the output newline and
  encoding), a CandidateTransition states the success criteria, forbidden
  outcomes and the risk estimate, and packet B is packet A plus an "observed
  environment" section derived from the Mirror Frame and the candidate's
  forbidden outcomes. Same checks, same oracle, same file scope.

Both packets are written and committed before either route runs; B is not
informed by A's result. Both run from the same commit, each in its own detached
worktree (`F:/VibeCoding/CAP-wt-cmp-A`, `F:/VibeCoding/CAP-wt-cmp-B`), through
the same NoMCP mode-1 route (cheap_coder first, fallback on a measured failure)
inside the path B relay, A first, then B; each with its own out dir and the same
verify stage (an admitted verifier that is not the coding model).

## 4. The full-cost method (fixed here)

Per path, in their own units, never summed across units:

- route: every attempt (turns, output tokens, wall) and the router's total wall,
  from the receipt (bound by rules 5–6 once step 2 lands);
- verifier wall, from the verdict receipt;
- relay: subagent tokens and Workflow wall, from the Workflow usage line;
- driver: wall of authoring the packet (A) or the Mirror Frame + candidate +
  packet (B), measured with timestamps; wall of the re-observation checks;
- set-aside attempts and driver interventions counted, not costed;
- money: unknown.

## 5. The five axes of the brief, and what counts

1. postcondition met and constraints violated: oracle exit, file scope, forbidden
   outcomes;
2. unverified completion claims: the worker's final answer against the checks;
3. interventions, retries, regressions, rollbacks: attempts, set-asides, driver
   repacketing (none allowed inside a path: a failed route is a failed path);
4. time and tokens: section 4;
5. new evidence: what each receipt and record adds that the other does not.

## 6. Hypotheses stated beforehand

- H1: path B closes with fewer attempts and lower route cost than A, because the
  two cheap closes of this project (runs 008, 009) came on packets that named every
  rule and file, and the five one-detail misses came on packets that left details
  to the worker.
- H0: no difference beyond noise; then the pair shows only that B's extra
  authoring cost bought nothing on this task.
- Either way one pair does not establish a rate. The comparison is recorded as
  two 0.2 execution records plus this README; no layer is declared "useful" from it.
