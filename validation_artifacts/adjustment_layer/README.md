# Adjustment Layer — Validation Artifacts

Raw evidence for the Adjustment Dynamics validation runs (main pack + holdout pack).

The current public case descriptions follow
[`../case_design_policy.md`](../case_design_policy.md). Older live model-run
JSON files are retained as historical evidence of the exact prompts and outputs
used at the time; do not rewrite them for presentation cleanup.

## Contents

- `main_case_pack.md` — Human-readable description of the 8 main cases.
- `main_cases/` — Eight machine-readable JSON case files for the main pack.
- `holdout_case_pack.md` — Human-readable description of the 9 holdout cases (separate, fresh pack).
- `holdout_cases/` — Nine machine-readable JSON case files for the holdout pack.
- `deterministic_baseline.json` — Deterministic checker output against the 8 main cases.
- `deterministic_holdout_baseline.json` — Deterministic checker output against the 9 holdout cases.

- `model_runs_main/` and `model_runs_holdout/` - archived live model outputs
  from the validation run.

## Main pack cases

| ID | Boundary tested |
|---|---|
| pal_01 | Desire-pressure admissible route |
| pal_02 | Problem-pressure recovery route |
| pal_03 | Markov bridge intermediate states |
| pal_04 | Schrödinger bridge minimal deformation |
| pal_05 | Anti-collapse advice guard |
| pal_06 | Looking-Glass chain integration |
| pal_07 | Budget-constrained routing |
| pal_08 | Leakage pattern invalidates route |

## Holdout pack cases

| ID | Boundary tested |
|---|---|
| pal_h01 | Partial budget reroutes, not blocks |
| pal_h02 | Relationship unilateral repair, leakage |
| pal_h03 | Coaching disguised as recovery routing |
| pal_h04 | Impossible single-step jump |
| pal_h05 | Schrödinger preserves prior dynamics |
| pal_h06 | Health recovery Looking-Glass chain |
| pal_h07 | Work desire-pressure budget gate |
| pal_h08 | Problem-pressure recovery, not self-improvement |
| pal_h09 | Symptom closure ignores active leakage |

## Validation results

```
Main pack (8 cases):
  Deterministic:           8/8
  comet_12b_v.7-i1:        8/8
  silicon-maid-7b-imatrix: 8/8
  fimbulvetr-11b-v2:       8/8

Holdout pack (9 cases):
  Deterministic:           9/9
  comet_12b_v.7-i1:        9/9
  silicon-maid-7b-imatrix: 9/9
  fimbulvetr-11b-v2:       9/9
```

All three models were identity-verified against the LM Studio `/v1/models` endpoint before the run; responses with mismatched model fields were rejected.

## What this evidence supports

- The Adjustment Layer boundary rules are computable as a deterministic baseline.
- The boundary rules generalize from the main pack to a fresh holdout pack.
- The boundary rules are stable across three independent inference surfaces.

## What this evidence does not support

- Empirical truth of the framework's claims about lived experience.
- Correctness of any specific recommendation in any specific real-world case.
- Generalization to cases outside the tested boundaries.

See [`../../03_validation/adjustment_layer.md`](../../03_validation/adjustment_layer.md) for the full validation report and [`../../03_validation/methodology.md`](../../03_validation/methodology.md) for the method.
