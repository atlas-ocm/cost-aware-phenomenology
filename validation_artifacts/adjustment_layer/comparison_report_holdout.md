# Adjustment Layer (Holdout) — LLM Model Comparison

## Scope

This report is generated from actual model_run files in this repository.

**Models verified:**
- `comet_12b_v.7-i1`
- `silicon-maid-7b-imatrix`
- `fimbulvetr-11b-v2`

## Per-Case Comparison

| Case | Expected | Comet | Silicon Maid | Fimbulvetr | Match |
|---|---|---|---|---|---|
| `pal_h01_partial_budget_reroutes_not_blocks` | `supportive / budget_gate_blocks_expensive_route` | `supportive / budget_gate_blocks_expensive_route` | `supportive / budget_gate_blocks_expensive_route` | `supportive / budget_gate_blocks_expensive_route` | 3/3 |
| `pal_h02_relationship_unilateral_repair_leakage` | `supportive / leakage_screen_invalidates_leaking_route` | `supportive / leakage_screen_invalidates_leaking_route` | `supportive / leakage_screen_invalidates_leaking_route` | `supportive / leakage_screen_invalidates_leaking_route` | 3/3 |
| `pal_h03_coaching_disguised_as_recovery_routing` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | 3/3 |
| `pal_h04_impossible_single_step_jump` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | 3/3 |
| `pal_h05_schrodinger_preserves_prior_dynamics` | `supportive / schrodinger_bridge_minimal_deformation_valid` | `supportive / schrodinger_bridge_minimal_deformation_valid` | `supportive / schrodinger_bridge_minimal_deformation_valid` | `supportive / schrodinger_bridge_minimal_deformation_valid` | 3/3 |
| `pal_h06_health_recovery_looking_glass_chain` | `supportive / looking_glass_chain_upstream_informs_adjustment` | `supportive / looking_glass_chain_upstream_informs_adjustment` | `supportive / looking_glass_chain_upstream_informs_adjustment` | `supportive / looking_glass_chain_upstream_informs_adjustment` | 3/3 |
| `pal_h07_work_desire_pressure_budget_gate` | `supportive / budget_gate_blocks_expensive_route` | `supportive / budget_gate_blocks_expensive_route` | `supportive / budget_gate_blocks_expensive_route` | `supportive / budget_gate_blocks_expensive_route` | 3/3 |
| `pal_h08_problem_pressure_recovery_not_self_improvement` | `supportive / problem_pressure_recovery_route_allowed` | `supportive / problem_pressure_recovery_route_allowed` | `supportive / problem_pressure_recovery_route_allowed` | `supportive / problem_pressure_recovery_route_allowed` | 3/3 |
| `pal_h09_symptom_closure_ignores_active_leakage` | `supportive / leakage_screen_invalidates_leaking_route` | `supportive / leakage_screen_invalidates_leaking_route` | `supportive / leakage_screen_invalidates_leaking_route` | `supportive / leakage_screen_invalidates_leaking_route` | 3/3 |

## Alignment Summary

```text
Comet          verdict: 9/9   primary_reading: 9/9
Silicon Maid   verdict: 9/9   primary_reading: 9/9
Fimbulvetr     verdict: 9/9   primary_reading: 9/9
```

All models match the deterministic baseline.

## Limitation

This is structured-output consistency validation. It does not constitute empirical truth claims.