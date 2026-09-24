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
  candidate-vs-gate vocabulary gap; both left as open decisions.

What these records are not: they are not benchmark evidence, not a
comparison against a baseline path (that comparison is defined but not yet
run; see `CAP_CLOUD_HANDOFF.md`), and not proof that any CAP layer improved
the outcome. One trajectory does not establish minimal cost. Costs are kept
in their own units (tokens, turns, seconds) and are never summed; money is
unknown for subscription-served models. Model identity is what the executing
CLI reported (`modelUsage`), not an independent probe.

Local paths inside the receipts (`F:/VibeCoding/...`, `C:/Users/...`) are the
executor's real working paths at the time of the run and are left as written.
