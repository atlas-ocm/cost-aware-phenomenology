# Telemetry Gating

Telemetry is the second hard constraint in CAP, alongside observer budget. Where budget asks *can the observer afford this operator*, telemetry asks *do we have enough signal to recommend it at all*. This document defines telemetry, lists the four gate states, and explains how telemetry interacts with risk throttling.

---

## Why Telemetry

The framework cannot allow itself to believe its plan more than the channel state supports. If the observable signals do not confirm a state, the framework cannot proceed as if that state is confirmed.

Without a telemetry gate, a CAP analysis can drift in two failure modes:

1. **Hallucinated states**: assigning a state to a node based on narrative inference rather than observable signal.
2. **Hallucinated outcomes**: predicting that an operator will succeed without checking whether the surrounding signal supports execution.

Both produce CAP-shaped output that has no operational ground. The telemetry gate exists specifically to prevent this.

> **Gate on signal, not intention.** Telemetry state determines what outputs are permitted, not what the analyst wants to recommend.

---

## Telemetry Signals (examples)

Telemetry signals are observable signals in the actual world that confirm or deny the state assigned to a node. Examples:

**Material signals**
- Completed deliverables (yes / no, on time / late)
- Received payments (amount, date, source)
- Money flow direction over a window

**Communication signals**
- Returned messages (response time, content, tone)
- Pattern of contact (frequency, initiation direction)
- Contract terms (written, verbal, implied)

**Behavioral signals**
- Frequency and consistency of behaviors
- Repeated patterns across cycles
- Drop-out, pull-back, escalation patterns

**Bodily signals**
- Energy level, sleep quality, somatic markers (headache, tension, gut)
- Physical capacity (can the observer perform the operator with the body they have right now)
- Recovery patterns after prior cycles

**Cognitive signals**
- Retrieval pressure (is it expensive to think about this domain right now)
- Attention bandwidth available
- Working memory load

**Affective signals**
- Flashback frequency
- Emotional flooding events
- Recovery time after emotional triggers

A node's state assignment must be backed by at least one telemetry signal. If no signal can be identified, the state assignment is **hypothetical** and must be marked as such.

---

## The Four Gate States

| State | Description | Permitted Outputs |
|---|---|---|
| **Clean** | All required signals present and consistent. No contradictions between signals. | Full COM-Log including operator recommendations and route forecast. |
| **Loaded** | Most signals present; minor gaps or contradictions. Situation is legible but not fully confirmed. | COM-Log with operator recommendations; route forecast marked as provisional. |
| **Overheating** | Significant signal gaps or contradictions. Multiple plausible interpretations. Observer budget partially depleted. | COM-Log with state assignments only; operator recommendations gated until signal improves; no route forecast. |
| **Breach** | Critical signal failure. Key information unavailable or actively contradicted. Observer budget at Critical. | Pause on all active operators; Fixation on all Leaking nodes; no new operator recommendations; ReverseTrace required. |

The gate state is determined by the joint condition of signal quality and observer budget. A situation can be Loaded because of signal contradictions even if budget is Full; a situation can be Overheating because of budget depletion even if signal quality is high.

---

## Risk Throttling

Risk throttling is the **automatic reduction of operator risk ceiling** as telemetry degrades.

| TelemetryState | Maximum Permitted RiskWeight |
|---|---|
| Clean | 90% |
| Loaded | 60% |
| Overheating | 30% |
| Breach | 0% (Pause only) |

When the system selects an operator and that operator's RiskWeight exceeds the permitted ceiling for the current TelemetryState, the system must:

1. **Select a lower-risk operator** that achieves partial progress toward the target status.
2. If no lower-risk operator is available, **apply Pause** and log the reason.
3. **Never override the telemetry ceiling** to apply a preferred operator. This is a hard constraint, not a suggestion.

This auto-downgrade is the most distinctive runtime behavior of CAP: it is the moment when the framework refuses to give the observer what they ask for and instead gives them what they can safely execute.

---

## Telemetry-First Realism

No analytical output is valid without a telemetry ground. Telemetry-first realism prohibits:

- Assigning states that have no observable correlate
- Recommending operators that cannot be executed in the current telemetry state
- Producing CAP analyses that describe a situation without grounding signals

If no telemetry signal exists for a proposed state, the state cannot be assigned. It can be proposed as a hypothesis, marked Pending, and gated on future signal arrival.

This is a strong constraint. It rules out a large class of plausible-sounding analyses that are not actually grounded. The cost is occasional inability to produce a confident recommendation; the benefit is that confident recommendations, when they exist, are backed by signal.

---

## Budget Recovery Protocol

When TelemetryState reaches Breach (often co-occurring with Critical budget), the Budget Recovery Protocol activates. See [`observer_budget.md`](./observer_budget.md) for the full six-step protocol. Summary:

1. Inventory all Active nodes
2. Triage as continue / pause / drop
3. Apply Pause to pause-eligible, Dropped to drop-eligible
4. Stabilize
5. Define recovery condition as a Pending node
6. Resume in priority order when condition is met

Critically: in Breach state, the framework permits **only stabilizers** (Pause, Fixation). It does not produce route forecasts and does not recommend new operators until telemetry recovers. The validation runs (see [`../03_validation/com_grammar.md`](../03_validation/com_grammar.md)) confirm that all three tested LLMs respect this constraint when given Breach-state inputs.

---

## Antifragility Rule

An operator sequence is **antifragile** if it produces a better-than-expected outcome when a Guard condition is violated — i.e., the route becomes more robust when stressed.

CAP prefers antifragile operator sequences:

- **Граница (Boundary) before Разрыв (Break)**: If Boundary fails, the route proceeds to Break — which was always an option. Boundary failure does not make Break harder. The sequence is antifragile.
- **Фиксация (Fixation) before Усиление (Pump)**: Stabilizing a leak before amplifying ensures amplification does not accelerate the leak. Fixation failure prevents wasted Pump resource.
- **Пауза (Pause) before irreversible operators**: A Pause before Break or Closure never makes the irreversible option less available. It may make it unnecessary.

The non-antifragile error: applying Break before Boundary. If Break was unnecessary (Boundary would have resolved it), the route incurs unnecessary damage. If Break was necessary, it would still have been available after Boundary — nothing was gained by skipping Boundary.

Telemetry gating supports antifragility by automatically routing toward reversible, lower-risk options when signal is weak.

---

## What Telemetry Does Not Do

Telemetry does not:

- replace the observer's judgment (it gates the framework's outputs, not the observer's choices)
- guarantee the operator will succeed (it just confirms the operator is admissible to recommend)
- measure the moral or strategic weight of the situation (it measures signal quality and observer state)

A high-stakes situation with bad telemetry is still bad telemetry. The framework will not upgrade the gate state because the situation matters. This is the same anti-drama discipline as in [`observer_budget.md`](./observer_budget.md).

---

## Where to Read Next

- [`operator_admissibility.md`](./operator_admissibility.md) — how budget and telemetry combine to determine which operators can fire
- [`com_grammar.md`](./com_grammar.md) — the full operator grammar
- [`../03_validation/com_grammar.md`](../03_validation/com_grammar.md) — validation results showing telemetry gating works across models
