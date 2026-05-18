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

## Position in OCM

Looking-Glass sits between Mirror Layer and Adjustment Layer:

```text
Mirror Layer
  -> Observed State B
  -> Looking-Glass
  -> retro-diagnostic trace
       (plausible prior paths, split point, damaged invariants,
        repair mode, minimal repair path)
  -> Adjustment Layer
  -> admissible next routes to C
  -> Verifier
  -> Release Gate
```

The layer divides the Adjustment formula `B -> infer A -> plan C` at the
arrow: Looking-Glass produces the left half (`B -> infer A` with a split
point and damaged invariants), Adjustment produces the right half
(`A + B -> admissible C`). Without Looking-Glass, Adjustment can start
from a fabricated cause and arrive at a confidently wrong route.

Looking-Glass is read-only. It does not mutate, does not release, does
not canonicalize.

## Runtime Trace Contract

The runtime output of a Looking-Glass analysis is a `LookingGlassTrace`.
The contract lives at
[`../spec/looking_glass_trace.schema.json`](../spec/looking_glass_trace.schema.json),
exercised by
[`../reference/python/tests/test_looking_glass_trace_schema.py`](../reference/python/tests/test_looking_glass_trace_schema.py).

The trace carries:

- `input_mirror_frame_id` — reference to the Mirror Frame that fixed `B`;
- `observed_outcome` with a typed `kind` (test_failure, runtime_crash,
  ui_state_mismatch, memory_conflict, config_drift,
  context_contamination, route_failure, agent_loop, release_block,
  semantic_mismatch);
- `plausible_prior_paths[]` — each with a `path` kind (direct_cause,
  state_drift, stale_context, wrong_boundary, misrouted_operator,
  anchor_conflict, role_permission_mismatch, budget_exhaustion,
  external_dependency, unknown), probability band, and confidence;
- `likely_split_point` — described by a `location` enum (code_path,
  config_overlay, memory_merge, prompt_boundary, tool_result,
  agent_role_switch, runtime_state, browser_state, git_state,
  semantic_anchor);
- `damaged_invariants[]` — each typed by class (identity, boundary,
  causal, temporal, permission, config, memory, release, budget,
  semantic) and damage kind (violated, weakened, stale, contradicted,
  unproven, unknown);
- `recommended_repair_mode` from a closed enum: restore, compensate,
  reconcile, retcon, rollback, tolerate_scar, hold,
  escalate_to_human;
- `minimal_repair_path` — bounded sequence of steps, each labelled
  read_only / candidate_patch / requires_authorization, with a cost
  estimate;
- `uncertainty[]` and `blocked_assumptions[]` — explicitly preserved;
- `verdict` from a closed enum: split_point_detected, restore_path_found,
  compensate_required, reconcile_required, rollback_recommended,
  tolerate_scar, insufficient_trace, multiple_competing_paths,
  boundary_obscured.

Hard invariants enforced by the schema:

- LG-01: `input_mirror_frame_id` is required;
  `observed_outcome.evidence_refs` minItems:1;
  `policy.require_mirror_frame` is locked to `const true`.
- LG-02: `policy.allow_mutation` is locked to `const false`. The trace
  carries no `applied_diff` field.
- LG-03: `policy.allow_single_cause_without_evidence` is locked to
  `const false`.
- LG-04: `policy.preserve_competing_paths` is locked to `const true`.
  `verdict: multiple_competing_paths` requires
  `plausible_prior_paths` minItems:2.
- LG-05: a `likely_split_point` with `confidence > 0.7` requires
  `evidence_refs` minItems:1.
- LG-06: `minimal_repair_path.steps` minItems:1 (no unbounded rewrites).
- LG-09: `verdict: tolerate_scar` requires a `tolerated_scar_note`
  string explaining locality and non-cascade.
- LG-10: trace does not carry a release decision; downstream Release
  Gate handles release.
- LG-11: `uncertainty` and `blocked_assumptions` arrays are required
  (may be empty).
- Verdict / repair_mode consistency: `restore_path_found` requires
  `restore`; `compensate_required` requires `compensate`;
  `reconcile_required` requires `reconcile`; `rollback_recommended`
  requires `rollback`; `insufficient_trace` requires
  `hold | escalate_to_human`; `multiple_competing_paths` requires
  `hold`; `boundary_obscured` requires `hold` and
  `blocked_assumptions` minItems:1.

The companion case schema at
[`../spec/looking_glass.schema.json`](../spec/looking_glass.schema.json)
validates the test-input cases (`alg_*.json`) used to exercise the
layer. The trace schema validates the layer's runtime output. Both are
machine-checked in the check_repo smoke.

## Machine-Readable Contract

The corresponding case schema is
[`../spec/looking_glass.schema.json`](../spec/looking_glass.schema.json).
It locks the operator alphabet (`Retrodict`, `TraceSplit`, `UnwindCost`,
`RepairPlan`, `RestoreOrCompensate`, `AntiMagicGuard`, `UpstreamBridge`),
the case `ground_truth` enums (`verdict`, `final_reading`, `claim_status`),
and enforces the cross-field invariants from this document:

- `verdict: reject` requires a `*_rejected` `final_reading` and a `blocked_*`
  `claim_status`;
- `claim_status: blocked_*` requires `verdict: reject`;
- `verdict: supportive` requires a `allowed_*` `claim_status`;
- a `*_rejected` `final_reading` requires `AntiMagicGuard` in `operators`.

A worked example lives at
[`../examples/looking_glass_case_example.json`](../examples/looking_glass_case_example.json)
and is exercised by
[`../reference/python/tests/test_looking_glass_schema.py`](../reference/python/tests/test_looking_glass_schema.py),
which also validates every case in
`Patch/adjoint_looking_glass_layer_cases/` and
`Patch/adjoint_looking_glass_layer_holdout_cases/` against the schema.

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
