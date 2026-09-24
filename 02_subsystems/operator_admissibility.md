# Operator Admissibility

Operator admissibility is the **derived concept** that combines observer budget and telemetry state to determine, for any given operator, whether the framework is permitted to recommend it right now.

Admissibility is the runtime gate. Every operator recommendation passes through it before being emitted.

---

## Definition

> An operator is **admissible** for the current observer in the current cycle if and only if all of the following hold:
>
> 1. Its RiskWeight does not exceed the maximum permitted by the current TelemetryState
> 2. Adding it to TotalRisk does not exceed AllowedTotalRisk (= ObserverUsableBudget × RiskToleranceFactor)
> 3. Its preconditions are satisfied (e.g., Boundary requires a definable scope; Closure requires a deliverable)
> 4. It is causally aligned with the LikelySplitPoint, not just the visible symptom
> 5. Its reversibility profile is appropriate to the current TelemetryState (irreversible operators are restricted under Loaded or Overheating)

If any of these fail, the operator is inadmissible. The framework then either downgrades to a lower-risk substitute or holds (Pause).

---

## The Admissibility Rule

Combining the rules above into a single decision procedure:

```text
function is_admissible(operator, node, observer, cycle):
    if RiskWeight(operator) > max_permitted_risk(observer.TelemetryState):
        return False                                # blocked by risk throttle

    if cycle.TotalRisk + RiskWeight(operator) > observer.AllowedTotalRisk:
        return False                                # blocked by budget gate

    if not preconditions_satisfied(operator, node):
        return False                                # blocked by precondition

    if not addresses_split_point(operator, node):
        return Conditional                          # may proceed if no causal alternative

    if irreversible(operator) and observer.TelemetryState in {Loaded, Overheating}:
        return Conditional                          # require explicit override justification

    return True
```

The framework prefers to **downgrade rather than block**. If a high-risk operator is inadmissible, the framework looks for a lower-risk operator that achieves partial progress toward the same target status. Only if no such operator exists does it fall back to Pause.

---

## Worked Example

**Setup**:
- Node: Project payment node, in Looping state (3 unpaid revisions)
- Observer: Partial budget (~70%), TelemetryState = Loaded
- Recommended operator: Inversion (reverse course on the project, take legal action) — RiskWeight 80%

**Admissibility check**:

| Check | Result |
|---|---|
| RiskWeight (80%) > max permitted at Loaded (60%) | Blocked |
| Inversion would push cycle TotalRisk over AllowedTotalRisk | Blocked |
| Preconditions for legal action (signed contract) | Possibly satisfied |
| Addresses SplitPoint (lack of boundary at first free revision) | No — symptom-level |
| Irreversibility under Loaded telemetry | Requires override |

**Verdict**: Inversion at 80% is **inadmissible**. Multiple gates fire.

**Downgrade sequence**:

1. **Try Boundary at ~35% risk**: defines scope in writing, halts further work pending acceptance. Admissible.
2. **Sequence with Fixation at ~25% risk**: stops all project work until Boundary is accepted or Break is applied. Admissible.
3. **Conditional Break (~50% risk) on the next cycle** if Boundary is rejected by client. Deferred.

Total admissible cycle: Fixation → Boundary, ~60% combined risk, within Partial-budget Loaded-telemetry envelope.

---

## The Downgrade Sequence

When the recommended operator is inadmissible, CAP follows a standard downgrade sequence:

```text
1. Reduce risk: find a lower-RiskWeight operator that achieves partial progress.
2. Split: decompose one high-risk operator into a sequence of lower-risk operators across cycles.
3. Defer: if no admissible operator exists this cycle, queue the operator for the next cycle and apply Pause.
4. Stabilize: if the node is Leaking and no admissible operator exists, apply Fixation to halt the leak.
5. Recover: if budget is Critical and telemetry is Breach, enter Budget Recovery Protocol.
```

Each step is preferred over the next. The framework does not jump directly to Pause if a downgrade or split is available.

---

## Causal Alignment Check

Item 4 in the admissibility rule — **causal alignment with the LikelySplitPoint** — is the check that distinguishes CAP from symptom-treatment frameworks.

An operator that addresses only the visible symptom is not strictly inadmissible — sometimes a symptom-level operator is the only available move. But the framework flags it explicitly:

