# Ameba cycle — recorded runs

Recorded passes of the executable transition cycle from `CAP_REWORK_BRIEF.md`,
applied to this repository itself as the first real subject:

```text
observed state + goal + constraints + available actions + budget
  -> candidate next state and route
  -> action by an existing executor
  -> observed result and checked postcondition
  -> Adjustment when expectation != result
```

Each run directory holds:

| file | produced by | validated against |
|---|---|---|
| `mirror_frame.json` | the driver, from git / pytest / grep output only | `spec/mirror_layer.schema.json` |
| `candidate_transition.json` | the driver, before any executor ran | `spec/adjustment_layer.schema.json` |
| `coding_packet.json` | the driver (the task handed to the executor) | — |
| `nomcp_coding_receipt.json` | the NoMCP router, verbatim | — |
| `verify_packet.json` | a deterministic packet builder (no model) | — |
| `nomcp_verdict_receipt.json` | the NoMCP verifier runner, verbatim | — |
| `README.md` | the driver: the five items the brief asks to keep, plus costs and the Adjustment | — |
| `transition_execution_record.json` | the driver, from the artifacts above and the checks re-run at the obtained revision (0.2 from run 009 on: `costs.route` from the receipt) | `spec/transition_execution.schema.json` + `scripts/validate_execution_record.py --repo .` |
| `record_spec.json` (from run 009) | the driver: the non-derivable fields of the record (criteria, check mapping, observation, divergence, verdict reasons) | consumed by the record builder |
| `checks/*.txt` | the driver: outputs of each criterion's check at the obtained revision, in a detached worktree | referenced by the record |

No new schema was introduced: execution and verdict receipts are kept as the
executor and verifier wrote them, because `adjustment_layer.schema.json`
deliberately has no executor fields (ADJ-09).

Runs:

- [`run_001_layout_fix/`](./run_001_layout_fix/README.md) — first end-to-end
  pass; cheap tier closed it (`CHEAP_PASS`); commit `602fa63`.
- [`run_002_telemetry_admissibility/`](./run_002_telemetry_admissibility/README.md)
  — first measured escalation; cheap tier broke an existing definition,
  fallback tier closed it (`FALLBACK_PASS`); commit `bbbc26c`.
- [`run_003_numeric_coverage/`](./run_003_numeric_coverage/README.md) —
  evidence-only run (no transition): what the numeric gate can decide from
  the 25 pack cases; files are `coverage.json`, `gate_outputs.json`,
  `README.md`. Found the Breach ceiling contradiction and the
  candidate-vs-gate vocabulary gap; both decided by the operator the same
  evening (see runs 004 and 005 and `CAP_CLOUD_HANDOFF.md` §5).
- [`run_004_breach_recovery_only/`](./run_004_breach_recovery_only/README.md) —
  operator decision executed: Breach = Recovery-Only by operator identity;
  second measured escalation (Gemma missed an import); commit `989a7e2`; first
  execution record with checks re-run at the revision.
- [`run_005a_execution_record_schema/`](./run_005a_execution_record_schema/README.md)
  and [`run_005b_execution_record_validator/`](./run_005b_execution_record_validator/README.md)
  — the executed-transition record schema and its resolving validator, routed
  and verified the same way after the unsplit task failed twice (relay ceiling;
  fallback wall); each half has its own execution record.
- [`run_006_com_log_link/`](./run_006_com_log_link/README.md) — the candidate
  step ↔ COM-Log link with risk-weight provenance (operator's item 2), executed
  from the packet kept under `prepared/com_log_link/`; execution record included.
- [`run_007_record_binding_gap/`](./run_007_record_binding_gap/README.md) —
  evidence-only run after the review of `26535dc`: the validator accepts four
  records whose stored results contradict them (reproduced on the shipped
  example); corrections to the records of runs 002–006 (`execution.tool`,
  whole-route costs in `route_costs_correction_001.json`, run 005a packet
  bytes); the binding step is prepared under `prepared/record_binding/`.
- [`run_008_record_binding/`](./run_008_record_binding/README.md) — the
  execution record bound to its stored carriers (four rules), executed from
  the packet prepared in run 007 through the installed NoMCP path B relay;
  cheap tier closed it (`CHEAP_PASS`); commit `fc87e62`; the first record
  built under the new rules; a corrected record for run 005a added beside
  its original, which stays as the negative control.
- [`run_009_route_costs/`](./run_009_route_costs/README.md) — whole-route
  costs in the record bound to the receipt (schema 0.2, rules 5 and 6);
  fallback closed it after a cheap-tier set-aside; first verdict `OBJECT` on
  a stray worker file, second `ACCEPT` after one recorded driver
  intervention; path B exercised (background launch, eight waits); commit
  `5b84998`; the first 0.2 record, with its `record_spec.json`.
- [`run_010_adjustment_comparison/`](./run_010_adjustment_comparison/README.md) —
  the same change routed twice from `7bc4780`: path A (executor route alone)
  and path B (Mirror Frame + candidate informed packet); both reached the
  postcondition after one cheap set-aside each; one pair, a probe; path B's
  builder script landed on the branch; results on `cmp/run-010-path-A|B`.

What these records are not: they are not benchmark evidence, not a
comparison that establishes anything (one pair was run as a probe in run 010;
see `CAP_CLOUD_HANDOFF.md` §2.12), and not proof that any CAP layer improved
the outcome. One trajectory does not establish minimal cost. Costs are kept
in their own units (tokens, turns, seconds) and are never summed across units (within a unit the whole route counts:
`route_costs_correction_001.json`); money is
unknown for subscription-served models. Model identity is what the executing
CLI reported (`modelUsage`), not an independent probe.

Local paths inside the receipts (`F:/VibeCoding/...`, `C:/Users/...`) are the
executor's real working paths at the time of the run and are left as written.
