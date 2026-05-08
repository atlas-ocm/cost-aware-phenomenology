# COM Grammar (Chain Operator Module) Case Pack

Date: 2026-05-02

Status: `research-only / deterministic synthetic baseline`

Purpose:

- test COM Grammar as a structured operator-log layer for life-route parsing;
- preserve correct COM-Log output, reverse-first parsing, risk throttling, persistent fault detection, and budget recovery;
- separate anti-advice-collapse, anti-noise, legacy boundary, and structured COM output from collapse into generic advice, non-functional state expansion, or legacy-system-as-engine substitution.

## Cases

| Case | Target Verdict | Target Reading | Boundary Tested |
|---|---|---|---|
| `cgm_01_advice_collapse_blocked` | `reject` | `advice_collapse_blocked` | anti-advice-collapse: output must be COM-Log, not generic advice |
| `cgm_02_com_log_format_valid` | `supportive` | `com_log_format_valid` | COM-Log baseline: correct output format allowed |
| `cgm_03_risk_throttle_downgrade_applied` | `supportive` | `risk_throttle_downgrade_applied` | risk throttling: high-risk operator blocked at Overheating telemetry |
| `cgm_04_reverse_first_applied` | `supportive` | `reverse_first_applied` | reverse-first: when outcome visible, start from ReverseTrace → SplitPoint |
| `cgm_05_anti_noise_state_rejected` | `reject` | `anti_noise_state_rejected` | anti-noise: new state must change diagnosis/operator/risk/forecast to be valid |
| `cgm_06_persistent_fault_candidate_detected` | `supportive` | `persistent_fault_candidate_detected` | persistent fault: node open 3+ cycles must be flagged as PFC |
| `cgm_07_budget_recovery_limits_to_stabilizers` | `supportive` | `budget_recovery_limits_to_stabilizers` | budget recovery: only low-risk stabilizers when TelemetryState=Breach |
| `cgm_08_legacy_as_engine_blocked` | `reject` | `legacy_as_engine_blocked` | legacy boundary: I Ching/Medici as engine blocked (frontend only) |

Runner:

- `run_com_grammar_non_llm_core.py`

Expected deterministic result:

```text
total_cases = 8
expectation_mismatch_count = 0
```

## Boundary

What COM Grammar tests:
- correct structured COM-Log output (typed domain, node, status, operator, next physical step);
- rejection of advice collapse (generic "you should..." output instead of COM-Log);
- risk throttling under Overheating/Breach telemetry (high-risk operators blocked, downgraded to stabilizers);
- reverse-first parsing when outcome is already observable (ReverseTrace → SplitPoint before forward history);
- anti-noise rule (new states/operators/nodes only valid if they change diagnosis, operator, risk, or forecast);
- persistent fault candidate detection (node open/leaking 3+ cycles → PFC flag + operator change required);
- budget recovery protocol (TelemetryState=Breach → only low-risk stabilizers permitted);
- legacy boundary enforcement (I Ching, Medici Patience as frontend analogy only, not as COM engine).

What COM Grammar does not test:
- this is not therapy, life coaching, or motivational advice;
- this is not financial planning or investment guidance;
- shortlist agreement would only support a bounded COM operator grammar interpretation;
- advice collapse, non-functional state expansion, and legacy-as-engine remain blocked.
