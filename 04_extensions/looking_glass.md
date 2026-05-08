# Looking-Glass / Adjoint Layer

The Looking-Glass Layer (also: Adjoint Layer) is a **diagnostic extension** of CAP. It is not part of the core operator grammar — it is a research-only routing mode for reverse-causal reading and repair planning.

Status: `research-only / two-model identity-verified / holdout clean`.

---

## Purpose

The Looking-Glass Layer is useful when the framework has observed an outcome first and needs to ask:

```text
What prior paths could have produced this?
Where was the split point?
What can still be restored?
What can only be compensated?
What is the minimal repair path?
```

It is the **reverse diagnostic** half of the diagnostic-routing chain. Its forward counterpart is the Adjustment Layer (see [`../02_subsystems/adjustment_dynamics.md`](../02_subsystems/adjustment_dynamics.md)).

---

## Core Boundary

**Not this:**

```text
effect -> cause in physical reality
```

**This:**

```text
observed outcome
-> plausible prior paths
-> split point / critical transition
-> restore-or-compensate decision
-> minimal repair path
```

The layer is a **retrodiction and repair-planning mode**. It does not claim that history can be deleted, that an effect becomes physically earlier than its cause, or that the past can be made non-existent.

---

## The Anti-Magic Guard

The most distinctive runtime check in the layer is the **Anti-Magic Guard**:

```text
AntiMagicGuard(claim):
    if claim implies any of:
        - past events can be made non-events
        - macro consequences can be undone without cost
        - entropy can be reversed for free
        - L5 (physical law) can be bypassed by narrative wording
        - retrodiction is independent proof of the true prior path:
    then REJECT
```

The Looking-Glass layer is not an undo mechanism. It is a planning tool that takes the present as given and asks what the most likely path from present back through history was, and what still admits repair.

---

## Restore vs Compensate

The key practical distinction the layer produces:

```text
restore     = return the same functional channel
compensate  = build a new support path because the old state is unavailable
```

A Looking-Glass analysis is strongest when it says plainly which one is still possible. Examples:

- A relationship breach where mutual repair is still possible: **restore**
- A relationship breach where mutuality has structurally collapsed: **compensate** (build new mutuality with someone else, or design closure)
- A health setback where recovery margin can be rebuilt: **restore**
- A health setback where the body has lost a function permanently: **compensate** (build a new functional path around the lost function)
- A financial loss recoverable through additional income: **restore**
- A financial loss exceeding any plausible income trajectory: **compensate** (accept loss, redesign the floor, use formal restructuring if applicable)

The framework's honesty is in the distinction. A pretend-restore plan is worse than an honest compensate plan because the pretend-restore consumes budget without producing the restored state.

---

## The Operators

### `Retrodict(outcome, horizon)`
Reconstructs plausible prior trajectories from the observed result. Output remains probabilistic unless backed by independent evidence.

### `TraceSplit(outcome)`
Searches for the critical branch point or local transition that made the outcome likely.

### `UnwindCost(target_state)`
Estimates the cost of moving from current state back into a target-compatible state.

### `RepairPlan(target_state, constraints)`
Proposes the smallest intervention path still compatible with observed constraints.

### `RestoreOrCompensate(outcome)`
Separates what can still be restored from what can only be compensated.

### `AntiMagicGuard(claim)`
Rejects claims that the patch erases history or bypasses physics by narrative.

---

## Non-Banality Rule

The layer must identify the **earlier bridge** that made a later shock damaging. A banal reading would identify the visible trigger as the cause; a non-banal reading identifies the upstream margin failure that made the trigger consequential.

Example:

```text
Banal reading:
emergency database recovery invoice -> budget overrun
(Implication: negotiate the invoice / find a cheaper vendor)

Non-banal reading:
prior non-critical prototype spend -> contingency-buffer depletion
                                   -> visible emergency invoice -> budget overrun
(Implication: stop optional buffer leakage BEFORE treating the invoice as isolated)
```

The non-banal reading is what allows the chained Adjustment Layer to route from the depleted source rather than from the visible symptom. Without the non-banality rule, the chain produces ordinary advice; with it, the chain produces structural repair.

---

## Relation to Adjustment Layer

```text
Looking-Glass diagnoses:
observed outcome -> plausible prior paths -> upstream bridge -> split point

Adjustment Layer routes:
current pressured state -> admissible future trajectory distribution
```

The chain:

```text
Looking-Glass produces the upstream bridge.
Adjustment Layer reweights forward paths from the depleted source state
identified by the upstream bridge.
```

The two layers are sequential and must not be collapsed. They handle different kinds of objects (retrodicted prior paths vs. forward route distributions) and have different runtime guards (Anti-Magic Guard vs. Anti-Collapse Guard).

---

## Validation Status

```text
Deterministic baseline:                clean 8/8
Fresh holdout deterministic:           clean 9/9

comet main hardened:        verdict 8/8, primary 8/8
silicon main hardened:      verdict 8/8, primary 7/8
opencrystal main hardened:  verdict 4/8, primary 4/8 (excluded as positive support)

comet fresh holdout:    verdict 9/9, primary 9/9
silicon fresh holdout:  verdict 9/9, primary 9/9
```

OpenCrystal is not used as positive support because its main identity-verified run overused the underdetermined-retrodiction bucket. The third model is not required for bounded research-only helper use when deterministic baseline, fresh holdout, and two identity-verified LLM surfaces are clean.

For the threshold rationale see `Patch/research_only_model_surface_threshold_note.md`.

---

## Permitted Use

```text
observed outcome    -> plausible prior paths
visible trigger     -> upstream enabling bridge
split-point candidate detection
restore-vs-compensate routing
repair-cost accounting
future-anchor compatibility checks
moving-baseline maintenance cost
```

## Not Permitted as Proof

```text
literal undo-history
free entropy reversal
exact-past proof from downstream outcome alone
generic financial advice
post-hoc common sense checklist
downstream advice replacing upstream diagnosis
canon promotion evidence
model-independent stability claim
```

---

## Authoritative Artifacts

```text
RESEARCH_PATCH_ADJOINT_LOOKING_GLASS_LAYER.md
Patch/adjoint_looking_glass_layer_case_pack.md           (8 cases)
Patch/adjoint_looking_glass_layer_holdout_case_pack.md   (9 cases)
Patch/adjoint_looking_glass_layer_final_status_note.md
Patch/adjoint_looking_glass_layer_identity_boundary_note.md
Patch/adjoint_looking_glass_layer_upstream_causality_boundary_note.md
```

---

## Compression

```text
Looking-Glass is not history undo.

It is:
outcome observed
-> causes reconstructed
-> split point located
-> repair cost counted
-> restore or compensate.
```
