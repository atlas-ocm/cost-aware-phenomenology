# Run 005 — the executed-transition record (schema half, 005a)

Status: `recorded run / research-only`. The change that introduces the
binding the operator asked for: one machine-checkable record per executed
transition. It was routed in two halves after the unsplit task exceeded the
fallback worker's wall; this directory is the schema half (`005a`), the
validator half is `run_005b_execution_record_validator/`. Both share the same
Mirror Frame and CandidateTransition (`mirror_frame.json`,
`candidate_transition.json`, proposed before any worker ran).

## 1. Initial state and the input available before the choice

- Tree at `989a7e2`, clean, pushed; full suite `941 passed, 2 skipped`.
- Declared state (`source: user`): the operator's analysis and probe — a
  Release Gate `pass` with unresolvable references and a Mirror Frame without
  `evidence_ref` both pass JSON Schema; the next end-to-end step must bind the
  observed state and object revision, the candidate and its pre-defined
  postcondition, the execution (who, tool, inputs, stored result), the
  re-observation and per-criterion checks with references to actual results,
  the divergence fed back and the measured costs kept apart from estimates.
- Observed: no schema or code binds an executed transition to a revision, an
  executor call and resolvable check results; the run records of 001–004 keep
  the artifacts but link them in prose only.

## 2. Proposed transition

`candidate_transition.json`: mode `repair`, additive; a new schema
(`spec/transition_execution.schema.json`), a resolving validator
(`cap/execution_record.py`), a CLI, a worked example with two stand-in files,
tests; existing layer schemas untouched. `loop_risk` was estimated the
highest axis (0.15): "a schema-plus-validator task has many named parts and a
cheap worker may miss one". That is what happened.

## 3. Action actually executed and objects changed

Four routes were needed (all NoMCP mode 1: cheap_coder `gemma4:31b-cloud`,
fallback `deepseek-v4.1-flash:cloud`, declared checks, driver's oracle
outside the tree, red on the baseline):

| route | shape | cheap tier | fallback | outcome |
|---|---|---|---|---|
| 1 | unsplit task, inside a native Workflow with a Haiku relay | attempt set aside (no receipt survives) | started, wrote nothing | the relay's Bash tool ceiling (600 s) moved the call to background; the relay tried a second Bash to wait and our own one-Bash hook denied it; the harness then killed the route; **no receipt**, orphaned stash; Verify relay: `NO_CODING_RECEIPT` (`failed_route/`, Workflow 630.9 s, 21,036 relay tokens) |
| 2 | unsplit task, direct through the shim, detached | 29 turns, 14,589 tokens, 67.6 s: oracle failed (`load_schema("transition_execution")` looked for `spec/transition_execution.json`), 7 of 17 tests failed, two stray helper scripts left in the tree | wall timeout 600 s | `EXCEPTION` (`failed_route/nomcp_coding_receipt_exception.json`) |
| 3 | split: schema half (`05a`), direct | 46 turns, 9,488 tokens, 56.1 s: everything green except the example's input `sha256` (16 of 17 tests) | wall timeout 600 s | `EXCEPTION` |
| 4 | schema half with the exact byte hash given as an environment fact | see `nomcp_coding_receipt.json` | see receipt | see receipt and section 4 |

Objects changed by the closing route: `spec/transition_execution.schema.json`,
`examples/transition_execution_record_example.json`,
`examples/transition_execution_record/{executor_receipt.json,check_result_c1.txt}`,
`reference/python/tests/test_transition_execution_schema.py`.

## 4. Observed result, postcondition check, costs

See `transition_execution_record.json` (this run's own record, built with
the validator from `005b` and validated on the tree that contains it) and
`checks/` (each criterion re-run by the driver at the obtained revision in a
detached worktree). Costs of the closing route are in the receipt and the
record; the three failed routes' costs are in `failed_route/` and this table
and are not summed with them. Money: unknown.

## 5. Divergence between expectation and result; Adjustment

