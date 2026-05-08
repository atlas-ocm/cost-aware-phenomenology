# Adjustment Dynamics

The Adjustment Layer (also: Path Reweighting Layer) is CAP's **forward routing engine**. Where the COM Grammar parses the current state, and the Looking-Glass extension diagnoses the upstream cause, the Adjustment Layer answers the forward question:

> Given the current pressured state, the observer's budget, the known leakage patterns, and (optionally) an upstream bridge from Looking-Glass, **what admissible future paths still exist**?

This document covers the Adjustment Layer's two input modes, two bridge constructions, and three runtime guards.

Status: `research-only / three-model identity-verified / holdout clean`. See [`../03_validation/adjustment_layer.md`](../03_validation/adjustment_layer.md) for full validation results.

---

## Purpose

The Adjustment Layer is useful when the system has a current pressured or damaged state and needs to ask:

```text
What forward paths are still admissible under current constraints?
What is the minimal deformation of the route field?
Which routes are blocked by budget exhaustion?
Which routes are structurally invalid due to known leakage?
How does an upstream bridge from Looking-Glass inform forward routing?
```

The layer is **not** a claim that desired outcomes are guaranteed, that advice replaces routing, or that impossible jumps can be constructed.

---

## What the Layer Receives

```text
S0          : current observed state
St          : desired or required stabilized state
A           : hard anchors (constraints that cannot be moved)
P*          : observer-intent or problem-pressure vector
P(path)     : prior transition model
R           : available observer budget
L           : known leakage / contradiction patterns
upstream    : (optional) Looking-Glass bridge diagnosis
```

## What the Layer Outputs

```text
Q(path)              : reweighted admissible path distribution
trajectories         : low-cost trajectory candidates
budget_blocked       : routes that exceed observer usable budget
leakage_invalidated  : routes invalidated by structural leakage
rupture_score        : conflict / contradiction measure
repair_requirements  : stabilization conditions needed
boundary_rules       : reconfiguration rules for the new route
```

---

## Two Input Modes

### Desire Pressure

```text
Input: an intended or attractive future state
Question: I want X. What admissible routes from S0 to X exist?
Output: prospective route candidates with risk weights and budget gates
```

This is close to prospective route finding. It does not guarantee delivery — it identifies what is reachable under the current constraints. Routes that exceed the budget are reported as `budget_blocked`. Routes that pass through known leakage patterns are reported as `leakage_invalidated`.

The mode is honest: it can return "no admissible path under current constraints," which is a valid output. The framework does not invent a path to satisfy the desire.

### Problem Pressure

```text
Input: a damage, deficit, or hard problem event
Question: Something broke. How do we route toward stabilization?
Output: recovery route candidates from the damaged state
```

This is not desire fulfillment. It is recovery routing under a new constraint. Examples:

- debt
- illness
- lost work
- damaged relationship
- legal issue
- depleted reserve
- dependent-being emergency

Problem-pressure routing is structurally different from desire-pressure routing because it does not optimize toward a desirable target — it optimizes toward a stabilizable state. The target is "carryable" rather than "preferred."

---

## Markov Bridge Mode

```text
Given S0 and St,
find admissible intermediate states
that preserve local transition validity.
```

The Markov Bridge asks: what sequence can get from the current state to the target state without impossible jumps?

This is the local path-construction mode. It produces explicit intermediate states such that each transition between adjacent states is locally valid (admissible operator exists, transition cost fits budget, telemetry supports it).

Markov Bridge is used twice in advanced analysis:

```text
A -> intermediate states -> B  (test whether the latent cause produces the observed rupture)
B -> intermediate states -> C  (build a repair route)
```

The first bridge is diagnostic; the second is constructive.

---

## Schrödinger Bridge Mode

```text
Minimally deform P(path) into Q(path)
so that new boundary constraints become satisfiable
while preserving prior dynamics as much as possible.
```

The Schrödinger Bridge is the distribution-reweighting mode. It does not construct a single path; it deforms the entire path distribution as little as possible to make the new constraints satisfiable.

Practical reading: **do not summon an impossible route. Reweight the reachable route field under anchors, costs, and constraints.**

