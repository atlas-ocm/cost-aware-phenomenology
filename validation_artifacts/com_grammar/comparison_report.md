# COM Grammar — LLM Model Comparison

## Scope

This report is generated from actual model_run files in this repository.

**Models verified:**
- `comet_12b_v.7-i1`
- `silicon-maid-7b-imatrix`
- `fimbulvetr-11b-v2`

## Per-Case Comparison

| Case | Expected | Comet | Silicon Maid | Fimbulvetr | Match |
|---|---|---|---|---|---|
| `cgm_01_advice_collapse_blocked` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | `reject / advice_collapse_blocked` | 3/3 |
| `cgm_02_com_log_format_valid` | `supportive / com_log_format_valid` | `supportive / com_log_format_valid` | `supportive / com_log_format_valid` | `supportive / com_log_format_valid` | 3/3 |
| `cgm_03_risk_throttle_downgrade_applied` | `supportive / risk_throttle_downgrade_applied` | `supportive / risk_throttle_downgrade_applied` | `supportive / risk_throttle_downgrade_applied` | `supportive / risk_throttle_downgrade_applied` | 3/3 |
| `cgm_04_reverse_first_applied` | `supportive / reverse_first_applied` | `supportive / reverse_first_applied` | `supportive / reverse_first_applied` | `supportive / reverse_first_applied` | 3/3 |
| `cgm_05_anti_noise_state_rejected` | `reject / anti_noise_state_rejected` | `reject / anti_noise_state_rejected` | `reject / anti_noise_state_rejected` | `reject / anti_noise_state_rejected` | 3/3 |
| `cgm_06_persistent_fault_candidate_detected` | `supportive / persistent_fault_candidate_detected` | `supportive / persistent_fault_candidate_detected` | `supportive / persistent_fault_candidate_detected` | `supportive / persistent_fault_candidate_detected` | 3/3 |
| `cgm_07_budget_recovery_limits_to_stabilizers` | `supportive / budget_recovery_limits_to_stabilizers` | `supportive / budget_recovery_limits_to_stabilizers` | `supportive / budget_recovery_limits_to_stabilizers` | `supportive / budget_recovery_limits_to_stabilizers` | 3/3 |
| `cgm_08_legacy_as_engine_blocked` | `reject / legacy_as_engine_blocked` | `reject / legacy_as_engine_blocked` | `reject / legacy_as_engine_blocked` | `reject / legacy_as_engine_blocked` | 3/3 |

## Alignment Summary

```text
Comet          verdict: 8/8   primary_reading: 8/8
Silicon Maid   verdict: 8/8   primary_reading: 8/8
Fimbulvetr     verdict: 8/8   primary_reading: 8/8
```

All models match the deterministic baseline.

## Limitation

This is structured-output consistency validation. It does not constitute empirical truth claims.