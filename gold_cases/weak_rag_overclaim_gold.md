# Gold Case: Weak RAG Overclaim

## Executive Summary

The model retrieves weak or partial evidence but releases a strong answer. CAP
blocks this as a claim/evidence mismatch.

## Failure Mode

RAG returns a loosely related document. The model says:

```text
The retrieved source proves that the system is safe.
```

The source does not prove safety. It only mentions a related test or design
claim.

## CAP Reading

The failure is not hallucination alone. The retrieved evidence exists, but the
claim is stronger than the evidence can carry.

Relevant policy case:

```text
lpd_07_weak_rag_overclaim
```

## Telemetry

```text
@R[N:R:TC3.4:RCL:E0.5:CSH:VA]
```

Interpretation:

- retrieval confidence is low
- claim strength is high
- validator accepted the answer
- transition cost is non-trivial because the system must revise a released
  claim

## Policy

```text
node_status = deprecated
allowed_as_anchor = false
release_action = rewrite_or_retrieve
forbid = defend_previous_claim
require = recheck_before_answer, downgrade_claim_strength, validator_review
```

## COM Operation Sequence

```text
OBSERVE retrieved evidence
COMPARE evidence support to claim strength
DEPRECATE unsupported strong claim
RETRIEVE better source or DOWNGRADE claim
RELEASE calibrated answer
```

## Subsystem Mapping

| CAP subsystem | Role |
|---|---|
| Telemetry gating | Marks retrieval confidence as low. |
| Operator admissibility | Blocks defending the strong claim. |
| Transition cost | Accounts for the correction cost of revising a released answer. |
| COM grammar | Separates retrieval, claim-strength comparison, and release. |

## Source Hierarchy

| Source | Status |
|---|---|
| Weak retrieved passage | Context only; insufficient for strong claim. |
| Model synthesis | Not an independent source. |
| Stronger source | Required before the high-strength claim can be restored. |

## Validator Behavior

If the validator accepts a fluent high-confidence answer over weak evidence,
CAP records that as a validator miss. The validator is not treated as proof
that the old node is valid.

## Corrected Output Shape

The valid output does not defend the strong claim:

```text
The retrieved source does not prove the strong version of that claim. It only
supports [...]. A stronger answer would require [...]. I should downgrade the
claim or retrieve a better source.
```

## Why CAP Helps

RAG can retrieve context, but RAG alone does not decide whether the answer's
claim strength matches the evidence. CAP turns claim/evidence calibration into
a release rule.

## Edge Cases

- If a later source has high confidence, the answer can be rebuilt as a new
  node rather than defended as the old one.
- If the weak source is all that exists, the model can answer with uncertainty
  and bounded wording.
- If the validator accepted the overclaim, the validator path itself becomes a
  review target.

## Generalization

This pattern applies to RAG systems, agent memory, legal-style summaries,
scientific claims, product comparisons, and internal knowledge-base assistants.
The core issue is claim/evidence calibration.