The Schrödinger Bridge is what allows the framework to honestly say "your prior trajectory and your new constraints are compatible only with this much deformation" — and if the deformation cost exceeds the budget, the path is blocked.

---

## The Three Runtime Guards

### 1. Budget Gate

```text
BudgetGate(route, observer_budget):
    if cost(route) > observer.AllowedTotalRisk:
        return BLOCK("route exceeds usable budget")
```

Routes whose cumulative cost exceeds the observer's usable budget are blocked. The framework does not silently downgrade them — it reports them as `budget_blocked` so the observer knows what was disallowed and why.

This is the same budget discipline as in the COM Grammar layer (see [`observer_budget.md`](./observer_budget.md)). The Adjustment Layer enforces it across multi-step forward routes, not just single operators.

### 2. Leakage Screen

```text
LeakageScreen(route, leakage_patterns):
    for pattern in leakage_patterns:
        if route.passes_through(pattern):
            return INVALIDATE("route reactivates known leakage")
```

Routes that pass through known structural leakage patterns are invalidated. Examples:

- a relationship-repair route that requires unilateral repair labor (already a known leakage)
- a financial-recovery route that requires more help from the depleted base reserve (already the source of the original damage)
- a work-recovery route that requires sustained overload on an already collapsed body margin

The Leakage Screen is what prevents the framework from recommending routes that would re-cause the original damage.

### 3. Anti-Collapse Guard

```text
AntiCollapseGuard(claim):
    if claim.collapses_into({advice, coaching, motivation,
                              productivity, financial_advice,
                              moralization}):
        return REJECT
```

The Adjustment Layer must not collapse into ordinary advice, coaching, productivity guidance, motivational psychology, financial advice, or moralization. The Anti-Collapse Guard rejects outputs that have done so.

This is the most distinctive runtime check in the layer. The collapse failure mode is the most common — LLMs in particular are strongly trained toward advice-shaped outputs and will produce them unless explicitly gated.

Concrete examples of guarded collapses:

- "communicate more" / "set boundaries" (relational collapse)
- "make a budget and stick to it" (financial collapse)
- "just take a walk and you'll feel better" (health collapse)
- "be more productive" (work collapse)
- "you should have known better" (moralizing collapse)

These are not banned because they are wrong. They are banned because they bypass the layer's actual function (route reweighting under constraints) and substitute a category that does not respect the constraints.

---

## Looking-Glass Chain

The Adjustment Layer can run standalone, but it is most useful when chained with the Looking-Glass / Adjoint Layer:

```text
Looking-Glass diagnoses:   observed outcome -> upstream bridge -> split point
Adjustment Layer routes:   current pressured state -> admissible future trajectory
```

The chain is sequential, not interchangeable. The two layers must not be collapsed into a single layer because their inputs and outputs are different kinds of objects.

When the chain is active, the Adjustment Layer takes the upstream bridge as part of its input and routes from the **depleted source state**, not from the visible symptom. This is what produces non-banal recommendations: the layer addresses the cause of the depletion, not the symptom of it.

For the Looking-Glass extension see [`../04_extensions/looking_glass.md`](../04_extensions/looking_glass.md).

---

## What the Layer Does Not Do

The Adjustment Layer must not be used to claim:

- desired outcomes are guaranteed by correct formulation
- financial advice is equivalent to structural routing
- impossible route jumps are admissible
- delivery is promised if the path distribution is reweighted
- the layer replaces cause-first repair (use Latent Cause Reconstruction instead)

These boundaries are enforced by the Anti-Collapse Guard at runtime and by the validation suite at design time.

---

## Compression

```text
Adjustment is not advice.

It is:
pressured state observed
-> anchors and deficits read
-> route field reweighted under budget and leakage constraints
-> admissible future paths selected.

A path is not admissible because it is desired.
It is admissible because it is reachable within constraints.
```

---

## Where to Read Next

- [`../04_extensions/looking_glass.md`](../04_extensions/looking_glass.md) — the upstream-diagnosis half of the chain
- [`../04_extensions/latent_cause_reconstruction.md`](../04_extensions/latent_cause_reconstruction.md) — how latent causes are reconstructed when not given
- [`../03_validation/adjustment_layer.md`](../03_validation/adjustment_layer.md) — three-model validation results
