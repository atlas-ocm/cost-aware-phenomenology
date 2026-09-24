# Run 005b — the executed-transition record (validator half)

Status: `recorded run / research-only`. Second half of run 005: the
reference-resolving validator (`reference/python/cap/execution_record.py`),
its CLI (`reference/python/scripts/validate_execution_record.py`) and their
tests. The schema, the example and the story of the unsplit attempts are in
`run_005a_execution_record_schema/` (same Mirror Frame and
CandidateTransition, copied here).

## 1–2. State before, proposed transition

Tree after `336af16` (schema half), clean; full suite `961 passed, 2 skipped`.
The candidate is the one of run 005; this half closes the part the operator's
probe was about: a record whose references do not exist must be rejected by
code, not accepted by schema.

## 3. Action actually executed

NoMCP mode 1, direct through the shim (detached), declared checks: the
driver's oracle (`oracle_c2.py`, red on the baseline with
`ModuleNotFoundError: cap.execution_record`), the validator and schema
tests, the schema-validity and adjustment tests.

| stage | model (identity per CLI report, not independently verified) | turns | output tokens | wall s | outcome |
|---|---|---|---|---|---|
| cheap_coder | `gemma4:31b-cloud` | 9 | 4,246 | 22.4 | oracle failed: the CLI script did not put `reference/python` on `sys.path` (`ModuleNotFoundError: No module named 'cap'`); 26 of 27 tests passed; set aside (stash `964c0377`, local only) |
| fallback_coder | `deepseek-v4.1-flash:cloud` | 48 | 40,578 | 177.8 | oracle exit 0; 40 + 46 tests passed; `FALLBACK_PASS` |

Objects changed: exactly the three new files; no tracked file modified.

## 4. Observed result, postcondition check, costs

See `transition_execution_record.json` (validated by the validator it
describes, on the tree that contains it) and `checks/`: c1–c4 re-run by the
driver at the obtained revision in a detached worktree; c5 = the CLI of this
revision accepting the real records of runs 004 and 002, which closes the
operator's acceptance item "at least one candidate passes the whole chain to
a verified postcondition" on records of real transitions. Costs in the
receipt and the record; money unknown.

## 5. Divergence; Adjustment

- Expected: the cheap tier closes a three-file task with a spelled-out
  contract. Observed: it missed one line (the script's `sys.path`), as it
  missed one detail in every attempt of this evening; the fallback closed
  it. No Adjustment by a model; the router's policy applied; no oracle was
  weakened; no code was written by the driver.
- The CLI on the operator's probe (unresolvable reference, wrong hash,
  unknown revision on a copy of the example) exits non-zero and names each
  problem; the same copy passes JSON Schema. That is the boundary this run
  closes.

## Corrections

- correction_001 (2026-09-24, after the review of `26535dc`; see run 007):
  `costs.measured` in `transition_execution_record.json` holds the closing
  attempt only (48 turns, 40,578 output tokens, 177.84 s). The whole route from the same
  receipt is 57 turns, 44,824 output tokens, 213.25 s of router wall, verifier 36.3 s;
  see `../route_costs_correction_001.json`. For comparing transitions the
  whole route is the figure. The record is left as written: its schema has
  no place for route totals (`CAP_CLOUD_HANDOFF.md` section 7).
- correction_002 (same date): `execution.tool` said "one native Workflow with
  one nomcp-haiku relay per stage"; this coding route ran detached through
  the shim, only the verdict stage was relayed. Corrected in place; the
  original wording is in commit `1db22cf`.
