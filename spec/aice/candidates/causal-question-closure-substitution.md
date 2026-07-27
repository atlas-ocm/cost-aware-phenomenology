# Causal Question Closure Substitution

**Unofficial draft. NON-CANONICAL provisional candidate. Not a canonical AICE code.**

See [the candidate surface README](./README.md) for the authority status of this directory.
This record reserves no number and defines no canonical code.

## Identity

| Field | Value |
|---|---|
| working_title | Causal Question Closure Substitution |
| machine_name | `CAUSAL_QUESTION_CLOSURE_SUBSTITUTION` |
| status | `EVIDENCE_BACKED_PROVISIONAL` |
| canonical_code | `UNASSIGNED` |
| canonical_number_reserved | `false` |
| source_class | `OPERATOR_SUPPLIED_EPISODE_REPORT` |
| raw_trace_attached | `false` |

## Source and provenance limits

The evidence for this candidate is an operator-supplied report from a separate execution
window. No raw logs, frozen experiment bytes, metrics, or complete transcript are attached to
this record. The report establishes that one causal question was validly answered by evidence
and that a second, distinct causal question was then treated as closed using that same evidence
without a verified bridge.

This provenance is sufficient for `EVIDENCE_BACKED_PROVISIONAL` status. It is **not** sufficient
for canonical promotion.

## Core definition

A causal question is marked closed using evidence whose valid closure authority belongs to a
distinct causal question, outcome, comparison basis, or conditioning regime, without an explicit
verified bridge between them.

## Observed form

```
Q1: source of byte reduction
    = evidence-backed ANSWERED

Q2: cause of superiority at equal bytes
    = materially distinct causal target and conditioning regime

VERIFIED_BRIDGE_Q1_TO_Q2:
    absent

DEFECT:
    Q2 was incorrectly treated as closed using Q1 evidence.
```

The defect is **not** total absence of evidence. Evidence existed and was valid for Q1. The
defect is the unauthorized transfer of *closure authority* from Q1 to Q2.

## Trigger predicates — all required

The candidate fires only when all four hold:

1. Evidence `E` validly answers causal question `Q1`.
2. `Q2` differs materially from `Q1` in at least one load-bearing field:
   - target outcome;
   - conditioning regime;
   - comparison basis;
   - intervention or control;
   - candidate causal mechanism;
   - falsification requirement.
3. No verified causal bridge authorizes transfer from `Q1` to `Q2`.
4. `Q2` is nevertheless marked `ANSWERED`, `CLOSED`, `RESOLVED`, `COMPLETE`, or semantically
   equivalent.

## Forbidden inference

```
EVIDENCE_CLOSES(Q1)
  does not authorize
EVIDENCE_CLOSES(Q2)
```

Observed concrete form:

```
SOURCE_OF_BYTE_REDUCTION
  !=
CAUSE_OF_SUPERIORITY_AT_EQUAL_BYTES
```

## Required terminal

```
Q1 = ANSWERED

Q2 = OPEN
   or UNKNOWN
   or REQUIRES_CONTROLLED_EVIDENCE
```

…unless `Q2`'s own closure contract passes, or an explicit verified bridge supplies the missing
authority.

## Common workflow rule

```
CLAIM_PRESENT
REQUIRED_EVIDENCE_ABSENT_FOR_THIS_CAUSAL_SCOPE
WORKFLOW_EFFECT = Q2_STATE_UNCHANGED
```

## False-positive boundary

This candidate must **not** fire merely because one piece of evidence contributes to more than
one question. Evidence reuse is ordinary and legitimate.

Legitimate non-incidents include:

- one controlled experiment was explicitly designed to answer both `Q1` and `Q2`;
- `Q1` and `Q2` share the same load-bearing target and conditioning regime;
- a verified causal bridge connects `Q1` evidence to `Q2`;
- matched-byte evidence directly isolates the claimed superiority mechanism;
- `Q1` evidence is recorded only as partial support while `Q2` remains `OPEN`.

### Negative control (must not fire)

`Q1` evidence may legitimately contribute to `Q2` when **all** hold:

- destination relevance is established;
- conditioning regimes are compatible;
- the bridge is evidence-backed and independently checkable;
- `Q2`'s own closure requirements are satisfied.

In that case `Q2` closes on its own contract and no incident exists. The candidate concerns
*unauthorized closure transfer*, not evidence reuse.

### Positive control (should fire)

