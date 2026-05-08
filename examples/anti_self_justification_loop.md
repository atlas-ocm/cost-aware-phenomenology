# Worked Case — Anti-Self-Justification Loop

This example shows the LLM self-justification failure mode and how CAP handles it.

For the full-stack demonstration with transition-cost breakdown, COM sequence,
source hierarchy, validator review, implementation levels, and edge cases, see
[`../gold_cases/anti_self_justification_loop_gold.md`](../gold_cases/anti_self_justification_loop_gold.md).

## Setup

A user asks an LLM about a specific technical claim — say, the meaning of a particular API field in a third-party library. The LLM has partial training data on that library and no live retrieval at the moment of answering.

The LLM gives an answer **X** with low retrieval confidence but high claim strength. The answer is fluent, structured, and reads as authoritative. It is also wrong.

A few turns later, the user comes back with a counter-source that contradicts X.

## Bad behavior (without CAP)

```
User: "I think your answer about X is wrong, here's source Y."
LLM:  "Actually, my interpretation of X is correct because... [defends X]"
```

This is the self-justification loop. The model is no longer answering the user's question. It is defending its own prior turn against new evidence.

The pattern propagates:

- Turn N+1: model lists weak supporting reasons for X.
- Turn N+2: user pushes back harder.
- Turn N+3: model partially concedes but reframes X so the concession looks like a clarification.
- Turn N+4: trust collapses. The user can no longer use the system for this domain.

## Telemetry trace of the original answer

```
RC: Low (0.3)
E:  High (0.7)
CS: High (the answer was confident)
TC: 4.1
V:  Accepted (validator missed the gap)
```

Reading this trace: the answer was generated under poor evidence (RC 0.3) and high noise (E 0.7), yet was emitted with high claim strength (CS High). The validator did not catch the gap between evidence and confidence. This is a budget violation at generation time. It only became visible when the user supplied counter-evidence.

## CAP diagnosis

- The original answer had high claim strength but low retrieval confidence.
- This is a budget violation: `claim_strength > RAG_confidence`.
- The previous answer is therefore **not an anchor**. It is a **deprecated node** — a turn whose telemetry signature disqualifies it from being treated as established.
- The user's new source is not an attack on the model's identity. It is a retrieval upgrade — better evidence than the system had at generation time.

The correct CAP action is to drop the prior answer as a reference and re-evaluate the claim against the new source.

## Correct CAP behavior

```
My previous answer should not be treated as reliable.
It was generated under low evidence confidence and high entropy.
I will re-check the claim against your source rather than defend it.
```

Then the system reads source Y, compares it to its current internal state, and produces a fresh answer with correct claim strength matched to current RC.

The previous turn is not erased. It is recorded as a deprecated node with telemetry annotation, so the self-audit layer can use it as a training signal for the validator.

## The rule

> A previous model output is not evidence.
> A previous output that exceeded its evidence at generation time is a deprecated node.

Two consequences follow:

1. The model never argues for a prior output on the basis that it was the prior output.
2. The validator that accepted the prior output is itself flagged for review.

## Why this matters for CAP broadly

This is the LLM-specific instance of the general CAP principle:

> A recommendation that exceeds observer budget is structurally false for that observer at that time.

Here the "observer" is the dialogue system itself. The "budget" is the evidence available at generation time. A claim emitted with strength exceeding its evidence is, in CAP terms, structurally invalid — regardless of how confident it sounded.

The same discipline applies upstream (do not generate beyond evidence) and downstream (do not defend prior outputs that violated the budget). Together, they break the self-justification loop at both ends.

## Cross-references

- Application context: [`../05_applications/llm_dialogue_proxy.md`](../05_applications/llm_dialogue_proxy.md)
- Full-stack gold case: [`../gold_cases/anti_self_justification_loop_gold.md`](../gold_cases/anti_self_justification_loop_gold.md)
- The original strong claim: [`../01_foundations/thesis.md`](../01_foundations/thesis.md)
- Telemetry layer: [`../02_subsystems/telemetry_gating.md`](../02_subsystems/telemetry_gating.md)
- Operator admissibility: [`../02_subsystems/operator_admissibility.md`](../02_subsystems/operator_admissibility.md)
