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

## 8. Pair 2 — same base, same packets, same oracle, run again (01:33–01:52)

Both worktrees recreated at `7bc4780`; the same Workflow script; nothing
reused from pair 1 but the packets and the oracle; no driver authoring.
Results on `cmp/run-010-pair2-path-A` (`6a92c5f`) and `cmp/run-010-pair2-path-B`
(`c72c820`); records under `pair_2/`. Receipts read from the untruncated
`stdout_tail` (`pair_2/receipt_cases_pair2.txt`; pair 1 re-read the same way in
`receipt_cases_pair1.txt`).

| | path A | path B |
|---|---|---|
| cheap_coder `gemma4:31b-cloud` | 6 turns, 2,204 tokens, 13.73 s; c1 failed: the record it built had unresolved references and revisions (literal `unknown`, a run-dir-relative packet ref; seven validator problems); c4 failed; set aside | 5 turns, 2,147 tokens, 18.33 s; c1 failed: schema problems (unexpected keys; `costs.route` written as a list of attempts instead of the object); c4 failed (`FileNotFoundError`); set aside |
| fallback_coder `deepseek-v4.1-flash:cloud` | 45 turns, 30,692 tokens, 135.26 s; `FALLBACK_PASS` | 27 turns, 22,172 tokens, 94.0 s; `FALLBACK_PASS` |
| whole route (receipt) | 51 turns, 32,896 tokens, 305.84 s | 32 turns, 24,319 tokens, 267.49 s |
| verifier `glm53_flash` | `ACCEPT`, 109.0 s | `ACCEPT`, 164.6 s |
| checks re-run at the revision | c1–c3 exit 0 at `6a92c5f`; 53 s | c1–c3 exit 0 at `c72c820`; 54 s |
| result | 261 lines | 233 lines |
| execution record | none (as in pair 1) | `pair_2/path_B/transition_execution_record.json`, built with the landed builder script |

Workflow: 1041.5 s wall, 47,123 relay tokens, 17 tool uses (2 launches, 13
waits, 2 verify stages); model-pin check in `pair_2/model_pin.txt`.

### Across the two pairs

| route unit | pair 1 A | pair 1 B | pair 2 A | pair 2 B |
|---|---|---|---|---|
| turns | 55 | 52 | 51 | 32 |
| output tokens | 39,217 | 32,351 | 32,896 | 24,319 |
| router wall s | 315.9 | 307.1 | 305.8 | 267.5 |
| cheap set-asides | 1 | 1 | 1 | 1 |
| fallback turns | 49 | 47 | 45 | 27 |

- Direction: path B cheaper than path A in both pairs on all three route
  units, and its fallback needed fewer turns both times.
- Magnitude: the within-path swing between pairs (A 39,217 → 32,896 tokens;
  B 32,351 → 24,319) is as large as the pair-1 difference between paths
  (6,866) and comparable to the pair-2 one (8,577). Two pairs give a
  consistent direction, not an established effect; H1 on attempts stays
  unsupported (four routes, four cheap set-asides).
- The cheap tier missed the oracle's first case in all four attempts, each
  time differently (pair 1: `result_ref` resolution; pair 2: unresolved refs
  and revisions from misread spec fields in A, wrong shape of `costs.route`
  and extra keys in B). The informed packet did not prevent cheap-tier
  misses; what it plausibly bought is a shorter fallback (47 and 27 turns
  against 49 and 45). Plausible, not established.
- Verifier walls (109.0 s and 164.6 s here; 35.0 s and 21.8 s in pair 1 after a
  482 s deadline) vary more than the routes and say nothing about the paths.
- Nothing from pair 2 is landed; the landed script remains pair 1's path B.

## Corrections

- correction_001 (2026-09-25 01:40, after the NoMCP session read both receipts
  at `52667eb`): the cheap-tier cells of the table in section 3, the fifth
  axis in section 4 and the third bullet of section 5 say the cheap attempts
  failed the oracle's case c4 only and call the miss packet-independent. The
  receipts (`path_A/nomcp_coding_receipt.json`, `path_B/nomcp_coding_receipt.json`,
  `first_attempt.checks[0].stdout_tail`) show both attempts failing **c1, the
  plain in-repo rebuild**, as well as c4: A ignored `checks[].result_ref` and
  invented `<run_dir>/checks/<criterion_id>.txt` ("Missing check result file:
  ...checks/c1.txt"); B took `result_ref` but joined it onto the run directory
  instead of the repo root (a doubled path). c1 alone would have set both
  attempts aside. So the miss is a cheap-tier miss on resolving `result_ref`,
  on which packet A says nothing and packet B names the field and calls record
  paths repo-relative without saying explicitly that `result_ref` resolves
  against the repo root. c4 does depend on the oracle's construction (the
  base copy lacks the inputs outside the run directory), but it is not what
  decided the set-asides. The claim "the driver's oracle, not the worker" is
  withdrawn. Cause of the error: the driver read the first four `case=` lines
  of the receipt's truncated `tail` field, whose beginning (the c1 line) was
  cut; the untruncated `stdout_tail` field holds all four cases. The original
  text is kept above; the path B record's divergence sentence is corrected in
  `path_B/transition_execution_record_corrected_001.json` (built from
  `path_B/record_spec_corrected_001.json` with the landed builder script); the
  original record stays as written.