`Q1` answered by valid evidence; `Q2` differs in conditioning regime (absolute vs matched
bytes); no bridge object; `Q2` nevertheless reported `CLOSED`. Required terminal:
`Q2 = REQUIRES_CONTROLLED_EVIDENCE`, `WORKFLOW_EFFECT = Q2_STATE_UNCHANGED`.

## Comparison with canonical AICE

### Not AICE-602

[`AICE-602`](../codes/AICE-602.md) is narrowly **Gateway Authority Context Failure**: an
authoritative gateway / security / policy decision that substitutes request content or shape for
required identity, authority, provenance, purpose, target, environment, or incident context.

This candidate has:

- no gateway-authority decision;
- no authorized-denial branch;
- no untrusted-admission branch;
- no identity or authority-context substitution.

The transferred object here is **causal closure authority between distinct questions**, not
actor/authority context at a gateway.

```
CAUSAL_SCOPE_TRANSFER
  !=
GATEWAY_AUTHORITY_CONTEXT_FAILURE
```

AICE-602 must **not** be broadened to absorb this candidate.

### AICE-609 (nearest neighbour)

[`AICE-609`](../codes/AICE-609.md) — *Consensus Exists, Evidence Not Found* — is nearby because
`Q2` lacks sufficient supporting evidence.

Distinction: here valid evidence **exists** and correctly closes `Q1`; the defect is the
*transfer of closure authority* from `Q1` to `Q2`. Use AICE-609 when the defect is generic
unsupported consensus or agreement, rather than question-to-question closure substitution.

### Not AICE-611 / 612 / 614 / 618

- [`AICE-611`](../codes/AICE-611.md) — no operational-reachability evidence is transferred.
- [`AICE-612`](../codes/AICE-612.md) — no actor-specific execution/observation path is substituted.
- [`AICE-614`](../codes/AICE-614.md) — no infrastructure terminal impersonates a semantic verdict.
- [`AICE-618`](../codes/AICE-618.md) — no coder/verifier capability or evidence ceiling is conflated.

### Open taxonomy question

Is this boundary sufficiently distinct from AICE-609 to deserve an independent canonical code?

```
Current answer: PROVISIONALLY_YES
                CANONICAL_PROMOTION_NOT_AUTHORIZED
```

## Portable CAP enforcement requirement (non-implemented)

Associated pattern: `CAUSAL_SCOPE_CLOSURE_BOUNDARY`.

**Core law:** every causal question has its own identity and closure contract.

Question identity should bind at least: `question_id`, `target_outcome`, `conditioning_regime`,
`comparison_basis`, `candidate_mechanism`, `intervention_or_control`, `required_evidence`,
`falsification_boundary`, `status`.

Required invariants:

```
CLOSED(question_id) requires that question's own closure contract PASS
CLOSED(Q1) does not imply CLOSED(Q2)
CONDITIONING_REGIME_A != CONDITIONING_REGIME_B
absolute byte reduction != superiority at matched bytes
partial investigation success != complete investigation closure
```

Evidence transfer requires an explicit bridge that is: declared; evidence-backed; relevant to
the destination; independently checkable; compatible with the destination conditioning regime;
and sufficient for the destination closure contract.

A future deterministic representation may use question objects, evidence-to-question bindings,
verified bridge objects, and a question-result closure matrix.

Required future fixture:

```
Q1 evidence present
Q2 evidence absent
bridge absent
attempted Q2 closure
→ closure rejected
```

Positive control fixture:

```
Q1 evidence present
verified bridge present
Q2 closure contract satisfied
→ Q2 may close
```

```
FUTURE_IMPLEMENTATION_TARGET = cap-processor
IMPLEMENTATION_STATUS = NOT_STARTED
MCP_STATUS = NOT_CONNECTED
```

This section is a specification handoff only. Nothing is implemented here and cap-processor is
not modified by this record.

## Promotion gate

Future canonical promotion requires, in a separate episode:

1. exact source episode preserved;
2. trigger predicates independently reviewed;
3. distinction from AICE-609 established;
4. explicit protection against broadening AICE-602;
5. false-positive boundary accepted;
6. valid negative and positive controls;
7. portable CAP enforcement requirement specified;
8. independent semantic verifier PASS;
9. explicit operator authorization to assign a number;
10. canonical registry / schema / code / example update in a separate episode;
11. tests, commit, publication, and readback performed separately.

No promotion condition is satisfied merely by creating this file.

## Verification status

```
AUTHOR_SELF_REVIEW      = present (not independent)
INDEPENDENT_SEMANTIC_REVIEW = pending (this recording episode; read-only verifier when available)
CANONICAL_PROMOTION     = NOT_AUTHORIZED
```
