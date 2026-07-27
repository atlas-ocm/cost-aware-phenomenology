# Verdict Origin Exists, Evidence Not Found

**Unofficial draft. NON-CANONICAL provisional candidate. Not a canonical AICE code.**

See [the candidate surface README](./README.md) for the authority status of this directory.
This record reserves no number and defines no canonical code.

## Identity

| Field | Value |
|---|---|
| working_title | Verdict Origin Exists, Evidence Not Found |
| machine_name | `DECLARED_VERDICT_PROVENANCE_WITHOUT_RESOLVABLE_EVIDENCE` |
| previous_machine_name | `DECLARED_VERDICT_PROVENANCE_WITHOUT_EVIDENCE` |
| status | `EVIDENCE_BACKED_PROVISIONAL` |
| canonical_code | `UNASSIGNED` |
| canonical_number_reserved | `false` |
| operator_indicated_number | `AICE-623` — future publication identity only |
| source_class | `PRIMARY_PERSISTED` (task envelope) |
| raw_trace_attached | `false` (referenced by path and digest, not copied) |

> **Revision note.** This candidate was narrowed from *Verdict Origin Exists, Evidence Not
> Found* / `DECLARED_VERDICT_PROVENANCE_WITHOUT_EVIDENCE`. The original machine name risked
> asserting that the declared evidence never existed at all. What the primary evidence actually
> establishes is narrower and, for the purpose of a boundary taxonomy, more defensible: the
> declared evidence is not **durably linked or resolvable** from the record — it may have existed
> transiently inside the process and simply never reached a durable poststate. The class does not
> require, and must not claim, proof of metaphysical non-existence:
>
> ```
> EVIDENCE_NOT_RESOLVABLE_NOW  != EVIDENCE_NEVER_EXISTED
> ```
>
> The working title is unchanged; "Not Found" in this title means *not durably resolvable from
> the record*, not *proven never to have existed*.

```
OPERATOR_INDICATED_NUMBER != REGISTRY_ASSIGNMENT
EVIDENCE_ORIGIN_LABEL     != RESOLVABLE_EVIDENCE_LINEAGE
```

The operator has named `AICE-623` as the intended future publication identity and placed this
candidate second in the canonicalization order. That naming is provenance only and reserves
nothing; the registry's unreserved-successor claim is unaffected by this file.

## Source and provenance limits

Primary episode: Atlas task `atlas-b4c5dd43` — the same envelope that carries the
`ATTEMPT_CONSUMPTION_OUTCOME_EVIDENCE_GAP` observation, inspected read-only:

```
F:\VibeCoding\Atlas\.atlas\tasks\atlas-b4c5dd43.json    iterations[0].inner_result
evidence_digest                                          7911e8936b73e326
terminal                                                 2026-07-26T18:52:04+00:00
```

Stated limits:

```
exact_incident_time_orchestrator_bytes   NOT_ESTABLISHED
verdict_origin_field_semantics           INFERRED from the field name and the empty companions
second_independent_episode               NOT_ESTABLISHED
```

Sufficient for `EVIDENCE_BACKED_PROVISIONAL`; not sufficient for promotion.

## Core definition

A decision record declares the *provenance class* of its own evidence — deterministic evidence,
tool output, test execution, inspection — while the evidence set that provenance names is not
durably linked to, or resolvable from, that record. The label is emitted unconditionally by the
code path rather than derived from what was actually consumed and preserved, so it asserts a
grade of evidentiary support the record itself cannot substantiate.

The defect is not a wrong verdict. The verdict may be entirely correct. The defect is not even
necessarily that the evidence never existed — it may have existed transiently inside the process
and never reached durable storage. The defect is that the record advertises a resolvable
evidentiary lineage it cannot produce, and downstream consumers — audits, score attribution,
promotion gates, humans — read the label instead of finding the lineage empty.

## Observed form

```
verdict_origin        = "DETERMINISTIC_EVIDENCE"
checks                = []
verifier_verdicts     = []
test_output           = ""
candidate_diff        = ""
candidate_diff_sha256 = ""
status                = "FAILED"
reason                = "BLOCKED_ATTEMPT_BUDGET_EXHAUSTED"
```

Every evidence container the record carries is empty, and the record still declares its verdict
origin to be deterministic evidence. Nothing deterministic was ever resolvable from this record:
the route never produced a candidate to evaluate, and nothing preserved says otherwise.

## Trigger predicates — all required

