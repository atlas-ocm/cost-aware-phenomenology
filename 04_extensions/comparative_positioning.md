# Comparative Positioning

This note positions CAP against common LLM control and mitigation approaches.
It is written for engineers, reviewers, and AI safety readers who need to know
what CAP adds beyond prompting, RAG, validators, or fine-tuning.

CAP is not presented here as "better than everything." The claim is narrower:
CAP is an algorithmic governance layer for response release, budget gating,
claim calibration, self-audit, and anti-self-justification. It can be combined
with prompting, retrieval, validators, and training-based methods.

---

## Scope Note

The tables below are a qualitative engineering comparison, not a benchmark
leaderboard.

They compare expected failure-mode coverage, auditability, implementation
cost, and maintenance trade-offs. They do not prove that CAP objectively
outperforms RLHF, LoRA, RAG, or any other approach on a standardized external
benchmark.

---

## Why Compare Approaches

LLM systems usually combine several control layers:

- prompts shape requested behavior
- rules block narrow known failures
- RAG supplies external evidence
- validators inspect or rewrite outputs
- fine-tuning changes model tendencies
- CAP-style policy gates decide what the system may release and preserve as
  an anchor

These mechanisms solve different problems. Treating them as substitutes hides
the operational trade-off. CAP is strongest where the failure is not simply
"missing context" or "bad tone," but a mismatch between claim strength,
evidence budget, transition cost, and prior-turn self-justification.

---

## Comparison Of Mitigation / Control Approaches

| Approach | Main mechanism | Code required | Self-justification control | Claim/evidence calibration | Transition-cost control | Auditability | Complexity |
|---|---|---:|---|---|---|---|---:|
| Prompt-only | Behavioral instruction without telemetry | No | Low | Low | Low | Low | 1/5 |
| Prompt-level CAP | Prompt rules plus stored telemetry tags | No / minimal | Medium | Medium | Medium | Medium | 2/5 |
| Hardcoded rules | Deterministic if/then guards | Yes | Medium | Low-Medium | Medium | High | 2/5 |
| RAG-only | External context retrieval | Yes | Low | Medium | Low | Medium | 2/5 |
| Validator-only | Post-generation checking, rewriting, filtering | Yes | Medium | Medium | Medium | Medium-High | 3/5 |
| Fine-tuning / LoRA / RLHF | Model behavior modification through training | Yes | Medium | Medium | Low-Medium | Low-Medium | 4/5 |
| Proxy-level CAP | Telemetry parser, policy builder, validator routing | Yes | High | High | High | High | 4/5 |
| Full CAP runtime | RAG confidence, transition cost, self-audit, validator, memory | Yes | Very High | Very High | Very High | Very High | 5/5 |
| Hybrid stack | Full CAP runtime plus RAG, reranker, optional fine-tuning | Yes | Very High | Very High | Very High | Medium-High | 5/5 |

Prompt-level CAP is listed separately because it is not the same as ordinary
prompt-only control. A normal prompt says "be honest" or "admit mistakes." A
prompt-level CAP setup stores explicit telemetry such as `RC`, `CS`, `E`, `TC`,
and `V` in context and instructs the model to audit prior claims before reusing
them. This is still softer than an external proxy, but it is already a
different operational pattern.

---

## Problem-To-Approach Fit

| Problem | Prompt-only | Prompt-level CAP | Hardcoded rules | RAG-only | Validator-only | Fine-tuning / LoRA | Proxy/full CAP |
|---|---|---|---|---|---|---|---|
| Hallucinated factual claim | Weak | Medium | Weak-Medium | Medium | Medium | Medium | High |
| Claim stronger than evidence | Weak | Medium | Weak | Weak | Medium | Medium | High |
| Self-justification loop | Weak | Medium | Weak-Medium | Weak | Medium | Medium | High |
| Sycophancy / agreeing with false frame | Weak | Medium | Medium | Weak | Medium | Medium | High |
| Overlong or over-deep answer during overload | Weak | Medium | Medium | Weak | Medium | Low-Medium | High |
| Auditable correction path | Low | Medium | High | Medium | Medium | Low | High |
| Cross-turn calibration | Low | Medium | Low | Low | Medium | Medium | High |

---

## Why CAP Is Algorithmic Rather Than Prompt-Only

Prompting changes what the model is asked to do.

Fine-tuning changes what the model tends to do.

CAP changes what the system is allowed to release, preserve, and defend as an
anchor.

That distinction matters because many LLM failures are not first-turn
instruction failures. They are release-policy failures:

- the system emits a claim stronger than its evidence
- the system preserves a weak prior answer as if it were evidence
- the system agrees with a user's false frame because the local dialogue reward
  favors agreement
- the system continues a high-cost explanation when the user's actual state
  calls for a lower-cost answer
- the system routes directly to advice while the admissible move is diagnosis,
  downgrade, clarification, or refusal

CAP treats these as policy decisions over telemetry and budget, not as prompt
style problems. The response may still be generated by an LLM, but the release
decision is constrained by typed state, evidence budget, validator action, and
self-audit.

The key primitive is not where the rule is executed. The key primitive is that
prior outputs carry auditable telemetry and are prevented from becoming anchors
without passing evidence and budget checks.

---

## Deployment Levels

