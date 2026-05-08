# Validation Methodology

CAP is validated against a three-tier pattern. This document describes the pattern, explains why it matters for a phenomenology framework, and states the limits of what the validation supports.

---

## Why Validate a Phenomenology Framework

Most frameworks for analyzing lived experience are validated through philosophical argument, case studies, or clinical outcome reports. These are useful but limited:

- philosophical argument can be internally consistent and operationally empty
- case studies are subject to selection bias and post-hoc rationalization
- clinical outcome reports require infrastructure that small frameworks cannot afford

CAP adds a fourth method: **machine-checkable structured outputs**. The framework defines what a valid output looks like (COM-Log v1.1 with specific fields, valid operator alphabet, valid status syntax, telemetry gating, budget enforcement). Then we test whether multiple LLMs, given the same case input, produce outputs that match the expected structure and verdict.

This does not replace the other validation methods. It supplements them with a check that no other phenomenology framework currently performs at scale.

---

## Three-Tier Validation

Every CAP component is validated in three tiers:

### Tier 1 — Deterministic Baseline

A non-LLM core implementation runs the case pack and produces structured outputs. The deterministic baseline establishes what the *expected* output is for every case, without LLM noise. Cases are designed with explicit expected verdicts (e.g., `risk_throttle_downgrade_applied`, `advice_collapse_blocked`).

The deterministic baseline must achieve `expectation_mismatch_count = 0` before LLM validation begins. If the deterministic baseline cannot produce the expected output, the case is malformed and gets revised.

### Tier 2 — LLM Validation

The same case pack is presented to multiple identity-verified LLMs. Each LLM must:

- match the expected verdict
- produce a primary reading consistent with the expected interpretation
- respect all guards (advice collapse, anti-noise, risk throttle, etc.)

**Identity verification** means the LM Studio `/v1/models` endpoint is queried before each model run, and each LM Studio response's `model` field is checked against the requested model id. A run is not counted if the loaded model identity cannot be confirmed. This rules out a class of validation errors where a different model than requested produces the response.

Three models are used per validated component:

- `comet_12b_v.7-i1`
- `silicon-maid-7b-imatrix`
- `fimbulvetr-11b-v2`

These were selected because they vary in size (7B / 11B / 12B), in tuning lineage, and in default behavior. They are not selected for being CAP-friendly — they are selected for being available local models that span enough variation to make agreement meaningful.

### Tier 3 — Holdout (optional)

For components that pass main validation, a fresh holdout case pack is constructed. The holdout cases are not derived from the main pack; they probe boundaries and edge cases that the main pack does not cover. The same LLMs are run against the holdout pack with the same identity verification.

A component is considered to have passed holdout if all tested models match verdict and primary reading on all holdout cases.

---

## Why This Matters

Most frameworks for lived experience cannot be validated this way because their outputs are not structured. A typical philosophical analysis of a relationship situation is a paragraph that no machine can verify against an expected verdict. CAP's outputs are structured COM-Log blocks with specific required fields, so a verdict and primary reading can be extracted and checked programmatically.

The benefit is not that LLM agreement *proves* the framework. It is that LLM agreement *rules out* a class of failure modes:

- **The framework is so vague that any output passes.** Ruled out by the deterministic baseline expectation matching.
- **The framework is so specific that only one model can produce its outputs.** Ruled out by multi-model agreement.
- **The framework's outputs are model-dependent in a way that hides the framework's actual operation.** Ruled out by identity-verified runs.
- **The framework's outputs are case-pack-dependent.** Ruled out (partially) by holdout passes.

What remains after these failure modes are ruled out is not "proof of CAP" — it is "the framework operates consistently across models and across case packs at this validation surface."

---

## Anti-Overclaim Rule

Validation supports the framework's status as `research-only`. It does not promote the framework to canon, doctrine, or "proven." Specifically:

- A 3-models 8/8 result is consistency evidence, not truth evidence.
- LLM agreement is not external-world evidence. The framework's external-world validity depends on whether the operators it recommends, when applied, produce the predicted state changes. That validation requires real-world deployment, not LLM runs.
- Validation does not establish numeric thresholds as ontological constants. A `risk_throttle_downgrade_applied` verdict at 30% Overheating ceiling is consistency with the framework's defaults, not proof that 30% is a universal cognitive constant.

The anti-overclaim rule is enforced at the documentation level. Validation results are reported with explicit "this does not promote the layer beyond research-only" language.

---

## Numeric Thresholds Are Engineering Defaults

All numerical thresholds — risk percentages, budget bands, telemetry cutoffs, leak levels — are **engineering defaults**. They are not:

- discovered constants
- empirical proof
- universal psychological laws

They are:

- runnable assumptions
- calibration targets
- sensitivity points

If changing a threshold changes the recommendation, the system must mark the decision as `threshold-sensitive / provisional`.

```text
Thresholds are knobs, not truths.
```

---

## What Validation Does Not Cover

The current validation surface does not cover:

- **External outcomes**: whether observers who follow CAP recommendations have better real-world results than observers who do not. This is not testable inside the current setup.
- **Long-horizon stability**: whether CAP analyses produced today are still valid in cycles months later. The framework does not yet have longitudinal validation.
- **Cross-cultural generality**: validation cases are written from a specific cultural and linguistic context. Cross-cultural validity is an open question.
- **Edge cases of clinical pathology**: CAP is not validated for use in active psychiatric crises, severe dissociation, or other states where the observer's continuity assumption is broken.

These are documented limits, not hidden problems. They define the next research targets.

---

## Component-Specific Validation

For per-component results see:

- [`com_grammar.md`](./com_grammar.md) — COM Grammar validation results
- [`adjustment_layer.md`](./adjustment_layer.md) — Adjustment Layer validation results
- [`../04_extensions/looking_glass.md`](../04_extensions/looking_glass.md) — Looking-Glass extension validation status
- [`../04_extensions/latent_cause_reconstruction.md`](../04_extensions/latent_cause_reconstruction.md) — A-Reconstruction validation status

---

## Compression

```text
The framework defines structured outputs.
The deterministic baseline defines expected outputs.
The LLM validation tests whether multiple identity-verified models
can produce those outputs across a case pack.
The holdout tests whether the agreement extends to fresh cases.

This is consistency evidence, not truth evidence.
The framework remains research-only.
```
