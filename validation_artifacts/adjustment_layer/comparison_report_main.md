# Adjustment Layer (Main) — LLM Model Comparison

## Scope

This report is generated from actual model_run files in this repository.

**Models verified:**
- `comet_12b_v.7-i1`
- `silicon-maid-7b-imatrix`
- `fimbulvetr-11b-v2`

## Per-Case Comparison

| Case | Expected | Comet | Silicon Maid | Fimbulvetr | Match |
|---|---|---|---|---|---|
| `pal_01_desire_pressure_admissible_route` | `supportive / desire_pressure_admissible_route_found` | `supportive / desire_pressure_admissible_route_found` | `supportive / desire_pressure_admissible_route_found` | `supportive / desire_pressure_admissible_route_found` | 3/3 |
| `pal_02_problem_pressure_recovery_route` | `supportive / problem_pressure_recovery_route_allowed` | `supportive / problem_pressure_recovery_route_allowed` | `supportive / problem_pressure_recovery_route_allowed` | `supportive / problem_pressure_recovery_route_allowed` | 3/3 |
| `pal_03_markov_bridge_intermediate_states` | `supportive / markov_bridge_intermediate_states_valid` | `supportive / markov_bridge_intermediate_states_valid` | `supportive / markov_bridge_intermediate_states_valid` | `supportive / markov_bridge_intermediate_states_valid` | 3/3 |
| `pal_04_schrodinger_bridge_minimal_deformation` | `supportive / schrodinger_bridge_minimal_deformation_valid` | `supportive / schrodinger_bridge_minimal_deformation_valid` | `supportive / schrodinger_bridge_minimal_deformation_valid` | `supportive / schrodinger_bridge_minimal_deformation_valid` | 3/3 |
| `pal_05_anti_collapse_advice_guard` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | 3/3 |
| `pal_06_looking_glass_chain` | `supportive / looking_glass_chain_upstream_informs_adjustment` | `supportive / looking_glass_chain_upstream_informs_adjustment` | `supportive / looking_glass_chain_upstream_informs_adjustment` | `supportive / looking_glass_chain_upstream_informs_adjustment` | 3/3 |
| `pal_07_budget_constrained_routing` | `supportive / budget_gate_blocks_expensive_route` | `supportive / budget_gate_blocks_expensive_route` | `supportive / budget_gate_blocks_expensive_route` | `supportive / budget_gate_blocks_expensive_route` | 3/3 |
| `pal_08_leakage_pattern_invalidates_route` | `supportive / leakage_screen_invalidates_leaking_route` | `supportive / leakage_screen_invalidates_leaking_route` | `supportive / leakage_screen_invalidates_leaking_route` | `supportive / leakage_screen_invalidates_leaking_route` | 3/3 |

## Alignment Summary

```text
Comet          verdict: 8/8   primary_reading: 8/8
Silicon Maid   verdict: 8/8   primary_reading: 8/8
Fimbulvetr     verdict: 8/8   primary_reading: 8/8
```

All models match the deterministic baseline.

## Limitation

This is structured-output consistency validation. It does not constitute empirical truth claims.