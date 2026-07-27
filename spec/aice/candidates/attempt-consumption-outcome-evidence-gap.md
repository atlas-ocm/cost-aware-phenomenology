# Attempt Spent, Outcome Not Found

**Unofficial draft. NON-CANONICAL provisional candidate. Not a canonical AICE code.**

See [the candidate surface README](./README.md) for the authority status of this directory.
This record reserves no number and defines no canonical code.

## Identity

| Field | Value |
|---|---|
| working_title | Attempt Spent, Outcome Not Found |
| machine_name | `ATTEMPT_CONSUMPTION_OUTCOME_EVIDENCE_GAP` |
| status | `EVIDENCE_BACKED_PROVISIONAL` |
| canonical_code | `UNASSIGNED` |
| canonical_number_reserved | `false` |
| operator_indicated_number | `AICE-622` — future publication identity only |
| source_class | `PRIMARY_PERSISTED` (task envelope + score ledger) |
| raw_trace_attached | `false` (referenced by path and digest, not copied) |

```
OPERATOR_INDICATED_NUMBER != REGISTRY_ASSIGNMENT
CANDIDATE_PRESENT         != CANONICAL_CODE_DEFINED
```

The operator has named `AICE-622` as the intended future publication identity and placed this
candidate first in the canonicalization order. That naming is provenance only. At the time of
writing the registry's own claim — `AICE-601`…`AICE-621` defined, `AICE-600` unassigned,
`AICE-622` **neither defined nor reserved** — remains true and is not weakened by this file.
Promotion, if it happens, is what would make `AICE-622` defined; this dossier does not.

## Source and provenance limits

Primary episode: Atlas task `atlas-b4c5dd43`, created `2026-07-26T18:41:08+00:00`, target
repository `F:\VibeCoding\v5.com.ua` at head `6bd7bc3`, terminal recorded
`2026-07-26T18:52:04+00:00`.

Durable artifacts inspected read-only:

```
F:\VibeCoding\Atlas\.atlas\tasks\atlas-b4c5dd43.json      task envelope, iterations[0].inner_result
F:\VibeCoding\Atlas\.atlas\scores.jsonl                   durable outcome ledger
evidence_digest                                           7911e8936b73e326
```

Stated limits:

```
exact_incident_time_orchestrator_bytes   NOT_ESTABLISHED
    the episode ran at or after Atlas commit 8d90678 (2026-07-26T21:22:10+03:00) with an
    uncommitted working tree; the exact live bytes at 21:41 local are not recoverable
raw_model_payloads                       LOST
per-attempt provider metadata            LOST
second_independent_episode               NOT_ESTABLISHED
```