1. `VERDICT_IS_DURABLE` — a decision, terminal, or classification was written to durable storage.
2. `VERDICT_DECLARES_AN_EVIDENCE_ORIGIN` — that record names an evidence class, origin, or grade
   for itself.
3. `THE_DECLARED_SUPPORTING_EVIDENCE_IS_NOT_DURABLY_LINKED_OR_RESOLVABLE` — the artifacts that
   provenance names cannot be resolved to observed, durable bytes from the record as it stands.
4. `THE_VERDICT_REMAINS_ACTIONABLE_OR_TERMINAL` — the verdict has force: it drives a terminal
   state, an audit conclusion, or a routing decision, whether or not any consumer happens to read
   the provenance field on a given occasion.

Required formula:

```
VERDICT_IS_DURABLE
AND
VERDICT_DECLARES_AN_EVIDENCE_ORIGIN
AND
THE_DECLARED_SUPPORTING_EVIDENCE
  IS_NOT_DURABLY_LINKED_OR_RESOLVABLE
AND
THE_VERDICT_REMAINS_ACTIONABLE_OR_TERMINAL

→ DECLARED_VERDICT_PROVENANCE_WITHOUT_RESOLVABLE_EVIDENCE
```

Maxims:

```
EVIDENCE_ORIGIN_LABEL   != RESOLVABLE_EVIDENCE_LINEAGE
DECLARED_DETERMINISTIC  != DETERMINISTICALLY_DERIVED
FIELD_POPULATED         != FIELD_EARNED
```

## Forbidden inference

```
VERDICT_CORRECT              != PROVENANCE_HONEST
NO_EVIDENCE_WAS_POSSIBLE     != DECLARING_EVIDENCE_IS_HARMLESS
DEFAULT_CONSTANT             != OBSERVED_CLASSIFICATION
EVIDENCE_NOT_RESOLVABLE_NOW  != EVIDENCE_NEVER_EXISTED
```

