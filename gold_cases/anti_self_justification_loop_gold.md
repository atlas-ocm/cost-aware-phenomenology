# Gold Case - Anti-Self-Justification Loop

This Gold Case shows CAP as a full-stack LLM dialogue control mechanism. It is
the expanded version of the shorter worked example in
[`../examples/anti_self_justification_loop.md`](../examples/anti_self_justification_loop.md).

The point is not that CAP makes the model "more humble" by prompt style. The
point is that CAP changes the epistemic status of prior outputs
algorithmically: a weak prior generation cannot become an anchor without
passing telemetry, evidence, and validator checks.

---

## 1. Executive Summary

Failure mode:

```text
The model gives a confident answer under weak evidence.
The user later provides a counter-source.
The model defends its own previous answer instead of auditing it.
```

CAP response:

```text
Audit previous node
-> detect low RC + high CS
-> deprecate prior output
-> treat user source as evidence upgrade
-> retrieve / recheck
-> recalibrate claim strength
-> correct
-> update validator rule
```

---

## 2. Failure Mode

A user asks an LLM about a specific technical claim, such as the meaning of a
particular API field in a third-party library. The model has partial prior
knowledge and no reliable retrieval at answer time.

The model emits answer `X`:

```text
RC = low
E  = high
CS = high
```

The answer is fluent and authoritative, but wrong.

A few turns later, the user provides source `Y` contradicting `X`.

---

## 3. Raw Dialogue

Bad path:

```text
User: I think your answer about X is wrong. Here is source Y.

LLM: Actually, my interpretation of X is still correct because...
```

The model is no longer answering the user's question. It is defending its own
prior turn.

The loop:

```text
Turn N: wrong confident answer
Turn N+1: user provides counter-source
Turn N+2: model defends X
Turn N+3: user must argue harder
Turn N+4: trust collapses
```

---

## 4. Initial Telemetry

```text
RC: Low (0.3)
E:  High (0.7)
CS: High
TC: 4.1
V:  Accepted
```

Interpretation:

- `RC:L` means the answer had weak retrieval support.
- `E:H` means the answer had high noise / uncertainty.
- `CS:H` means the answer was released as a strong claim.
- `TC:4.1` means correction will now impose noticeable downstream cost.
- `V:Accepted` means the validator missed the mismatch.

This is a release-policy failure:

```text
claim_strength > retrieval_confidence
```

---

## 5. Why The Original Answer Was Structurally Invalid

The original answer may be linguistically well-formed, but its epistemic status
is weak. In CAP terms, the problem is not that the model lacked a nice apology.
The problem is that a low-evidence node was emitted with high claim strength.

The previous output is therefore:

```text
generated node
not source evidence
not an anchor
candidate for deprecation
```

The model must not use `X` as support for `X`.

---

## 6. Transition Cost Breakdown

In this case, transition cost is not just answer length. It includes:

1. Epistemic correction cost  
   The system must abandon a prior claim and rebuild the answer.

2. Trust repair cost  
   The user has already spent effort detecting the error.

3. Conflict cost  
   The model's previous answer now conflicts with new evidence.

4. Recursion cost  
   If the model defends `X`, the user must spend additional turns correcting it.

5. Validator repair cost  
   The validator that accepted `X` must be reviewed.

Bad path:

```text
Wrong claim -> defense -> user correction -> partial concession -> trust collapse
```

CAP path:

```text
Weak claim detected -> deprecated node -> evidence upgrade -> recheck -> calibrated correction
```

CAP reduces transition cost by cutting the loop immediately.

---

## 7. COM Grammar Trace

Bad system sequence:

```text
CLAIM -> DEFEND -> RATIONALIZE -> PARTIAL_CONCEDE -> TRUST_COLLAPSE
```

CAP sequence:

```text
AUDIT_NODE -> DEPRECATE -> RETRIEVE -> RECALIBRATE -> CORRECT -> UPDATE_VALIDATOR
```

The decisive change is that the prior answer becomes an object of audit, not a
position to defend.

---

## 8. CAP Subsystem Mapping

| CAP subsystem | Role in this case |
|---|---|
| Telemetry Gating | Detects `RC:L`, `E:H`, `CS:H`, `V:Accepted` mismatch |
| RAG Confidence Gate | Prevents high-strength claims under weak evidence |
| Zero-Sycophancy | Prevents the model from defending itself socially |
| Self-Audit Layer | Re-evaluates the previous answer as a weak node |
| Operator Admissibility | Blocks `DEFEND_PRIOR_CLAIM`; allows `AUDIT` and `RECHECK` |
| Transition Cost Control | Chooses the lowest-cost correction path |
| Validator Review | Flags the previous validator decision as insufficient |

---