```text
RecommendedOperator: Boundary (symptom-level — does not address SplitPoint)
Notes: Addresses current visible leak but does not repair upstream cause.
       Underlying SplitPoint (Revision 1 delivery without scope) remains.
       Re-Looping likely if SplitPoint not addressed in subsequent cycle.
```

This is the framework's honesty about the limit of the current operator. It can produce immediate progress without claiming to have solved the underlying configuration.

---

## Why Admissibility Is a Hard Gate

A common alternative to hard admissibility gating is "soft" gating: the framework warns about admissibility violations but lets them through if the user insists. CAP rejects this design.

Reasons:

1. **Compounding error**: a single admissibility override creates pressure for the next override. The framework's discipline degrades cycle by cycle.
2. **No structural validity claim**: if the framework can be talked into recommending inadmissible operators, the strong claim ("a recommendation that exceeds budget is structurally false") collapses into a soft preference.
3. **Failure attribution**: when an inadmissible operator fails, the framework is responsible for not having blocked it. Hard gating makes the responsibility chain clean.

The cost is occasional friction — situations where the observer wants the framework to recommend a high-risk operator and the framework refuses. The benefit is that what the framework does recommend can be trusted as admissible.

---

## Admissibility and the Observer's Choice

Admissibility is a property of recommendations, not of choices. The observer is always free to apply an inadmissible operator. The framework's role is to refuse to *recommend* it.

This distinction matters. CAP does not control the observer; it controls itself. The observer can override anything. But when they do, they do so without the framework's recommendation, which is the correct attribution of agency.

---

## Numeric Contract

The numeric part of the admissibility rule (items 1 and 2 above) is encoded in
[`../reference/python/cap/budget_calculus.py`](../reference/python/cap/budget_calculus.py)
as `operator_admissibility(operator, risk_weight, active_operator_risks,
allowed_total_risk, telemetry_state)`, exercised by
[`../reference/python/tests/test_budget_calculus.py`](../reference/python/tests/test_budget_calculus.py):

- any missing input (`None`) returns `not_computed`; a missing input never
  produces a positive result, and invalid present inputs raise `ValueError`;
- at `breach` there is no numeric ceiling: an operator outside the
  `Recovery-Only` gate of `spec/operator_alphabet.json` (Fixation, Hold,
  Cleanup) returns `blocked_recovery_only` whatever its weight, and a
  Recovery-Only operator must still fit the budget with the active operators;
- otherwise the telemetry ceiling (`max_permitted_risk`, from
  [`telemetry_gating.md`](./telemetry_gating.md)) is checked first and returns
  `blocked_by_telemetry`;
- then `total_risk(active + [candidate]) > allowed_total_risk` returns
  `blocked_by_budget`; equality admits, as in `is_cycle_admissible`;
- otherwise the operator is `admissible` on the numeric checks. A numeric
  `admissible` is not full admissibility: items 3–5 remain unchecked by code.
- Items 3–5 (preconditions, causal alignment with the LikelySplitPoint,
  reversibility under the current telemetry) are **not** encoded: they need
  inputs that no current artifact supplies, so they remain the analyst's or
  the model's reading and are not claimed as machine-checked.
- The worked example above is one of the test cases: at Loaded telemetry with
  AllowedTotalRisk 60, Inversion 80 is `blocked_by_telemetry`, Fixation 25 and
  then Boundary 35 are `admissible`, and a further 50 is `blocked_by_budget`.
  The COM Grammar case `cgm_03` (Overheating, AllowedTotalRisk 30: Inversion 80
  blocked, Hold 10 then Fixation 20 admissible) and the Breach case `cgm_07`
  (Recovery-Only: Fixation 20, Hold 10, Cleanup 15 admissible within the
  budget; any other operator `blocked_recovery_only`) are the others; the
  case numbers are example values.

## Where to Read Next

- [`com_grammar.md`](./com_grammar.md) — the full operator alphabet that admissibility operates on
- [`adjustment_dynamics.md`](./adjustment_dynamics.md) — the forward routing engine that uses admissibility to reweight paths
- [`../examples/worked_case_client_free_edits.md`](../examples/worked_case_client_free_edits.md) — a complete admissibility check in context
