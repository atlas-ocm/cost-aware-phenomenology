# Validation Artifacts

This folder contains raw validation evidence for the CAP framework subsystems.

Public-facing case packs follow
[`case_design_policy.md`](./case_design_policy.md). The policy favors neutral
engineering/product/operations scenarios and separates archived historical
outputs from current benchmark surfaces.

## Contents

- `com_grammar/` - validation pack and results for COM Grammar (Layer C)
  - 8 deterministic cases
  - 3 identity-verified models: comet_12b_v.7-i1, silicon-maid-7b-imatrix, fimbulvetr-11b-v2
  - all models 8/8 on verdict and primary reading

- `adjustment_layer/` - validation pack and results for Adjustment Dynamics
  - 8 main cases + 9 holdout cases
  - same 3 identity-verified models
  - all models 8/8 on main, 9/9 on holdout

- `llm_dialogue_proxy/` - deterministic policy-surface checks for LLM/RAG
  release control
  - 8 cases
  - no LLM calls
  - telemetry/context flags -> response policy behavior

- `llm_dialogue_benchmark/` - scaffold for LLM-in-the-loop mode comparison
  - 5 cases
  - 5 intended modes
  - default report uses synthetic smoke outputs
  - first live two-model run included under `model_outputs/`
  - no LLM calls in the scorer itself

See:

- [`llm_dialogue_proxy/benchmark_report.md`](./llm_dialogue_proxy/benchmark_report.md)
- [`llm_dialogue_benchmark/scaffold_report.md`](./llm_dialogue_benchmark/scaffold_report.md)
- [`llm_dialogue_benchmark/scorer_audit.md`](./llm_dialogue_benchmark/scorer_audit.md)
- [`llm_dialogue_benchmark/adjudication/README.md`](./llm_dialogue_benchmark/adjudication/README.md)
- [`llm_dialogue_benchmark/model_outputs/comet_silicon_report.md`](./llm_dialogue_benchmark/model_outputs/comet_silicon_report.md)
- [`case_design_policy.md`](./case_design_policy.md)

## What these prove and don't prove

These artifacts demonstrate that the CAP boundary rules are:

1. Computable as a deterministic baseline
2. Stable across multiple independent inference surfaces

They do NOT prove:

- Empirical truth of the framework's claims about lived experience
- That any specific operator recommendation is correct in any specific real case
- That the framework generalizes outside the tested boundaries
- That the synthetic LLM dialogue benchmark fixture is an empirical model result
- That the initial live benchmark is sufficient for deployment claims

The validation supports research-only status, not certified canon.
