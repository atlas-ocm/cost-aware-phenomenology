# CAP Roadmap

## v0.1 — Initial public research release (current)

- Conceptual framework: thesis, positioning, epistemic contract, primitive-experience grounding
- Six subsystems documented (transition cost, observer budget, telemetry gating, operator admissibility, COM Grammar, Adjustment Dynamics)
- Six machine-readable JSON Schemas (com_log, operator_alphabet, runtime_telemetry, response_policy, validator_result, self_audit)
- Two diagnostic extensions documented (Looking-Glass, Latent Cause Reconstruction)
- LLM/RAG dialogue proxy application (anti-self-justification, RAG confidence gating, self-audit)
- CAP Lite reference middleware and integration guide for OpenAI-compatible / RAG pipelines
- Qualitative comparative positioning against prompt-only, rules, RAG-only, validators, fine-tuning, CAP-style proxy, and hybrid stacks
- Gold Case demonstrations for anti-self-justification, sycophancy, weak-RAG overclaiming, and stale cross-turn anchors
- Trace Library with initial LLM dialogue failure traces
- Two worked examples (client free-edits case, anti-self-justification loop)
- Validation methodology, falsifiability, and claims documents
- Validation artifacts: deterministic baselines + LLM model_runs from 3 identity-verified models
  - COM Grammar: 8 cases x 3 models — all 8/8
  - Adjustment Layer: 8 main cases x 3 models — all 8/8
  - Adjustment Layer holdout: 9 cases x 3 models — all 9/9
- LLM dialogue proxy policy pack: 8 deterministic cases
- LLM dialogue benchmark scaffold: baseline 5 cases x 5 modes and
  hard-holdout 15 cases x 5 modes
- Initial live LLM dialogue benchmark:
  - comet_12b_v.7-i1 and silicon-maid-7b-imatrix baseline-v1 run
  - 50 generation calls on the original small pack
  - proxy-level CAP scored 5/5 on both models under the current heuristic
    scorer
  - qwen/qwen3.5-9b baseline-v1 run added with generation-budget reporting
- Hard-holdout live stress track:
  - mistral-nemo-instruct-2407 complete live run
  - atlas/qwen3.5-9b-no-thinking complete live run after standard Qwen
    released-output failures
  - Gemini 2.5 Flash partial free-tier control and Gemini Pro access/quota
    failure note
  - lexical and release-gate reports documented as stress/adjudication
    artifacts, not final benchmark claims
- Deterministic proxy release gate for already-produced hard-holdout outputs
- Preregistered release-gate v0.2 implementation with separate v0.2 reports
  and v0.1/v0.2 comparison
- Deterministic post-gate rewrite shaper for hard-holdout outputs, with
  separate shaped artifacts and v0.2 gate checks
- Compact release-gate boundary adjudication pack, with Codex draft labels
  reported only as a debugging artifact
- Scorer audit for the initial LLM dialogue benchmark
- Blinded manual adjudication pack prepared for the first live run
- Optional model-graded auditor prompt pack scaffold
- Manual adjudication disagreement-analysis scaffold
- Python reference validator, CAP Lite middleware, optional auditor scaffold,
  release-gate tools, rewrite shaper, disagreement analyzers, and benchmark
  tools with tests (47 tests, all passing)
- Artifact integrity checker (validate_artifacts.py)
- GitHub Actions workflow for CAP reproducibility checks
- ASCII and Mermaid pipeline diagrams
- Critiques and responses note for external reviewers
- Glossary (30+ terms), CLAIMS.md, REPRODUCIBILITY.md

## v0.2 — External review + integrity hardening

- Address external reviewer feedback
- Scorer audit hardening for LLM dialogue benchmark
- Freeze scoring patterns before future live runs
- Continue release-gate v0.2 review from the preregistered comparison
  (see
  [`validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/release_gate_v01_v02_comparison.md`](./validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/release_gate_v01_v02_comparison.md))
- Review deterministic shaped outputs separately from raw model outputs; do not
  report shaped release rates as model benchmark scores
- Fill and compare manual/blinded adjudication labels for current live outputs
- Run optional model-graded auditor over the current live outputs and compare against manual labels
- Complete manual adjudication for the Mistral Nemo v1 and hardened v2 runs
- Complete manual adjudication for the four-model baseline-v1 pack
- Analyze lexical-scorer disagreements before any scorer update
- Keep Codex draft labels separated from independent human adjudication labels
- Run Gemini Pro or another strong external-model control only after provider
  access is working and scoring criteria are frozen
- CI configuration for schema, artifact integrity, policy pack, and benchmark scaffold checks
- LessWrong-style writeup for external feedback
- Additional worked examples across multiple domains
- Expand Trace Library from 3 traces to 5-7 compact traces
- Add rendered SVG exports for Mermaid diagrams if needed for GitHub / paper packaging

## v0.3 — Parser and dialogue proxy reference implementation

- Python reference parser: input text -> COM-Log
- LLM dialogue proxy reference: anti-self-justification + RAG confidence gating
- Parser-integrated validator/shaper reference implementation
- Larger LLM dialogue benchmark case pack (10-15 cases)
- Additional model families and reruns with frozen scoring criteria
- Third-model live dialogue benchmark rerun after manual adjudication and frozen scorer update

## v0.4 — Human-rated transition-cost study

- Survey instrument for subjective burden ratings
- Inter-rater agreement study on operator selection
- Calibration data for risk-weight ranges

## v0.5 — Public evaluation benchmark

- Standardized eval harness for cost-aware dialogue systems
- Quantitative comparison benchmarks against baseline systems
- Open eval cases beyond synthetic test packs
- Separate raw lexical score from manual adjudicated score

## Beyond v0.5

- Cross-domain applications (decision support, repair planning, route engineering)
- Community case contributions
- Enterprise integration documentation (paid layer)
