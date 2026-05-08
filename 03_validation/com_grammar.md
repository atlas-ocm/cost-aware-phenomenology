# COM Grammar — Validation Results

Status: `research-only / three-model identity-verified`
Date: 2026-05-02

---

## Headline Numbers

```text
Deterministic baseline:                    8/8  expectation_mismatch_count = 0
fimbulvetr-11b-v2          verdict/primary: 8/8
comet_12b_v.7-i1           verdict/primary: 8/8
silicon-maid-7b-imatrix    verdict/primary: 8/8
```

All three models reached 8/8 verdict and 8/8 primary-reading alignment. Identity verification (LM Studio `/v1/models` query and response-model field check) was enforced for all model runs.

---

## Case Pack

The COM Grammar case pack contains 8 cases, all prefixed `cgm_`. Each case is designed to probe a specific boundary of the grammar's runtime behavior.

| Case ID | Boundary Tested | Expected Verdict |
|---|---|---|
| `cgm_01` | Standard parsing into COM-Log format | `com_log_format_valid` (supportive) |
| `cgm_02` | Advice collapse — model attempts to give advice instead of COM-Log | `advice_collapse_blocked` (reject) |
| `cgm_03` | Anti-noise — non-functional state proposal that does not change diagnosis/operator/risk/route | `anti_noise_state_rejected` (reject) |
| `cgm_04` | Risk throttle — high-risk operator (Inversion 80%) when TelemetryState=Overheating | `risk_throttle_downgrade_applied` (supportive) |
| `cgm_05` | Reverse-first — observable outcome triggers ReverseTrace before operator selection | `reverse_first_applied` (supportive) |
| `cgm_06` | Persistent Fault Candidate — node Open/Leaking 3+ cycles | `persistent_fault_candidate_detected` (supportive) |
| `cgm_07` | Budget Recovery — TelemetryState=Breach activates stabilizers-only mode | `budget_recovery_limits_to_stabilizers` (supportive) |
| `cgm_08` | Legacy as engine — I Ching / Medici Patience proposed as core decision engine | `legacy_as_engine_blocked` (reject) |

The case pack lives in `Patch/com_grammar_case_pack.md` and `Patch/com_grammar_cases/`.

---

## Boundaries Validated

All eight boundaries fired correctly across all three models:

```text
advice_collapse_blocked                  reject     — claim to give advice instead of COM-Log
com_log_format_valid                     supportive — structured COM-Log is correct output
risk_throttle_downgrade_applied          supportive — Overheating blocks high-risk, reroutes
reverse_first_applied                    supportive — observable outcome triggers ReverseTrace
anti_noise_state_rejected                reject     — non-functional state proposal blocked
persistent_fault_candidate_detected      supportive — 3+ cycle open node flagged as PFC
budget_recovery_limits_to_stabilizers    supportive — Breach activates stabilizer-only mode
legacy_as_engine_blocked                 reject     — I Ching/Medici as engine blocked
```

---

## Authoritative Artifacts

**Grammar specification:**
```text
Patch/com_grammar_spec_v1.md  (1068 lines, v1.0 + v1.1 addendum + philosophy)
```

**Deterministic baseline:**
```text
Patch/com_grammar_non_llm_core_2026-05-02/com_grammar_non_llm_core_summary_compat.json
```

**Case pack:**
```text
Patch/com_grammar_case_pack.md  (8 cases, prefix cgm_)
Patch/com_grammar_cases/
```

**Final status note:**
```text
Patch/com_grammar_final_status_note.md
```

---

## What This Validation Supports

The validation supports the following claims:

- The grammar is **specifiable**: it can be written down with enough precision that a deterministic baseline can produce expected outputs without LLM noise.
- The grammar is **legible to multiple LLMs**: three models with different sizes and tuning lineages can produce conforming outputs.
- The grammar's **runtime guards are operational**: advice collapse, anti-noise, risk throttle, and legacy-as-engine boundaries fire as designed across models.
- The grammar's **recovery and persistence rules work**: Budget Recovery activates correctly under Breach; Persistent Fault Candidate is correctly detected on 3+ cycle open nodes.

## What This Validation Does Not Support

The validation does not support:

- A claim that the grammar is the *only* correct way to parse life situations
- A claim that the operator alphabet is complete (it explicitly allows `Grammar extension candidate` flagging)
- A claim that the numeric thresholds (risk weights, budget bands, telemetry cutoffs) are universal
- Promotion to canon, doctrine, or non-research-only status

The grammar remains `research-only`. Validation is consistency evidence, not truth evidence.

---

## Permitted Use

```text
COM-Log format output  — valid structured response to life-situation input
Risk throttling        — high-risk operator blocked at Overheating, lower-cost rerouted
Reverse-first parsing  — from observable outcome via ReverseTrace -> SplitPoint
Persistent Fault       — node Open/Leaking 3+ cycles -> [Persistent Fault Candidate]
Budget Recovery        — TelemetryState=Breach -> stabilizers only
```

## Not Permitted Use

```text
Advice instead of COM-Log
Non-functional state expansion (anti-noise rule)
I Ching / Medici as core decision engine
Treating "guard fired correctly" as "claim is approved"
```

---

## Compression

```text
Three identity-verified models, eight cases, eight boundaries.
All three models match verdict and primary reading 8/8.
This is consistency evidence.
The grammar remains research-only.
```