The provenance is sufficient for `EVIDENCE_BACKED_PROVISIONAL`. It is **not** sufficient for
canonical promotion — see [Promotion gate](#promotion-gate).

## Core definition

An invocation is dispatched, a bounded attempt or route budget is decremented as a result, and
a routing decision or terminal state depends on that consumption — yet no durable receipt links
the consumed unit to an outcome. The budget is authoritative enough to end the work but not
accountable enough to explain why.

The defect is **not** absence of logging in general. Some ledger exists and other invocations in
the same episode are recorded. The defect is that the *authority-bearing* consumption event has
no durable causal receipt.

## Observed form

Recorded route (`iterations[0].inner_result.trace`, durable):

```
18:41:08  CODING           coder=glm-5.2     verifier=kimi-k2.7-code
18:46:09  BLOCKED          SYSTEM_OR_POLICY  "TRANSPORT_FAILURE: TimeoutError: stream exceeded 300s wall clock"
18:46:09  SWITCHING_CODER  coder=minimax-m3  cause=SYSTEM_OR_POLICY
18:46:09  CODING           coder=minimax-m3  verifier=kimi-k2.7-code
18:49:03  FIXING           coder=minimax-m3  attempt=2
          terminal: status=FAILED  reason=BLOCKED_ATTEMPT_BUDGET_EXHAUSTED
```

Durable ledger rows for the same `job_id` (complete, one row):

```
{"job_id":"atlas-b4c5dd43","model":"glm-5.2","role":"coder","attempt":1,
 "outcome":"system_transport_failure","latency_ms":300141,"edit_format":"ops"}
```

Contradiction:

```
minimax-m3 attempts entered      >= 2   (CODING at 18:46:09, FIXING attempt=2 at 18:49:03)
minimax-m3 durable receipts       = 0
terminal                          = BLOCKED_ATTEMPT_BUDGET_EXHAUSTED
terminal depends on the count of spent attempts
```

The episode ended *because* the attempt budget reached zero, and the attempts that exhausted it
left no durable outcome record. `inner_result.coder_model` is `minimax-m3`, so the terminal is
attributed to a model whose attempts are entirely unaccounted for in the ledger.

### What this exemplar does not claim

The exact per-attempt outcome for either minimax invocation — schema-invalid, transport failure,
truncation, or anything else — is **not** established from durable bytes, and the exact
incident-time Atlas implementation is itself `NOT_ESTABLISHED` (see
[Source and provenance limits](#source-and-provenance-limits)). Reasoning backward from "zero
score rows" to a specific outcome class such as truncation would be a fabrication: the absence of
a receipt is consistent with every outcome class, and that indifference is exactly the defect,
not a gap to paper over with a guess.

```
ATTEMPTS_CONSUMED          = ESTABLISHED
LINKED_OUTCOME_RECEIPTS    = 0
EXACT_MINIMAX_OUTCOME      = NOT_ESTABLISHED
TERMINAL_CAUSAL_LINEAGE    = UNRESOLVABLE
```

This is not a weaker exemplar for it — it is the sharpest form of the class. This candidate does
not require knowing what the outcome was. It requires proving that authority was consumed
without preserving what the outcome was:

```
ATTEMPT_CONSUMPTION_OUTCOME_EVIDENCE_GAP
    is proven by the ABSENCE of a linked receipt,
    never by RECOVERING the outcome the missing receipt would have named.
```

## Trigger predicates — all required

1. `INVOCATION_STARTED` — an actor invocation was actually dispatched.
2. `ATTEMPT_BUDGET_CONSUMED` — a bounded attempt, retry, coder-slot, or route budget was
   decremented as a consequence of that invocation.
3. `ROUTING_OR_TERMINAL_STATE_DEPENDS_ON_THE_OUTCOME` — the consumption feeds a switch,
   escalation, blocking, or terminal decision.
4. `NO_DURABLE_LINKED_OUTCOME_RECEIPT_EXISTS` — no durable artifact links that consumed unit to
   an outcome class, at the granularity the budget is enforced at.

Required formula:

```
ATTEMPT_SPENT        != ATTEMPT_ACCOUNTED
BUDGET_DECREMENTED   != CAUSE_DURABLE
TERMINAL_IS_DURABLE  != TERMINAL_IS_EXPLAINED
```

## Forbidden inference

```
LEDGER_FILE_EXISTS           != EVERY_CONSUMED_ATTEMPT_IS_RECORDED
SOME_ROWS_PRESENT            != COVERAGE_ESTABLISHED
TRACE_MENTIONS_THE_ATTEMPT   != DURABLE_OUTCOME_RECEIPT
NO_PENALTY_WAS_WARRANTED     != NO_EVENT_OCCURRED
```

The fourth line is the suspected mechanism and is recorded separately as a held hypothesis
(`FAULT_ABSENCE_EVENT_ABSENCE_CONFLATION`, see [`held-hypotheses.md`](./held-hypotheses.md)). It
is **not** a trigger predicate here: this candidate fires on the missing receipt regardless of
why it is missing.

## Required terminal

An episode that cannot produce a per-consumption receipt for every decremented unit must not
present its terminal as explained:

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
REQUEST_EVIDENCE
```

The remediating shape is one durable receipt per consumed invocation, written at the moment of
consumption and carrying at minimum: invocation identity, actor role, model, attempt index,
outcome class, whether the attempt was spent, and budget-before/budget-after.

## Comparison with nearby canonical codes

| Code | Boundary | Why this candidate is distinct |
|---|---|---|
| [`AICE-617`](../codes/AICE-617.md) Work Exists, Result Not Found | Process activity accumulates while the *product outcome* stays absent | 617 is about production; this is about accounting. Here each invocation *did* reach a definite outcome — the outcome record is what is missing, not the outcome |
| [`AICE-606`](../codes/AICE-606.md) PASS Exists, Test Run Not Found | A *success verdict* is asserted without a run receipt | 606 requires an asserted success. This fires on a purely failing route where no verdict was claimed at all |
| [`AICE-604`](../codes/AICE-604.md) Hash Exists, Reality Not Found | A *declared artifact* has no confirmed bytes | Nothing was declared. The missing thing is a receipt for a consumed resource, which no actor claimed to have produced |
| [`AICE-609`](../codes/AICE-609.md) Consensus Exists, Evidence Not Found | Agreement offered in place of evidence | No agreement, no participants, no claim — an unattested resource consumption |
| [`AICE-621`](../codes/AICE-621.md) Task Admitted, Output Capacity Not Found | Minimum valid output exceeds the effective cap | 621 explains why an attempt *fails*; this fires on the absence of the record of that failure. Same episode family, orthogonal axes — they may co-emit |

## False-positive boundary

Not this candidate when:

- the budget was never decremented (a pre-dispatch policy refusal consumes nothing);
- a durable receipt exists elsewhere and is *linkable* — a different store, an external CI
  record, or a provider-side receipt with a resolvable identifier is evidence, not a gap;
- the outcome is recorded at the granularity the budget is enforced at, even if coarser than
  per-message (a budget counted in *coder slots* needs a per-slot receipt, not a per-token one);
- the episode is still open and the receipt is expected to be written at close;
- the receipt exists but is merely unflattering, ambiguous, or lacks provider metadata — an
  incomplete receipt is a quality defect, not an evidence gap;
- the ledger was lost by an independent storage failure with its own durable evidence.

## Negative controls

1. **Recorded failure.** `atlas-99b6bb2d` — three attempts entered, three durable rows
   (`schema_invalid`, `schema_invalid`, `system_transport_failure`). Attempts were spent and every
   one is accounted for. Not this candidate, though that episode is the
   [`AICE-621`](../codes/AICE-621.md) exemplar.
2. **Pre-dispatch refusal.** A route rejected before the provider call, with no decrement, leaves
   nothing to account for.
3. **Receipt elsewhere.** An orchestrator that writes no local row but records a provider
   invocation id that resolves to a durable provider-side outcome satisfies predicate 4 negatively.

## Portable CAP enforcement requirement

```
CONSUMPTION_RECEIPT_COMPLETENESS
```

A budget that can terminate work is an authority mechanism. Every decrement of such a budget
must be paired with exactly one durable receipt, written at consumption time, and the terminal
must be derivable from those receipts alone. An orchestrator should be able to answer "which
invocations spent this budget, and what did each of them do" from durable bytes with no
transcript and no live process.

## Promotion gate

```
1. a second independent episode, in a different orchestrator, route, or budget kind
2. the exact incident-time implementation bytes established, or the defect reproduced
   against a pinned commit
3. differential resolution against AICE-617 and AICE-606 reviewed independently
4. a decision on whether FAULT_ABSENCE_EVENT_ABSENCE_CONFLATION is a separate class or the
   root mechanism of this one
5. a decision on whether TERMINAL_CAUSAL_LINEAGE_GAP is an umbrella above this candidate
6. explicit operator number assignment and canonical publication episode
```

Condition 1 is **unmet**. `atlas-b451a87d` and `atlas-1582aecc` reach the same terminal with
minimax attempts *present* in the ledger, which supports the boundary but does not supply a
second positive instance.

## Verification status

```
authored_by            CAP session 91033b6c (Claude Opus 5)
independent_review     NOT_PERFORMED
operator_acceptance    NOT_GIVEN
canonical_promotion    NOT_PERFORMED
```

Primary evidence was read directly by the author. No independent actor has reviewed these bytes
or this dossier.
