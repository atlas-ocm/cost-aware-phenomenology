# Claims, Boundaries, and Current Validation

This file makes explicit what CAP claims, what it does not claim, and what current validation supports vs does not support.

## CAP claims

- **Transition cost is useful as a modeling primitive** for analyzing experiential routes.
- **COM Grammar can structure certain transition problems** into a typed operator-status graph.
- **Telemetry gating can prevent over-budget recommendations** that would fail under current observer state.
- **Previous model generations are not evidence**, and self-audit by telemetry is more reliable than defending past outputs.
- **Boundaries between operators, states, and domains are machine-checkable** with current schemas.

## CAP does not claim

- Empirical proof of phenomenal consciousness.
- Psychological diagnosis or clinical authority.
- Guaranteed delivery of any wished-for outcome.
- Objective truth detection or universal decision authority.
- That LLM behavior validates CAP ontology (LLM is scaffold, not evidence).
- That numeric thresholds (RiskWeight values, telemetry signals) are anything but provisional engineering defaults.
- That qualitative comparisons against prompting, RAG, validators, or fine-tuning are benchmark results.

## Current validation supports

- **Schema consistency** across the COM-Log document format.
- **Structured-output reproducibility** via JSON Schema validation.
- **Bounded model agreement** on supplied test cases:
  - COM Grammar: 3 identity-verified LLMs match deterministic baseline 8/8 (verdict and primary reading).
  - Adjustment Layer: 3 models 8/8 main, 9/9 holdout.
- **Boundary-rule stability** across multiple independent inference surfaces.
- **Artifact integrity**: all 25 case files have corresponding model_runs from all 3 models (verified by `validate_artifacts.py`).
- **LLM dialogue proxy policy coverage**: 8 deterministic proxy cases pass under the reference policy pack.
- **CAP Lite middleware behavior**: the copyable middleware has unit coverage for self-justification, sycophancy, overload, and supported technical-query routing.
- **Initial live dialogue benchmark**: proxy-level CAP scored 5/5 on comet and silicon under the current small-pack heuristic scorer.
- **Third-model transfer probe**: `mistral-nemo-instruct-2407` was added as an exploratory run and exposed prompt/scorer transfer sensitivity under the current templates.
- **Exact-model hardening result**: `mistral-nemo-instruct-2407` was rerun with hardened v2 prompts; the current lexical CAP-mode score did not improve.
- **Qwen reasoning-budget result**: `qwen/qwen3.5-9b` required `max_tokens=8192` for released outputs and scored 4/5 under proxy-level CAP in the baseline-v1 run.
- **Hard-holdout stress track**: a separate 15-case pack has complete Mistral Nemo and Qwen no-thinking live runs, plus deterministic proxy release-gate reports. These are reported as transfer-stress/adjudication artifacts, not final benchmark claims. Current claim status is summarized in [`validation_artifacts/llm_dialogue_benchmark/hard_holdout/evaluation_status.md`](./validation_artifacts/llm_dialogue_benchmark/hard_holdout/evaluation_status.md).
- **Release-gate boundary review scaffold**: a compact 25-item blinded pack exists for `release` and `block` gate actions. Codex draft labels show 21/25 agreement with the deterministic gate, but are explicitly non-human debugging labels.
- **Preregistered release-gate v0.2 comparison**: v0.2 shape checks were applied only as explicit separate reports and moved six hard-holdout case actions, mostly from `release` to `rewrite_required`. This supports release-boundary hardening, not a benchmark win.
- **Deterministic rewrite-shaper boundary**: a post-gate shaper rewrites
  non-release hard-holdout outputs into case-contract release candidates and
  rechecks them with release gate v0.2. This supports the feasibility of a
  gate-to-rewrite boundary, not raw model performance.
- **Deployable local architecture demo**: Qwen presentable drafts plus CAP
  release gate, deterministic rewrite shaping, and final gate verification
  produced 75/75 shaped release candidates. Because 64/75 candidates were
  rewritten from case contracts, this supports pipeline feasibility rather than
  a raw Qwen performance claim.
- **Gemini external controls**: Gemini 2.5 Flash produced a partial free-tier
  run. A later Gemini 3.1 Pro presentable five-mode run produced 75/75 raw
  outputs. Under `release_gate v0.2`, baseline modes had 8/45 raw blocks while
  CAP modes had 0/30 raw blocks. After deterministic shaping, all 75 candidates
  passed the final gate. Because 67/75 candidates were rewritten from case
  contracts, this supports external architecture feasibility rather than a
  frozen benchmark or raw model-performance claim.

## Current validation does not yet prove

- Real-world outcome improvement from applying CAP recommendations.
- Clinical, financial, or relationship usefulness.
- Generalization beyond the test cases included in `validation_artifacts/`.
- Inter-rater agreement among human analysts.
- Predictive validity of transition-cost estimates.
- That the framework itself produces better outcomes for any of its target domains.
- That CAP objectively outperforms prompt-only, RAG-only, validator-only, fine-tuning, LoRA, or RLHF systems on external benchmarks.
- That the current heuristic LLM dialogue scorer is a final human-quality benchmark.
- That the current CAP prompt templates transfer cleanly across all instruct models.
- That prompt hardening alone resolves the Mistral Nemo transfer issue.
- That reasoning-heavy models can be evaluated fairly without reporting generation budget and checking released `message.content`.
- That hard-holdout lexical scores are final human-quality benchmark results.
- That deterministic release-gate actions already match independent human release decisions.
- That Codex draft labels can replace independent human adjudication.
- That preregistered v0.2 release-gate hardening is human-validated.
- That deterministic shaped outputs are raw model outputs or benchmark wins.
- That the Qwen gate/rewrite pipeline result means Qwen solved 75/75 cases.
- That the Gemini presentable five-mode comparison establishes full
  external-provider benchmark performance.

See [`03_validation/falsifiability.md`](./03_validation/falsifiability.md) for what would count against each claim.
