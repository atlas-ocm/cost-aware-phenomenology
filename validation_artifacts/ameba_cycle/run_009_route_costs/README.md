# Run 009 — whole-route costs in the record, bound to the receipt

Status: `recorded run / research-only`. The operator's step 2 of 2026-09-25,
executed from the packet prepared under `prepared/route_costs/` (`coding_packet.json`
here is that packet; `baseline_oracle.txt` the oracle on the clean tree before
the route; `record_spec.json` the spec the driver used to build this record).

Statuses, kept apart as the operator asked:

| status of | value | source |
|---|---|---|
| the route | `FALLBACK_PASS` — cheap tier set aside (its own tests failed), fallback closed it | `nomcp_coding_receipt.json` |
| the verdict | attempt 1 `OBJECT` (a stray empty `.run_checks.sh` the worker left); attempt 2 `ACCEPT` on the cleaned tree; both by `glm53_flash` | `nomcp_verdict_receipt_attempt1_object.json`, `nomcp_verdict_receipt.json` |
| the checks | five criteria re-run by the driver at `5b84998` in a detached worktree, all `exit=0` (62 s) | `checks/`, `reobservation_wall.txt` |
| the acceptance | accepted by the driver on the diff after one intervention (section 4) | this README, `driver_intervention.txt`, `transition_execution_record.json` |
| the transport (path B) | **exercised**: background launch, eight `wait` calls (`NOT_FINAL`), then `COLLECTED`; the first launch was killed by a relay deviation | `failed_route/`, Workflow transcripts, section 3 |

## 1. Initial state and the input available before the choice

- Tree at `c0c8cba` (prepared packet and oracle), clean, pushed; full suite
  `1011 passed, 2 skipped` at `fc87e62` with no code change since
  (`mirror_frame.json`; declared state `source: user` = the operator's step 2 and
  the NoMCP session's description of the installed path B text).
- Observed: the schema has no place for per-attempt or route figures; every
  receipt carries them; the correction file lists them unbound; the oracle on
  the clean tree exits 1 with one of nine expectations holding
  (`baseline_oracle.txt`).

## 2. Proposed transition

`candidate_transition.json`: mode `repair`; a schema field, two comparison
rules, an example update and tests across six files; `loop_risk` estimated 0.2
(run 008 closed cheap; the last schema-plus-validator task needed the fallback).
Proposed before the route was launched.

## 3. Action actually executed

Two native Workflows, each with two `nomcp-haiku` relays (model-pin check 2/2
Haiku each).

| launch | what happened | evidence |
|---|---|---|
| 1 (`wf_a8a8268c`, 28.9 s, 18,893 relay tokens) | the relay launched the route in the background, then ran `cat <output_file>` instead of the wait command; the one-Bash hook denied it (correctly); the relay ended its turn and the harness killed the route; the router had announced its run and finished `tree_check` only; no worker change reached the tree; no receipt | `failed_route/attempt1_launch_output.txt` (ends `[killed]`), `failed_route/attempt1_router_state.json`, `failed_route/attempt1_workflow_journal.jsonl` |
| 2 (`wf_eae63803`, 578.1 s, 24,139 relay tokens) | background launch; eight `nomcp.py wait` calls, each `{"status": "NOT_FINAL", "waited_s": 45.0}`; the ninth `COLLECTED` with the run bound (`run-40e4239b…`); the relay reported the lines verbatim | Workflow transcript; `nomcp_coding_receipt.json` |

The second launch's relay prompt differed from the first's in one place: it
said that the wait command is the only command permitted after the launch, that
a denial does not end the stage, and that ending the turn while `NOT_FINAL`
kills the route. The first prompt had said "if a call is denied, still return
the report", which the relay took literally. Reported to the NoMCP window.

| stage | model (identity per CLI report, not independently verified) | turns | output tokens | wall s | outcome |
|---|---|---|---|---|---|
| baseline (router, no model) | — | — | — | — | oracle exit 1, tests exit 0, run 008 record exit 0: red for the named reason only |
| cheap_coder | `gemma4:31b-cloud` | 24 | 15,121 | 65.0 | oracle exit 0; validator/schema tests exit 1 (its own tests); set aside (stash `f55b2863`) |
| fallback_coder | `deepseek-v4.1-flash:cloud` | 52 | 43,932 | 320.97 | all three declared checks exit 0; `FALLBACK_PASS`; left an empty untracked `.run_checks.sh` and said so |
| verifier, attempt 1 | `glm-5.3-flash:cloud` | — | — | 101.1 | `OBJECT`: the stray file violates "no other file added"; the diff itself judged as declared |
| driver intervention | — | — | — | — | removed the empty `.run_checks.sh` (`driver_intervention.txt`); re-ran the declared checks, the full suite and every record |
| verifier, attempt 2 | `glm-5.3-flash:cloud` | — | — | 98.5 | `ACCEPT`, eight files cited, no issues |

Whole route (router `total_wall_s`): 422.59 s, 76 turns, 59,053 output tokens.
Objects changed: `spec/transition_execution.schema.json` (+85), `cap/execution_record.py`
(+114), `tests/test_execution_record_validator.py` (+126, eight tests),
`tests/test_transition_execution_schema.py` (+38, three tests), the example
record (0.2) and the example receipt (attempt figures, `total_wall_s`).
Nothing else; the probe untouched.

## 4. Observed result, postcondition check, costs

See `transition_execution_record.json` (the first 0.2 record: `costs.route`
from this run's own receipt, both attempts) and `checks/`. Driver adjudication
on the diff: rule 5 compares the attempts list, each attempt's four fields, the
two sums and the router wall with the receipt; rule 6 the closing attempt; the
schema adds `route` as optional with a 0.2-requires-route entry; existing
checks, tests and strings unchanged (the diff only adds); numbers compared as
numbers. The stray file was a 0-byte artifact of the fallback worker's attempt
to run the checks itself, not part of the change; its removal is the one
driver intervention of this run and is counted, not hidden. Consequences on
the tree: every record of runs 002, 004, 005b, 006, 008 and the corrected 005a
resolves under rule 6 (their `measured` figures were the closing attempt
already); the original 005a stays refused on its input hash. Full suite
`1022 passed, 2 skipped`.

Costs, in their own units: route above; verifier 101.1 + 98.5 s; Workflow
relays 18,893 + 24,139 tokens, 28.9 + 578.1 s wall; driver re-observation 62 s;
driver authoring (packet, oracle, Mirror Frame, candidate) about 15 minutes;
money unknown. `../route_costs_correction_001.json` regenerated over eight runs.

## 5. Divergence between expectation and result; Adjustment

- Expected: a cheap close was possible. Observed: the cheap tier's code passed
  the oracle and its own tests failed — the same shape as run 006. No
  CAP-level Adjustment; the router's policy applied; no oracle weakened; no
  code by the driver.
- Expected: path B on real work. Observed: exercised on the second launch;
  the first launch showed a relay-deviation class (reading the output file
  instead of waiting) that the prompt wording, not the mechanism, caused. The
  NoMCP status "working-path fix not yet confirmed" can now be updated by the
  NoMCP session on this evidence; CAP records the observation only.
- Expected: one verdict. Observed: two, with a driver intervention between
  them; the first verdict was right about the tree it saw.
- What a green record now means: the named links, and now the costs, are
  the receipt's for every attempt. Money, driver time and relay tokens remain
  outside the record.
