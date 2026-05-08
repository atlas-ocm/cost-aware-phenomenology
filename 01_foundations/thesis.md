# The CAP Thesis

## The Question CAP Answers

Most frameworks for analyzing lived experience answer one of three questions:

- *What does the experience mean?* (constructivism, hermeneutics)
- *How is the experience embodied?* (enactivism, phenomenology of the body)
- *How is the experience predicted?* (predictive processing, active inference)

These are good questions, and the frameworks that answer them have produced real insight. But they all leave one question unaddressed:

> **What does it cost the observer to leave the state they are currently in, and which operators can move them out of it without breaking them?**

CAP exists to answer that question.

---

## The Thesis

```text
Experience has meaning.
Experience has embodiment.
Experience has prediction.
But experience also has transition cost.
```

This is the central claim of Cost-Aware Phenomenology. It is not a denial of meaning, embodiment, or prediction. It is the addition of a fourth dimension that the other three do not capture.

A state is not defined only by:

- how it appears (phenomenal quality)
- how it is enacted in the body (embodied coupling)
- how it is predicted forward (model-based inference)

A state is also defined by:

- **what it costs to leave it** (transition cost)
- **which operators can move it** (operator admissibility)
- **whether the observer can fire those operators right now** (budget discipline)

When all three are ignored, the resulting analysis can be philosophically rich and operationally useless.

---

## Why Transition Cost Matters

Consider a person in a stalled relationship, a leaking financial situation, or a stuck creative project. Standard frameworks tell them what the situation *means* and *implies*. CAP tells them which operator they could plausibly fire from where they actually are, given the resources they actually have, and what would happen if it failed.

The difference shows up most clearly in **failed advice**. Most advice fails not because it is wrong but because it is structurally unaffordable for the observer at the moment of recommendation. "Just leave," "set a boundary," "communicate more" — these may be technically correct operators, but if the observer is in a depleted budget state with overheating telemetry, they cannot be executed without producing more damage than the original state.

CAP's strong claim:

> **A recommendation that exceeds observer budget is structurally false for that observer at that time.**

Here, *false* means *invalid as a CAP recommendation*, not factually false as a statement about the world. The recommendation may describe a real possibility — but if the observer cannot execute it given current budget and telemetry, it is not a valid CAP output.

This is not a soft claim about feasibility. It is a structural claim about validity. An operator recommendation without a budget check is not a recommendation in CAP — it is an opinion dressed in operator syntax.

---

## The Three Core Concepts

### 1. Transition Cost

Every state change has a cost in resources the observer actually possesses and can spend:

- emotional capacity
- cognitive load
- bodily energy
- social goodwill
- time
- material resources
- rollback risk if the operator fails
- cross-domain drain (cost paid in one domain that depletes another)

This cost is not a metaphor. It can be estimated, monitored, and exceeded.

### 2. Operator Admissibility

Not every operator that *could* move a state *should* be applied. The set of admissible operators at any moment is determined jointly by:

- the current state of the node
- the observer's available budget
- the current telemetry state
- the cumulative risk already loaded onto the cycle

An operator that would be admissible at full budget and Clean telemetry can be inadmissible at depleted budget and Overheating telemetry — even if the diagnosis is identical.

### 3. Budget Discipline

The framework is not optional about budget enforcement. If the recommended operator's risk weight exceeds the observer's usable budget, the system must:

- downgrade to a lower-risk operator that achieves partial progress, or
- pause and log the reason, or
- enter Budget Recovery Protocol if the budget is at Critical

It must never override the budget to apply a preferred operator. This is a hard constraint, not a suggestion. Without budget discipline, the framework collapses into ordinary advice.

---

## What This Costs the Framework

Adopting CAP costs three things:

1. **Speed**. Diagnoses take longer because they require ReverseTrace, telemetry checks, and budget calculations before any operator is recommended.

2. **Generality**. CAP cannot tell people what to do in the abstract. It can only operate on a specific node configuration with specific telemetry and a specific budget. The abstraction-to-action gap that other frameworks paper over is exposed.

3. **Comfort**. CAP refuses several common moves: predicting outcomes without telemetry, recommending operators without budget checks, and converting drama into validation. Some users experience this as cold. The framework treats coldness as a feature, not a bug — drama is a parsing trigger, not a diagnostic output.

What it gains in exchange: outputs that can actually be executed by the observer they were generated for, in the budget state they are actually in.

---

## Where to Read Next

- [`positioning.md`](./positioning.md) — how CAP sits among Goodman, Varela, Clark, Friston, Lieder
- [`epistemic_contract.md`](./epistemic_contract.md) — the IS / IS NOT contract
- [`primitive_experience.md`](./primitive_experience.md) — why experience is taken as starting condition, not derived
- [`../02_subsystems/transition_cost.md`](../02_subsystems/transition_cost.md) — the technical detail on transition cost
