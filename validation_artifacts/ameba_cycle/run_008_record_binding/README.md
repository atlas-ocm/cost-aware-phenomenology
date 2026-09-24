# Run 008 — the execution record bound to its stored carriers

Status: `recorded run / research-only`. The reviewer's step 1 of 2026-09-25,
executed from the packet prepared in run 007 (`coding_packet.json` here is
that packet with the local paths filled in; `baseline_oracle.txt` is the
oracle on the clean tree before the route).

The operator asked to keep the statuses apart. They are:

| status of | value | source |
|---|---|---|
| the route | `CHEAP_PASS` — the cheap tier closed it on its first attempt | `nomcp_coding_receipt.json` |
| the verdict | `ACCEPT` by `deepseek_v41_flash` (never the coding model), 19.7 s | `nomcp_verdict_receipt.json` |
| the checks | six criteria re-run by the driver at `fc87e62` in a detached worktree, all `exit=0` | `checks/` |
| the acceptance | accepted by the driver on the diff (section 4) | this README, `transition_execution_record.json` |
| the transport (path B) | installed relay text used; the launch completed in the foreground (71.3 s), so the wait mechanism was **not** exercised | Workflow transcript, section 3 |

## 1. Initial state and the input available before the choice

- Tree at `5a5e2e9`, clean, pushed; full suite `1004 passed, 2 skipped` at
  `ebe0ba0` with no code change since (`mirror_frame.json`; declared state
  `source: user` = the operator's instruction of 2026-09-25: execute the
  prepared packet through the installed NoMCP path B, keep the old run 005a
  record as the negative control, a corrected separate record may pass).
- Observed: the validator at `8d23161` resolves references, hashes,
  revisions and coverage and never opens a stored result; the oracle
  (revision 2) on the clean tree exits 1 with five gap cases accepted and four
  expectations holding (`baseline_oracle.txt`).

## 2. Proposed transition

`candidate_transition.json`: mode `repair`; four comparisons over carriers
that already exist plus the two example stand-ins; `loop_risk` estimated the
highest axis (0.25) after five one-detail misses of the cheap tier the
evening before. Proposed before the route was launched.

## 3. Action actually executed

One native Workflow (`cap-record-binding-nomcp`), two `nomcp-haiku` relays,
model-pin check 2/2 Haiku (`workflow_models.py`). Implement relay: exactly
one Bash call, the launch of `nomcp.py coding` through the shim; the relay
prompt carried the path B wait command for the case that the harness moves
the launch to the background. That case did not occur: the route finished in
the foreground. Declared checks: the committed probe with `--expect-closed`
(declared by hash in `check_files`), the validator and schema tests, run
006's record. Verify relay: the deterministic packet builder chose
`deepseek_v41_flash` (no fallback was used) and returned the verdict
receipt verbatim.

| stage | model (identity per CLI report, not independently verified) | turns | output tokens | wall s | outcome |
|---|---|---|---|---|---|
| baseline (router, no model) | — | — | — | — | oracle exit 1, tests exit 0, run 006 record exit 0: red for the named reason only |
| cheap_coder | `gemma4:31b-cloud` | 12 | 9,315 | 58.49 | all three declared checks exit 0; `CHEAP_PASS` |
| verifier | `deepseek-v4.1-flash:cloud` (no fallback was used, so not `glm53_flash`) | — | — | 19.7 | `ACCEPT`, six files cited, no issues |

Route wall (router `total_wall_s`): 71.31 s. Workflow: 147.9 s, 21,163 relay
tokens. Objects changed: `reference/python/cap/execution_record.py` (+145),
`reference/python/tests/test_execution_record_validator.py` (+80, seven
tests), `examples/transition_execution_record/check_result_c1.txt` (exit
line), `examples/transition_execution_record/executor_receipt.json` (router
shape). Nothing else; the probe untouched (`oracle_paths_changed: null`, not
in `touched`).

## 4. Observed result, postcondition check, costs

See `transition_execution_record.json` and `checks/`. Driver adjudication on
the diff: rule 1 reads exactly one `^exit=(-?\d+)$` line; rule 2 is string
equality of the command with the criterion; rule 3 resolves through
`git rev-parse` after `cat-file -e` and compares resolved SHAs, only with a
repository; rule 4 reads `decision`, the closing attempt's `model_served`
chosen by `fallback_used`, and the packet / check_files hashes, and nothing
else; every existing check and problem string is unchanged (the diff only
adds). Cosmetic, not a defect: `import re` sits inside the rule-1 loop.
Consequences on the tree: the original run 005a record is refused with
`execution.receipt_ref: input 9b0f0bd6... is not among the receipt inputs`
(the negative control, as intended); runs 002, 004, 005b, 006 and the example
resolve; the corrected run 005a record
(`transition_execution_record_corrected_001.json`, input 0 re-pointed at the
stored executed bytes) resolves. Full suite `1011 passed, 2 skipped`. Costs
in the receipt and the record; whole route in
`../route_costs_correction_001.json`; money unknown.

## 5. Divergence between expectation and result; Adjustment

- Expected: a cheap-tier miss and a fallback (loop_risk 0.25). Observed: the
  cheap tier closed it first time — the first `CHEAP_PASS` since run 001.
  One plausible reason, not established: the packet named every rule, every
  problem string and every file, after two review rounds; the five misses of
  the evening before were on packets that left one detail to the worker.
  No CAP-level Adjustment; no oracle weakened; no code by the driver.
- Expected: an observation of path B on real work. Observed: none of the
  path B mechanism ran, because the launch never reached the 600 s ceiling.
  The status "wait mechanism probed; working-path fix not yet confirmed"
  stands; this run neither confirms nor contradicts it.
- What a green record now means: the named links between the record and its
  stored carriers are checked. Full provenance of the execution is still not
  established (model identity is the CLI's report; the router's own
  execution is trusted from its receipt).
