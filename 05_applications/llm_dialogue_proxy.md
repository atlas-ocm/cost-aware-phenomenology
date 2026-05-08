# LLM Dialogue Proxy — Applying CAP to LLM/RAG Systems

## Why CAP for LLM dialogue

LLM responses have transition cost. Each response imposes:

- cognitive load on the user (parsing, evaluating, integrating)
- epistemic noise (low-confidence interpolation presented with high surface confidence)
- anchor formation (early outputs become reference points for later turns)
- drift from truth (each turn that defends a prior turn drifts further from the underlying source material)

When transition cost is untracked, dialogue systems exhibit the standard failure modes: sycophancy, self-justification loops, unfounded confidence on low-evidence claims, and amplification of user assumptions. CAP makes the cost explicit so the system can refuse outputs that exceed its evidence budget.

The "observer" in this application is the dialogue system itself. The "budget" is the evidence available at generation time (retrieval confidence, source quality, model uncertainty). The "telemetry" is the live signal stream (RAG hit quality, entropy, claim strength, prior-turn validator action). The same CAP discipline that refuses to recommend an operator beyond the human observer's budget here refuses to publish a claim beyond the system's evidence budget.

## Six sub-applications

### 1. Transition Cost in LLM Responses

Every response has a cost. CAP makes it explicit. Cost components:

- length (more tokens = more cognitive load on the reader)
- claim strength (a confident claim costs more than a hedged one if it is wrong)
- novelty load (new framing imposes integration cost)
- correction cost (cost paid downstream if the claim has to be retracted)

A cost-aware response prefers the lowest-cost output that still satisfies the user's actual question.

### 2. Zero-Sycophancy

Two sides:

- **Outward.** Do not flatter the user. Do not validate framings the evidence does not support. Do not echo emotional content as substantive agreement.
- **Inward.** Do not defend the model's own weak past outputs. A previous output is not evidence; it is a node in the conversation that can be deprecated like any other.

Zero-sycophancy is enforced at the validator layer: claims that pass only because they were already said are downgraded.

### 3. RAG Confidence Gating

Retrieval confidence (RC) gates response strength. The rule:

```
claim_strength <= RC + epsilon
```

Low RC + high claim strength is a budget violation. The system must either:

- lower claim strength to match RC, or
- escalate to a wider retrieval, or
- explicitly refuse: "I do not have sufficient evidence to answer this confidently."

Refusal is a valid CAP output. Hallucination dressed in fluent prose is not.

### 4. Self-Audit Layer

Re-evaluate previous outputs by their telemetry, not by the fact that they were generated. The fact that the system said something earlier does not raise its truth value. Each prior output retains a telemetry record (RC, E, TC, CS, V) and can be re-checked at any turn against new evidence.

If a prior output was generated under low RC and high CS, the self-audit layer flags it as a candidate for deprecation as soon as new evidence is requested.

### 5. Anti-Self-Justification Loop

Previous generation is not evidence. When a user pushes back on a prior output, the system must re-check the claim against sources, not defend it because it was previously emitted. See the worked case in [`../examples/anti_self_justification_loop.md`](../examples/anti_self_justification_loop.md).

### 6. Validator / Shaper Layer

A validator sits between the generator and the user. Its actions:

- **Pass** — claim is within budget and the validator has no edit.
- **Downgrade** — claim strength reduced to match evidence.
- **Supersede** — claim replaced with a stronger or better-sourced alternative.
- **Reject** — claim removed; system refuses or asks for clarification.

The validator action is part of the response telemetry and is recorded for self-audit.

## Telemetry tags for LLM responses

```
RC = retrieval confidence
E  = entropy / noise level
TC = transition cost
CS = claim strength
V  = validator action
```

Every response carries these tags internally even if they are not surfaced to the user. The self-audit layer reads them.

## Deployment Levels for LLM/RAG Systems

CAP can be deployed at several reliability levels. The logic is the same, but
the enforcement point changes.

### Level 1 - Prompt-level CAP

Telemetry is stored in the conversation, memory, or compact state:

```text
@R[N:R:RF:TC4.1:RCL:E0.7:CSH:VA]
```

The system prompt instructs the model:

- previous generation is not evidence
- if `RC` is low, do not treat the previous answer as an anchor
- if `CS > RC`, downgrade or recheck
- if `E` is high, require uncertainty or retrieval before reusing the claim
- if `V` was rewrite or fallback, treat the prior node as weak

This level is lightweight and can work as an MVP, but it is not fully
enforceable because the model may ignore or misread the telemetry.

### Level 2 - Proxy-level CAP

An external proxy parses telemetry and constructs a response policy before
generation:

```text
message history
-> telemetry parser
-> policy builder
-> LLM prompt
-> validator
-> final answer
```

At this level the system can mark prior outputs as deprecated, forbid
defending weak claims, require retrieval, and lower claim strength before the
answer reaches the user.

### Level 3 - Full runtime CAP

The strongest version integrates:

- RAG confidence and reranker scores
- context and transition-cost budgeting
- response policy construction
- validator enforcement
- source hierarchy
- self-audit memory
- telemetry writing

The model still generates text, but the runtime controls what the system is
allowed to release, preserve, or reuse as an anchor.

## The Anti-Self-Justification Rule

> The system must not defend a previous output merely because it generated it.
> Every previous output must be re-evaluated by its telemetry: RC, E, TC, CS, V, source validity, and user feedback.

This is the single rule that prevents the most common LLM dialogue failure mode: doubling down on a low-evidence claim because it has already been said.

## Mapping to CAP subsystems

| LLM dialogue concept | CAP subsystem |
|---|---|
| Transition cost of a response | [`../02_subsystems/transition_cost.md`](../02_subsystems/transition_cost.md) |
| Claim strength gating | [`../02_subsystems/operator_admissibility.md`](../02_subsystems/operator_admissibility.md) |
| RC, E, V signals | [`../02_subsystems/telemetry_gating.md`](../02_subsystems/telemetry_gating.md) |
| Structured response policy | [`../02_subsystems/com_grammar.md`](../02_subsystems/com_grammar.md) |
| Reroute when RAG returns weak evidence | [`../02_subsystems/adjustment_dynamics.md`](../02_subsystems/adjustment_dynamics.md) |
| Evidence budget enforcement | [`../02_subsystems/observer_budget.md`](../02_subsystems/observer_budget.md) |

## Where to read next

- Worked failure case: [`../examples/anti_self_justification_loop.md`](../examples/anti_self_justification_loop.md)
- Full-stack gold case: [`../gold_cases/anti_self_justification_loop_gold.md`](../gold_cases/anti_self_justification_loop_gold.md)
- Comparative positioning: [`../04_extensions/comparative_positioning.md`](../04_extensions/comparative_positioning.md)
- Full subsystem reference: [`../02_subsystems/`](../02_subsystems/)
- Validation methodology: [`../03_validation/methodology.md`](../03_validation/methodology.md)