- Expected: one bounded task closes at the cheap tier or the fallback.
  Observed: the task, as first cut, was too large for either — the cheap tier
  missed one detail each time (a schema file name; a byte hash) and the
  fallback did not finish inside its 600 s wall twice. Adjustments, by the
  driver, in order: (1) run the route detached after the relay ceiling
  killed it (a transport change, not a change of executor or checks);
  (2) split the task into the schema half and the validator half, each with
  its own oracle; (3) give the cheap worker the one environment fact it kept
  getting wrong (the input file's byte hash) instead of asking it to compute
  it. No oracle was weakened and no code was written by the driver.
- Three harness facts recorded for the NoMCP journal (confirmed and measured
  by that session without a coding model, and answered on its master by an
  in-flight state record, `d0d9b6c`): a coding route that escalates cannot be
  hosted by a one-Bash relay under the 600 s tool ceiling; a route killed
  mid-flight leaves no receipt, only an orphaned stash; and this session's
  Workflow script opened its Verify stage on the relay's return rather than
  on a final receipt of the same run, so Verify ran against nothing. Which
  transport to adopt (a raised ceiling for that one process, or a launch-then-
  wait rule) is the operator's decision; nothing was changed in policy here.
- What this run says about the cycle: the record format now exists so that
  "the required state exists" and "this execution led to it" are both
  checked by code; what it does not say is anything about Adjustment choosing
  a cheaper transition — that comparison is still to be run.

## Corrections

- correction_001 (2026-09-24, after the review of `26535dc`; see run 007):
  `costs.measured` in `transition_execution_record.json` holds the closing
  attempt only (38 turns, 21,688 output tokens, 90.34 s). The whole route from the same
  receipt is 48 turns, 28,094 output tokens, 132.34 s of router wall, verifier 38.8 s (the three failed routes in `failed_route/` and the table in section 3 come on top and are not summed with them);
  see `../route_costs_correction_001.json`. For comparing transitions the
  whole route is the figure. The record is left as written: its schema has
  no place for route totals (`CAP_CLOUD_HANDOFF.md` section 7).
- correction_002 (same date): `execution.tool` said "one native Workflow with
  one nomcp-haiku relay per stage"; this coding route ran detached through
  the shim, only the verdict stage was relayed. Corrected in place; the
  original wording is in commit `1db22cf`.
- correction_003 (same date): `execution.inputs[0]` hashes the stored
  `coding_packet.json` (LF, 8,271 bytes, `9b0f0bd6...`); the router hashed
  the packet it was given, `tasks5a.json` with CRLF line endings (8,296
  bytes, `08111685...`, the receipt's `inputs.packet.sha256`). Same text,
  different bytes: the copy was normalised on copy and `.gitattributes`
  would normalise it on staging anyway. The record is internally consistent
  and not bound to the executed bytes; the binding rule prepared in run 007
  refuses it, as intended. Left as written.
- correction_004 (same date, after the review of `8bc15b5`): the executed
  bytes of the packet are now on the branch as
  `coding_packet.executed.08111685.json` (the router's retained copy from
  its out dir, `inputs/<sha>`), with a `-text` entry in `.gitattributes` for
  that exact path so neither staging nor checkout converts its line
  endings; blob and fresh-checkout bytes verified (8,296 bytes, sha256
  `08111685...`). The driver's `tasks5a.json` is byte-identical (same sha)
  and is not duplicated. The record above is kept unchanged as the negative
  control of binding rule 4(c): it pins the detection of the mismatch, not a
  permanent refusal of this run; a corrected record that references the
  stored executed bytes may pass and would be a separate file, with this
  correction history kept here.
- correction_005 (2026-09-25, with run 008): the corrected record
  `transition_execution_record_corrected_001.json` exists beside the original;
  it differs only in `execution.inputs[0]` (the stored executed bytes, sha256
  `08111685...`), its record id and its reasons/notes, and it resolves under the
  validator at `fc87e62`. The original record is refused there naming input
  `9b0f0bd6...`, and is kept as the negative control.
