# COM Grammar — Validation Artifacts

Raw evidence for the COM Grammar (Layer C) validation runs.

## Contents

- `case_pack.md` — Human-readable description of all 8 cases, with expected verdicts and the boundary each case exercises.
- `cases/` — Eight machine-readable JSON case files used by the deterministic baseline and the LLM runs.
- `deterministic_baseline.json` — Output of the deterministic (non-LLM) checker against the 8 cases. This is the reference verdict.

## Cases covered

| ID | Boundary tested |
|---|---|
| cgm_01 | Advice collapse blocked |
| cgm_02 | COM-Log format valid |
| cgm_03 | Risk throttle downgrade applied |
| cgm_04 | Reverse-first parsing applied |
| cgm_05 | Anti-noise state rejected |
| cgm_06 | Persistent fault candidate detected |
| cgm_07 | Budget recovery limits to stabilizers |
| cgm_08 | Legacy-as-engine blocked |

## Validation results

```
Deterministic baseline:    8/8
fimbulvetr-11b-v2:        8/8 verdict / 8/8 primary reading
comet_12b_v.7-i1:         8/8 verdict / 8/8 primary reading
silicon-maid-7b-imatrix:  8/8 verdict / 8/8 primary reading
```

All three models were identity-verified against the LM Studio `/v1/models` endpoint before the run; responses with mismatched model fields were rejected.

## What this evidence supports

- The COM Grammar boundary rules are computable as a deterministic baseline.
- The boundary rules are stable across three independent inference surfaces.

## What this evidence does not support

- Empirical truth of the framework's claims about lived experience.
- Correctness of any specific recommendation in any specific real-world case.
- Generalization to cases outside the tested boundaries.

See [`../../03_validation/com_grammar.md`](../../03_validation/com_grammar.md) for the full validation report and [`../../03_validation/methodology.md`](../../03_validation/methodology.md) for the method.