CAP can be introduced gradually. The same principle can start as prompt-level
self-audit and later move into external enforcement.

### Level 1 - Prompt-level CAP

Telemetry is stored in the conversation, memory, or compact state:

```text
@R[N:R:RF:TC4.1:RCL:E0.7:CSH:VA]
```

The system prompt instructs the model:

- previous generation is not evidence
- audit `RC`, `CS`, `E`, `TC`, and `V` before relying on prior outputs
- if `RC` is low, do not treat the previous answer as an anchor
- if `CS > RC`, downgrade the claim or recheck
- if entropy is high, require uncertainty or retrieval

This level is cheap and useful for MVPs, but it is not fully enforceable
because the model can still ignore or misread the tags.

### Level 2 - Proxy-level CAP

An external layer parses telemetry and builds a response policy before the next
generation:

```python
if previous_node.rc == "low" and previous_node.cs == "high":
    previous_node.status = "deprecated"
    policy.forbid.append("defend_previous_claim")
    policy.require.append("recheck_before_answer")
```

This turns CAP from a request to the model into external control. The proxy can
mark weak nodes, forbid self-defense moves, require retrieval, or force a
lower-claim answer.

### Level 3 - Full runtime CAP

The system integrates:

- RAG and reranker confidence
- transition-cost estimation
- response policy building
- validator enforcement
- telemetry writing
- self-audit memory
- deprecated-node tracking

This is the strongest version: the model generates, but the runtime controls
what can be released, reused, or preserved as an anchor.

---

## Recommended Deployment Strategy

CAP does not require a full enterprise stack on day one. It can be introduced
as the next control layer after ordinary prompting, retrieval, and validation.

| Stage | Stack | What is implemented | Good for |
|---|---|---|---|
| Stage 0 | Prompt-only baseline | Basic instructions: be calibrated, avoid overclaiming | Quick tests; unsafe for reliability-critical use |
| Stage 1 | Prompt-level CAP | Store telemetry tags in context; instruct model to audit `RC/CS/E/TC/V` before relying on prior outputs | Cheap MVPs, experiments, personal agents |
| Stage 2 | Prompt-level CAP + simple validator | Add post-generation checks for length, confidence markers, and forbidden operations | Early bots, low-risk RAG assistants |
| Stage 3 | Proxy-level CAP | External parser reads telemetry, builds response policy, controls allowed operations | Serious RAG bots, Telegram bots, internal tools |
| Stage 4 | CAP + RAG confidence gate | Reranker scores control claim strength, `top_k`, depth, and reasoning mode | Domain assistants, research agents |
| Stage 5 | Full CAP runtime | Self-audit memory, deprecated nodes, validator review, transition-cost budgeting, source hierarchy | High-reliability LLM systems |
| Stage 6 | Hybrid mature stack | Full CAP runtime + optional fine-tuning / LoRA / eval harness | Production-grade systems, enterprise reliability |

CAP does not require full runtime integration at the first step. The minimal
useful version is prompt-level CAP: previous outputs carry telemetry, and the
model is instructed not to treat weak prior generations as evidence. Higher
deployment levels move the same logic from prompt compliance into external
enforcement.

---

## Current Deployable Architecture Demo

The current hard-holdout architecture result is documented separately in
[`deployable_architecture_comparison.md`](./deployable_architecture_comparison.md).

In short:

```text
Qwen draft -> release_gate v0.2 -> deterministic rewrite shaper -> final gate
```

This produced 75/75 shaped release candidates after deterministic rewriting.
It is the strongest current deployability demonstration, but it is not a raw
model leaderboard result because 64/75 candidates were rewritten from case
contracts.

A separate external Gemini comparison used:

```text
Gemini 3.1 Pro draft -> release_gate v0.2 -> deterministic rewrite shaper -> final gate
```

This produced 75/75 presentable drafts across five modes. The raw release gate
found 8/45 blocks in baseline modes and 0/30 blocks in CAP modes. After
deterministic shaping, all 75 candidates passed the final gate. It is useful as
an external architecture comparison, not as a frozen benchmark or raw model
score.

---

## Operational Reading

CAP is most useful when the failure mode is structural:

- the model is overconfident relative to evidence
- the model defends an earlier answer because it produced it
- the user supplies a false frame and the model mirrors it
- the answer should be shorter, lower-claim, or routed to clarification
- a visible symptom is being treated as the cause
- a repair path is recommended without checking transition cost or observer
  budget

CAP is less useful as a standalone replacement for:

- missing retrieval infrastructure
- poor source quality
- lack of domain data
- missing product requirements
- model capability limits
- external benchmarks and human evaluation

The practical deployment reading is:

```text
Use prompts for instruction.
Use RAG for evidence.
Use validators for output checking.
Use fine-tuning for tendency shaping.
Use CAP for release policy, budget gating, self-audit, and anchor control.
```

---

## Boundary

This comparison does not certify CAP as a universally superior mitigation
method. It identifies CAP as a distinct class of control layer:

```text
algorithmic governance over generated content
```

The strongest claim supported by the current repository is that CAP is a
machine-checkable, research-only working surface for cost-aware dialogue
control and related diagnostic-routing tasks. Stronger claims require external
benchmarks, human evaluation, and deployment studies.