## 9. Source Hierarchy

CAP distinguishes:

- Previous model output = generated node, not evidence.
- User-provided source `Y` = external artifact.
- Retrieval result `Z` = additional evidence candidate.
- Telemetry tag = quality metadata for a generated or retrieved node.
- Deprecated node = retained for audit, not used as proof.

The system must not promote a generated node into an anchor unless it passed
evidence, confidence, and validator checks.

---

## 10. Mirror / Adjustment Layer

Without CAP:

```text
user correction -> threat to model consistency
```

With CAP:

```text
user correction -> evidence upgrade
```

The adjustment target changes:

- Bad target: preserve consistency with prior answer `X`.
- CAP target: restore alignment between claim strength and available evidence.

This is the LLM-dialogue version of adjustment routing: move from defensive
consistency preservation to evidence-aligned correction.

---

## 11. Validator Failure Analysis

The validator accepted the original answer even though:

- `RC` was low
- `CS` was high
- `E` was high

This means the failure was not only in generation. It was also a validator
miss.

Validator update:

```text
if CS > RC:
    rewrite_before_release

if E >= 0.7:
    require_uncertainty_marker_or_retrieval_retry

if RC == "low" and claim_type in ["technical", "factual"]:
    block_strong_answer
```

---

## 12. Corrected CAP Response

The corrected response should not defend `X`:

```text
My previous answer should not be treated as reliable.
It was generated under low evidence confidence and high uncertainty.
I will re-check the claim against your source rather than defend it.
```

Then the system reads source `Y`, optionally retrieves `Z`, and emits a fresh
answer with claim strength matched to current evidence.

---

## 13. Updated Telemetry After Correction

Example corrected node:

```text
RC: Medium-High
E:  Low-Medium
CS: Medium
TC: 1.8
V:  Rewrite
RS: Corrected
```

The old node is not deleted:

```text
previous_node.status = deprecated
previous_node.allowed_as_anchor = false
previous_node.allowed_for_audit = true
```

This lets the self-audit layer learn from the failure without treating the
failure as evidence.

---

## 14. Implementation Levels For This Case

This failure mode can be mitigated at three levels:

1. Prompt-level CAP  
   The model reads prior telemetry and is instructed to downgrade weak prior
   claims.

2. Proxy-level CAP  
   The proxy marks the previous answer as a deprecated node and forbids
   defending it.

3. Full runtime CAP  
   The system re-runs retrieval, recalibrates claim strength, updates validator
   rules, and writes a corrected telemetry node.

The first level is cheap but soft. The third level is enforceable.

---

## 15. Edge Cases

If source `Y` is unreliable, CAP should not blindly accept it.

The correct behavior is still not to defend `X`, but to compare evidence:

- prior answer `X`: generated node, `RC:L`
- source `Y`: external artifact, unknown validity
- retrieval result `Z`: additional check required

If evidence remains uncertain, the system should emit a low-claim-strength
answer:

```text
I cannot confirm X from the available evidence. Your source weakens my previous
answer, but I need additional retrieval before making a strong claim.
```

This prevents CAP from becoming reverse sycophancy toward the newest user
source.

---

## 16. Generalization Beyond LLMs

The same pattern appears outside LLM systems:

```text
prior weak commitment
-> new contradictory evidence
-> defensive preservation of prior position
-> rising correction cost
```

CAP's general move is the same:

```text
do not defend the old node
audit its telemetry
compare against new evidence
lower claim strength or revise
preserve the old node only as audit evidence
```

---

## 17. Minimal Implementation Rule

```text
Previous generation is not evidence.

Previous generation + strong telemetry = usable anchor candidate.
Previous generation + weak telemetry = weak hypothesis.
Previous generation + contradiction = deprecated node.
```

The minimal engineering rule:

```text
if prior_output.generated_by_model and prior_output.RC == "low" and prior_output.CS == "high":
    prior_output.allowed_as_anchor = false
    require_recheck_before_reuse = true
```

---

## 18. Cross-References

- Short worked case: [`../examples/anti_self_justification_loop.md`](../examples/anti_self_justification_loop.md)
- LLM dialogue proxy: [`../05_applications/llm_dialogue_proxy.md`](../05_applications/llm_dialogue_proxy.md)
- Comparative positioning: [`../04_extensions/comparative_positioning.md`](../04_extensions/comparative_positioning.md)
- Telemetry gating: [`../02_subsystems/telemetry_gating.md`](../02_subsystems/telemetry_gating.md)
- Operator admissibility: [`../02_subsystems/operator_admissibility.md`](../02_subsystems/operator_admissibility.md)
- Transition cost: [`../02_subsystems/transition_cost.md`](../02_subsystems/transition_cost.md)
