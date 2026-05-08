# Observer Budget

The observer budget is the resource ceiling against which all transition costs are checked. This document defines it, gives the operating formula, and explains the three operating modes the framework recognizes.

---

## Definition

> **Observer Usable Budget** is the total cognitive, emotional, bodily, social, material, and temporal resources available to the observer in the current cycle, expressed as a fraction of nominal operating capacity.

The budget is not a fixed number. It varies by:

- time of day, week, season
- recent events (a fight, a deadline, a positive surprise)
- ongoing load (chronic stress, illness, large project running in background)
- observer-state factors (sleep debt, hunger, hydration, mood)

The budget can be estimated by the observer, by an analyst, or by a system that has access to enough telemetry signals to triangulate it. CAP does not require any one method — it requires that a budget estimate exists and is used.

---

## The Operating Formula

```text
TotalRisk(active operators in cycle) <= AllowedTotalRisk

AllowedTotalRisk = ObserverUsableBudget × RiskToleranceFactor
```

Where:

- **TotalRisk** = sum of `RiskWeight × P(failure)` across all operators in the cycle
- **ObserverUsableBudget** = current usable fraction of nominal capacity
- **RiskToleranceFactor** = a 0–1 multiplier representing how much of the available budget the observer is willing to commit (default ~0.7–0.9 depending on mode)

If TotalRisk exceeds AllowedTotalRisk, the framework must:

1. **Defer** the highest-risk operator to the next cycle, OR
2. **Downgrade** to a lower-risk operator that achieves partial progress, OR
3. **Pause** all pending operators and log the reason

It must not override the budget to apply a preferred operator. This is a hard constraint, not a guideline.

---

## Budget States

| Budget Level | Usable Budget | Permitted Risk Zone | Notes |
|---|---|---|---|
| **Full** | 100% | Nominal to Expansion | Operator selection is least constrained. |
| **Partial** | 60–80% | Conservation to Nominal | Expansion-zone operators require explicit justification. |
| **Depleted** | 30–50% | Conservation only | Only stabilizers and small boundaries. No new high-cost commitments. |
| **Critical** | <30% | Pause/Hold only | Budget Recovery Protocol activates. No active operators except continuing existing Active states. |

The boundary between these is a calibration point, not a discovered constant. Different observers and different domains may set the bands differently. What matters is that a band exists and is enforced.

---

## Three Operating Modes

CAP recognizes three operating modes that combine budget state with operator-selection policy:

### Conservative Mode

```text
Budget: any
RiskToleranceFactor: 0.5–0.7
Preferred operators: Conservation zone (10–30%)
Default response to ambiguity: Pause, gather more telemetry
```

Use when: stakes are high, telemetry is Loaded, recent operators have failed, or the observer is recovering from a prior cycle's depletion.

### Nominal Mode

```text
Budget: Partial or Full
RiskToleranceFactor: 0.7–0.85
Preferred operators: Nominal zone (40–60%)
Default response to ambiguity: select the operator that addresses the SplitPoint, not the symptom
```

Use when: telemetry is Clean or Loaded, budget is Partial or Full, the situation is legible, no recent failures.

### Expansion Mode

```text
Budget: Full
RiskToleranceFactor: 0.85–0.95
Preferred operators: any zone with budget to support
Default response to ambiguity: select the operator that produces the largest route change
```

Use when: Clean telemetry, Full budget, confirmed progress on prior cycles, and a clear strategic reason to take a route-changing risk.

Most CAP analyses operate in Nominal or Conservative mode. Expansion mode is the exception, not the default.

---

## Budget Discipline as Epistemological Principle

Budget discipline is not just a safety check — it is a **claim about what counts as a valid recommendation**.

> A recommendation that exceeds observer budget is structurally false for that observer at that time.

This claim is structural, not soft:

- It is not "the recommendation might be hard to follow." It is "the recommendation is not a recommendation in this framework."
- It is not "we should consider feasibility." It is "feasibility is a constituent of validity."
- It is not "be realistic." It is "an operator without a budget check is not in the operator alphabet."

This is what separates CAP from advice. Advice can be philosophically correct and operationally inadmissible. A CAP recommendation cannot.

---

## Cross-Cycle Carry

An operator that was deferred (HOLD) in cycle N becomes the first operator considered in cycle N+1, after a budget reassessment. The HOLD does not silently disappear; it is queued, logged, and the queue is checked at the start of every cycle.

This prevents a common failure mode: deferring an operator because budget is depleted, then forgetting the operator entirely, leaving the underlying node still Leaking.

---

## Budget Recovery Protocol

When budget falls to Depleted or Critical, the Budget Recovery Protocol activates:

1. **Inventory** all currently Active nodes and their operator states.
2. **Triage** Active nodes as: (a) must continue (Leaking at L3/L4 — Fixation required), (b) can pause (L1/L2 Leaking or no immediate deadline), (c) can drop (optional or duplicated nodes).
3. **Reduce** by applying Pause to (b) and Dropped status to (c).
4. **Stabilize**: verify TotalRisk is within Depleted budget constraints; continue pausing nodes until it is.
5. **Recovery condition**: identify what signal would restore budget to Partial or Full; log this as a Pending node ("Budget recovery: pending [condition]").
6. **Resume**: when the recovery condition is met, reopen Paused nodes in priority order (highest leak level first).

This protocol is what prevents a depleted observer from making a depletion-driven decision and then crashing further.

---

## What the Budget Does Not Measure

The budget does not measure:

- the *importance* of the situation (importance does not increase budget)
- the *moral weight* of the choice (moral weight does not increase budget)
- the *desire* for an outcome (desire does not increase budget)

A high-stakes, morally weighty, deeply desired outcome with insufficient budget is still budget-blocked. The framework does not rebalance the budget in response to narrative pressure. This is the core anti-drama discipline.

---

## Where to Read Next

- [`transition_cost.md`](./transition_cost.md) — what the budget is checked against
- [`telemetry_gating.md`](./telemetry_gating.md) — how telemetry caps the maximum permitted risk independent of budget
- [`operator_admissibility.md`](./operator_admissibility.md) — the derived concept that combines budget + telemetry