The last line is the boundary that motivated the [narrowing above](#identity): this candidate
never claims the evidence provably never existed, only that the record cannot resolve it. A path
that structurally could not gather or retain evidence must emit an origin that says so
(`NO_EVIDENCE_AVAILABLE`, `ROUTE_ABORTED`), not the strongest label in the enum by default.

## Required terminal

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
REQUEST_EVIDENCE
```

Remediation: derive the provenance label from evidence actually consumed and durably linked, or
emit an explicit "no evidence" origin. A provenance enum whose strongest value is also its
default is the defect's implementation shape.

## AICE-606 precedence (normative)

`AICE-606` (PASS Exists, Test Run Not Found) is the specific case of this candidate restricted to
one verdict polarity (a success claim) and one evidence-provenance class (test execution). The
two are not independent codes covering the same bytes:

```
AICE-606 ⊂ AICE-623   (as a specific case, not as a subordinate)
```

**Most-specific-code-wins rule.**

```
AICE-606 primary:
    a PASS claims test support, and no test-run receipt — command identity, exit status,
    captured output, timestamps — exists

AICE-623 primary:
    a different verdict polarity (the exemplar here is a FAILED terminal), a different
    declared evidence-provenance class (here: "deterministic evidence", not test execution),
    or a broader declared evidence lineage is unresolvable
```

If the only defect present in an episode is "a PASS claims test support with no test-run
receipt", emit `AICE-606`, not this candidate — do not duplicate one missing-receipt finding
under two names. Co-emission is permitted only when the episode has two **independently
satisfied** gaps (for example, a PASS with no test receipt *and* a separately declared
`verdict_origin` on an unrelated decision with no resolvable evidence of its own), never as two
labels for the same missing bytes.

## Comparison with nearby canonical codes

| Code | Boundary | Relationship |
|---|---|---|
| [`AICE-606`](../codes/AICE-606.md) PASS Exists, Test Run Not Found | A **success verdict** asserted without command identity, exit status, or captured output | **Closest neighbour; precedence rule above governs.** 606 is the success-verdict, test-execution instance of this shape. This candidate generalizes on two axes: any verdict polarity (the observed instance is a *failure*), and any declared provenance class, not only test execution |
| [`AICE-609`](../codes/AICE-609.md) Consensus Exists, Evidence Not Found | Agreement substituted for evidence; no participant inspected the postcondition | 609 needs multiple agreeing actors. This fires on a single record with no consensus involved |
| [`AICE-604`](../codes/AICE-604.md) Hash Exists, Reality Not Found | A declared digest with no bytes behind it | 604 is about a declared *artifact*; this is about a declared *epistemic grade* of a decision |
| [`AICE-608`](../codes/AICE-608.md) Verification Exists, Independence Not Found | The verifier was not independent | 608 concerns *who* verified; this concerns *whether the evidence for the verdict is resolvable at all* |
| [`AICE-618`](../codes/AICE-618.md) Verifier Gated by Coder Evidence Ceiling | The verifier could not obtain evidence because an upstream actor capped it | 618 explains a genuine, disclosed evidence shortage. This candidate is the shortage being *labelled over* rather than disclosed |

## Comparison with existing candidates

| Candidate | Relationship |
|---|---|
| [`CAUSAL_QUESTION_CLOSURE_SUBSTITUTION`](./causal-question-closure-substitution.md) | Disjoint on the evidence-existence axis. There, evidence exists and is *valid for a different question* — the defect is unauthorized transfer of closure authority. Here the evidence set is not resolvable and the defect is the label asserted over that gap |
| [`POST_OBSERVATION_EVALUATION_MUTATION`](./post-observation-evaluation-mutation.md) | There, the evidence is real and the *contract* that evaluates it was mutated after observation. Here the record's own evidence lineage cannot be resolved at all |
| [`ATTEMPT_CONSUMPTION_OUTCOME_EVIDENCE_GAP`](./attempt-consumption-outcome-evidence-gap.md) | Same episode, different object. That candidate is about a consumed *resource* with no receipt; this is about a declared *decision* with no resolvable evidence. They co-emitted here but are independently reachable: a fully-receipted route can still stamp a false provenance label, and a route with no provenance field at all can still lose receipts |

## False-positive boundary

Not this candidate when:

- the declared evidence resolves — a referenced job id, digest, or bundle that can be fetched is
  evidence, even if not inlined in the record;
- the provenance label is accurate about a *degenerate but real* evaluation ("deterministic
  evidence: zero checks applicable, all preconditions unmet") and the record says so;
- the record declares no provenance at all — silence is not a false claim, though it may fail a
  different requirement;
- the evidence existed durably and was pruned by a documented retention policy the record cites;
- the label is a schema-required placeholder that no consumer reads and no audit trusts, and the
  verdict itself has no actionable or terminal force — predicate 4 fails, and the finding is a
  hygiene issue rather than an incident;
- the only defect present is a PASS with no test-run receipt — see the
  [AICE-606 precedence rule](#aice-606-precedence-normative).

## Negative controls

1. **Resolvable provenance.** A verdict declaring `verdict_origin=DETERMINISTIC_EVIDENCE` with a
   non-empty `checks` array naming commands and exit codes. Predicate 3 fails.
2. **Honest emptiness.** The same failed route emitting `verdict_origin=NO_EVIDENCE_AVAILABLE`.
   Identical outcome, no incident — this is exactly the remediation.
3. **Absent field.** An orchestrator with no provenance field. Predicate 2 fails; whatever else
   is wrong, it is not this.
4. **606 territory only.** A PASS verdict with `verdict_origin=test_execution` and an empty
   `test_output`, with every other evidence container populated. Emit AICE-606 per the
   precedence rule; predicate 3 here is satisfied but the finding is not co-emitted as a
   second, duplicate label.

## Portable CAP enforcement requirement

```
PROVENANCE_LABEL_DERIVATION
```

An evidence-provenance label must be a function of the evidence actually consumed and durably
linked on that path, never a constant, never a default, and never assigned by the code path that
failed to gather or retain evidence. Where an enum has a strongest value, that value must be
unreachable unless the corresponding artifacts are present and resolvable.

## Promotion gate

```
1. a second independent episode, ideally outside Atlas
2. independent review and operator acceptance of the AICE-606 precedence rule above
3. confirmation that verdict_origin is consumed downstream and not decorative (predicate 4)
4. exact incident-time implementation bytes established
5. independent semantic review of this dossier
6. explicit operator number assignment and canonical publication episode
```

Conditions 1, 3, 4 and 5 are **unmet**. Condition 2 now has a drafted resolution (the
most-specific-code-wins rule above), but a rule the same author both proposes and accepts is not
independently reviewed — it counts as met only once reviewed by an actor other than this
candidate's author.

## Verification status

```
authored_by            CAP session 91033b6c (Claude Opus 5)
independent_review     NOT_PERFORMED
operator_acceptance    NOT_GIVEN
canonical_promotion    NOT_PERFORMED
```
