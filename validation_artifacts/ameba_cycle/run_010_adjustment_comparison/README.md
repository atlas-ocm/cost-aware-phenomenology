# Run 010 — Adjustment against a fixed baseline path: one pair, a probe

Status: `recorded comparison / research-only`. The operator's step 3 of
2026-09-25. Design fixed before either route ran:
`../prepared/adjustment_comparison/README.md` (the same text as committed at
`7bc4780`, with both packets, the oracle, path B's Mirror Frame and candidate).
Both paths ran from `7bc4780`, each in its own detached worktree, through the
same NoMCP mode-1 route inside one native Workflow of four `nomcp-haiku` relays
(path B transport: background launch, six `wait` calls, `COLLECTED`, for each
path), A first, B not informed by A. Results are on branches
`cmp/run-010-path-A` (`71a0248`) and `cmp/run-010-path-B` (`fa10bfd`).

## 1. The change and the postcondition (identical for both)

`reference/python/scripts/build_execution_record.py`: build a schema-0.2 record
from a run directory and a record spec, validate, write. Oracle
`probe_build_record.py --expect-closed`: rebuilds run 009's record (JSON
equality with the committed one), validity, and an exit-2 case on a malformed
stored result. Red on the baseline because the script did not exist
(`baseline_oracle.txt`).

## 2. What each path was given

- **A** (`path_A/coding_packet.json`): goal, CLI, inputs, exit codes, the
  declared checks. No derivation rules, no observed facts, no forbidden
  outcomes beyond the file scope. No Mirror Frame, no CandidateTransition.
- **B** (`path_B/coding_packet.json`): packet A plus an "observed environment"
  section transcribed from `path_B/mirror_frame.json` (how every record field
  derives from the artifacts and the spec, the receipt shape, encodings) and
  the forbidden outcomes of `path_B/candidate_transition.json`.

## 3. What happened

| | path A (executor route alone) | path B (Adjustment path) |
|---|---|---|
| cheap_coder `gemma4:31b-cloud` | 6 turns, 2,714 output tokens, 15.19 s; oracle case c4 failed (`relative_to` error on the spec path under the scratch base), suite passed; set aside | 5 turns, 2,142 tokens, 9.69 s; oracle case c4 failed (`FileNotFoundError` on the second input under the scratch base, exit 1 instead of 2), suite passed; set aside |
| fallback_coder `deepseek-v4.1-flash:cloud` | 49 turns, 36,503 tokens, 134.67 s; both checks exit 0; `FALLBACK_PASS` | 47 turns, 30,209 tokens, 127.75 s; both checks exit 0; `FALLBACK_PASS` |
| whole route (receipt) | 55 turns, 39,217 tokens, 315.91 s | 52 turns, 32,351 tokens, 307.14 s |
| verifier `glm53_flash` | attempt 1: no verdict, `final_error_kind: deadline` after 482.0 s (`nomcp_verdict_receipt_attempt1_deadline.json`); attempt 2 (driver re-ran the same deterministic stage): `ACCEPT`, 35.0 s | `ACCEPT`, 21.8 s |
| checks re-run at the revision (driver, detached worktree) | c1–c3 all exit 0 at `71a0248`; 52 s | c1–c3 all exit 0 at `fa10bfd`; 51 s |
| driver authoring before the route (timestamps) | packet A: about 2 minutes | Mirror Frame + candidate + packet B: about 7 minutes |
| result | `path_A/result/build_execution_record.py`, 234 lines | `path_B/result/build_execution_record.py`, 268 lines |
| execution record | none: the record schema requires `candidate.candidate_ref` and `mirror_frame_before_ref`, which the baseline path by definition does not produce; recorded as receipts, checks and `path_costs.json` | `path_B/transition_execution_record.json` (0.2; validates) |

Workflow: 1338.3 s wall, 47,127 relay tokens for the four relays (not split per
relay by the harness), 18 tool uses (2 launches, 14 waits, 2 verify stages).
Model-pin check: 4/4 Haiku. Money: unknown.

## 4. The five axes of the brief

1. **Postcondition met, constraints violated.** Both met (oracle 4/4, suite
   1022 passed, exactly one file added); no constraint violated on either.
2. **Unverified completion claims.** One per path: each cheap-tier answer said
   the script was added and done while the oracle failed; the declared checks
   caught both. The fallback answers matched the checks.
3. **Interventions, retries, regressions, rollbacks.** A: one router
   set-aside; one verifier retry by the driver after a provider deadline (no
   change to the tree). B: one router set-aside. No regression, no rollback,
   no driver edit in either tree.
4. **Time and tokens.** B's route: 3 fewer turns, 6,866 fewer output tokens
   (17.5 %), 8.8 s less router wall; B's driver authoring: about 5 minutes
   more. Verifier walls are not comparable (A's first call was a provider
   deadline).
5. **New evidence.** Both scripts pass the same oracle; B's names a missing
   artifact before the exit-line check (its c4 output lists both), A's reports
   the exit line only. Both cheap attempts failed on the oracle's own
   construction (a run-directory copy under a scratch base outside the
   repository, with the spec path relative to the cwd) — a detail neither
   packet described. That miss is the driver's oracle, not the worker's
   reading of the packet, and it is the same class as the seven driver-caused
   escalations in the NoMCP journal (row 62).

## 5. Hypotheses, and what the pair says

- H1 (B closes with fewer attempts and lower route cost): **not supported on
  attempts** (one set-aside each, same tier closed both); **weakly consistent
  on tokens and wall**, by margins one pair cannot separate from noise.
- H0 (no difference beyond noise): **not rejected**.
- The pair does say something the design did not ask: the derivation section
  of packet B did not move the cheap tier past the case that failed it, because
  that case was outside what either packet described. The next pair should
  vary the packets in exactly what the cheap tier tends to miss, and measure
  the driver's authoring time with the same care as the route.

## 6. Landing rule (chosen after the results, not in the design)

The design did not say which result lands on the research branch. Rule chosen
after both verdicts were in: the accepted path with the lower whole-route
cost lands; both would have been acceptable. Landed: path B's script, copied
byte for byte from `fa10bfd` into `reference/python/scripts/build_execution_record.py`
on the research branch; the oracle is run against it at the records commit.
Path A's script stays on its branch and under `path_A/result/`.

## 7. What this run is not

Not a rate, not an ablation, not proof that any CAP layer improved the
outcome. It is the first comparison with a baseline path fixed beforehand,
the same required postcondition, and the same full-cost method, recorded so
that the next pairs can be added to it rather than argued from.
