# Path Reweighting / Adjustment Layer Holdout Case Pack

Date: 2026-05-02

Status: fresh synthetic holdout / stress pack.

Purpose: test whether the Path Reweighting / Adjustment Layer remains usable
outside the original eight-case pack without turning the validator into a
ground-truth copying exercise.

## Cases

| Case | Target Verdict | Target Reading | Stress Point |
|---|---|---|---|
| `pal_h01_partial_budget_reroutes_not_blocks` | `supportive` | `budget_gate_blocks_expensive_route` | partial budget should enable cheaper route, not total block |
| `pal_h02_relationship_unilateral_repair_leakage` | `supportive` | `leakage_screen_invalidates_leaking_route` | relationship leakage pattern must be caught, not routed through |
| `pal_h03_coaching_disguised_as_recovery_routing` | `reject` | `advice_collapse_blocked` | motivational coaching disguised as recovery routing must be rejected |
| `pal_h04_impossible_single_step_jump` | `reject` | `advice_collapse_blocked` | impossible single-step jump must be blocked even when framed as bridge construction |
| `pal_h05_schrodinger_preserves_prior_dynamics` | `supportive` | `schrodinger_bridge_minimal_deformation_valid` | complete replacement request must be downgraded to minimal deformation |
| `pal_h06_health_recovery_looking_glass_chain` | `supportive` | `looking_glass_chain_upstream_informs_adjustment` | health domain upstream bridge must inform routing, not symptom alone |
| `pal_h07_work_desire_pressure_budget_gate` | `supportive` | `budget_gate_blocks_expensive_route` | budget gate must apply even under desire pressure mode |
| `pal_h08_problem_pressure_recovery_not_self_improvement` | `supportive` | `problem_pressure_recovery_route_allowed` | self-model damage must route to stabilization, not self-improvement |
| `pal_h09_symptom_closure_ignores_active_leakage` | `supportive` | `leakage_screen_invalidates_leaking_route` | symptom closure without leakage repair is structurally incomplete |

## Reading Boundary

This pack may support:

```text
budget-aware rerouting (partial and exhausted budget cases)
leakage-aware routing (relationship and financial domains)
anti-collapse guard (reject motivational coaching and impossible jumps)
Schrodinger bridge minimal deformation enforcement
Looking-Glass chain upstream-informed routing (health domain)
problem-pressure recovery toward stabilization
desire-pressure budget gating
```

It may not support:

```text
motivational coaching or encouragement as structural routing
impossible single-step state jumps (framed as bridge construction or otherwise)
complete replacement of prior path dynamics
symptom-only routing that ignores active leakage
self-improvement advice substituted for recovery routing
advice collapse into generic financial or productivity checklists
```

## Non-Banality Boundary

The layer is not a symptom-closure machine.

For cases like:

```text
incident response shock -> visible budget overrun -> proposed invoice-only fix
```

the system must not simply close the visible symptom. If leakage is active
(continued optional spend from the contingency buffer), closing the invoice
while the leakage continues is not stable repair.

The non-banal output is:

```text
visible symptom = budget overrun after incident response shock
proposed route = invoice-only fix
leakage detected = continued optional spend from the contingency buffer
leakage status = active
symptom closure blocked = yes (leakage still running)
required route = leakage-first, then symptom closure
anti_collapse_guard = symptom_closure_not_stable_while_leakage_active
```

This is the key non-banality boundary for this holdout pack (case `pal_h09`).

The same structural principle carries across domains:

- relationship: closing the conflict while unilateral repair labor continues
  is not stable repair — the leakage pattern must be addressed first
- health: treating fatigue symptoms while chronic overload continues will not
  produce stable recovery — the overload pattern is the upstream that must
  be routed from
- self-model: applying productivity advice to a shame spiral while identity
  rupture is active does not stabilize — bounded recovery routing is required first

## Domain-General Carryover

The holdout pack covers four domains:

**Relationships** (pal_h02): unilateral repair labor is a leakage pattern.
Apology-plus-gift routes that do not restore mutuality are structurally leaking.
The system must invalidate the leaking route and route toward mutuality restoration.

**Health** (pal_h06): visible symptoms (chronic fatigue) are not sufficient
routing anchors if an upstream bridge (repeated overload pattern) is identified.
Looking-Glass chain informs the adjustment layer to route from the overload-depleted
origin state, not just from the symptom.

**Work / desire pressure** (pal_h07): desire-pressure inputs (starting a new
creative project) do not bypass budget gating. Budget exhaustion from existing
overload applies regardless of desire-pressure mode. The system proposes a
phased lower-cost start as the admissible alternative.

**Self-model** (pal_h08): self-model damage (shame spiral, identity rupture)
routes to bounded stabilization under problem-pressure recovery. Self-improvement
coaching or productivity advice is a collapse and must be blocked.

The anti-collapse guard applies to all four domains:

```text
motivational coaching -> blocked (pal_h03)
impossible bridge jump -> blocked (pal_h04)
symptom closure without leakage repair -> blocked (pal_h09)
```

The budget gate applies even when desire-pressure is active (pal_h07), and
partial budget enables cheaper rerouting rather than total blocking (pal_h01).
