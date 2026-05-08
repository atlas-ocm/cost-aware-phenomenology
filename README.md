# CAP — Cost-Aware Phenomenology

*A typed operator framework for budget-limited transitions in lived experience.*

---

Experience is not only meaningful, embodied, and predictive. It is also **transition-costly**. CAP is a framework for analyzing experiential routes in terms of what it costs to leave a state, which operators can move it, and whether the observer can safely execute them.

A state is not defined only by how it appears, but also by what it costs to leave it, which operators can move it, and whether the current observer has the budget and the telemetry to fire those operators at all.

---

## What CAP IS

- An **observer-centric framework** for describing the organization of lived experience
- A **typed operator grammar** (13 operators, 12 domains, 16 statuses) for parsing life situations into routes
- A **transition-cost calculus** that treats every state change as an action with a budget cost and a failure probability
- A **telemetry-gated discipline** that refuses to recommend operators the observer cannot execute right now
- A **risk-throttling system** that downgrades unsafe operator selections automatically
- A **machine-checkable** framework: outputs are structured, validated, reproducible across models
- A **research-only** working surface — a working tool, not certified canon

## What CAP IS NOT

- Not a theory of consciousness
- Not a solution to the hard problem
- Not a proven cosmology or physics
- Not a deterministic fate system
- Not a divination system or symbolic oracle
- Not a license for magical thinking
- Not a coaching system or motivational psychology
- Not financial, medical, legal, or relationship advice
- Not a guarantee of delivery for any wished-for outcome
- Not a proof that LLM behavior validates the model (LLM is scaffold, not evidence)

## Validation status

```text
Deterministic baseline:           8/8 main, 9/9 holdout
COM Grammar (3 models):           comet 8/8, silicon 8/8, fimbulvetr 8/8
Adjustment Layer (3 models):      comet 8/8, silicon 8/8, fimbulvetr 8/8 (main)
                                  comet 9/9, silicon 9/9, fimbulvetr 9/9 (holdout)
LLM Dialogue Proxy policy:        8/8 deterministic proxy cases
CAP Lite reference middleware:    4/4 unit tests
LLM Dialogue Benchmark scaffold:  5 cases x 5 modes, synthetic smoke report
LLM Dialogue Benchmark baseline:  proxy-level CAP 5/5 comet, 5/5 silicon, 4/5 qwen
Hard-holdout stress track:        Mistral + Qwen no-thinking complete
Gemini API-access note:           2.5 Flash partial run only; incomplete due to access/quota limits
Proxy release gate:               deterministic hard-holdout gate reports + 25-item boundary pack
Release-gate v0.2:                preregistered hardening comparison, separate reports
Proxy rewrite shaper:             deterministic post-gate release candidates, not raw model scores
Deployable architecture demo:      Qwen + CAP gate/rewrite pipeline, 75/75 shaped release candidates
External Gemini comparison:        Gemini 3.1 Pro presentable 5-mode run; CAP raw blocks 0/30 vs baseline raw blocks 8/45
Current adjudication status:      Codex draft labels only; human adjudication still pending
```

Local LM Studio runs were identity-verified against the `/v1/models` surface.
Gemini controls are documented separately: Gemini 2.5 Flash remains a partial
API-access/quota attempt, not a benchmark lane or external ceiling estimate.
Gemini 3.1 Pro is a complete presentable five-mode architecture comparison.
Status remains `research-only`: validation supports the framework as a usable
working surface, not as certified canon.

These results validate boundary consistency and machine-checkability across multiple inference surfaces. The baseline live dialogue benchmark is an initial small-pack result with a lexical/heuristic scorer. The Qwen run required a larger generation budget because smaller budgets produced empty released outputs. The hard-holdout runs, Gemini 2.5 Flash access/quota note, Gemini 3.1 Pro and CAP-only controls, deterministic release-gate reports, and deterministic rewrite-shaper reports are deliberately reported as transfer-stress and pipeline-boundary artifacts, not as polished benchmark wins. Codex draft labels are debugging aids, not independent human labels. These artifacts do not constitute broad empirical truth claims.

The deterministic rewrite shaper demonstrates the next runtime boundary:
non-release outputs can be transformed into case-contract release candidates and
then checked again by the gate. Shaped artifacts are not raw model outputs and
must not be reported as model scores.

The most presentable current architecture result is documented in
[`04_extensions/deployable_architecture_comparison.md`](./04_extensions/deployable_architecture_comparison.md):
Qwen produces local drafts, CAP separates release / rewrite / block, the
deterministic shaper rewrites non-release drafts, and the final gate verifies
75/75 shaped release candidates. A separate Gemini 3.1 Pro presentable
comparison generated 75/75 drafts; its baseline modes had 8/45 raw gate blocks,
while CAP modes had 0/30 raw gate blocks. These are pipeline and architecture
feasibility results, not raw model scores.

For the current hard-holdout claim status, read the compact status map:
[`validation_artifacts/llm_dialogue_benchmark/hard_holdout/evaluation_status.md`](./validation_artifacts/llm_dialogue_benchmark/hard_holdout/evaluation_status.md).

## Repository structure

```text
CAP/
├── README.md                      <- you are here
├── PAPER.md                       <- single-document academic paper
├── LICENSE                        <- Apache License 2.0
├── ROADMAP.md                     <- versioned roadmap
├── CITATION.cff                   <- citation metadata
├── CONTRIBUTING.md                <- contribution guide
├── 01_foundations/                <- thesis, positioning, contracts
│   ├── thesis.md
│   ├── positioning.md
│   ├── epistemic_contract.md
│   └── primitive_experience.md
├── 02_subsystems/                 <- the six functional layers
│   ├── transition_cost.md
│   ├── observer_budget.md
│   ├── telemetry_gating.md
│   ├── operator_admissibility.md
│   ├── com_grammar.md
│   └── adjustment_dynamics.md
├── 03_validation/                 <- validation methodology + results
│   ├── methodology.md
│   ├── com_grammar.md
│   └── adjustment_layer.md
├── 04_extensions/                 <- diagnostic add-ons and positioning
│   ├── looking_glass.md
│   ├── latent_cause_reconstruction.md
│   └── comparative_positioning.md
├── 05_applications/               <- applied use cases
│   └── llm_dialogue_proxy.md
├── gold_cases/                    <- full-stack demonstrations
│   ├── README.md
│   └── anti_self_justification_loop_gold.md
├── examples/                      <- worked cases
│   ├── worked_case_client_free_edits.md
│   └── anti_self_justification_loop.md
├── spec/                          <- machine-readable schemas
│   ├── com_log_schema.json
│   └── operator_alphabet.json
└── validation_artifacts/          <- raw validation evidence
    ├── README.md
    ├── com_grammar/
    │   ├── README.md
    │   ├── case_pack.md
    │   ├── cases/                 <- 8 JSON case files
    │   └── deterministic_baseline.json
    └── adjustment_layer/
        ├── README.md
        ├── main_case_pack.md
        ├── main_cases/            <- 8 JSON case files
        ├── holdout_case_pack.md
        ├── holdout_cases/         <- 9 JSON case files
        ├── deterministic_baseline.json
        └── deterministic_holdout_baseline.json
```

## Quick start

For the full argument in one document, read **[PAPER.md](./PAPER.md)**.

For a compact external overview, read **[PITCH_ONE_PAGER.md](./PITCH_ONE_PAGER.md)**.

Run the reproducibility check from the `CAP/` directory:

```powershell
.\scripts\check_repo.ps1 -Install
.\scripts\check_repo.ps1
```

The check runs the Python tests, artifact integrity validation, and the LLM
proxy policy demo/pack.

For a deeper dive, navigate by folder:

1. Start with the **thesis**: [`01_foundations/thesis.md`](./01_foundations/thesis.md)
2. See where CAP sits among adjacent frameworks: [`01_foundations/positioning.md`](./01_foundations/positioning.md)
3. Understand the IS / IS NOT contract: [`01_foundations/epistemic_contract.md`](./01_foundations/epistemic_contract.md)
4. Walk through the six subsystems: [`02_subsystems/`](./02_subsystems/)
5. Read a worked example: [`examples/worked_case_client_free_edits.md`](./examples/worked_case_client_free_edits.md)
6. Check the validation runs: [`03_validation/`](./03_validation/)
7. Inspect the raw validation artifacts: [`validation_artifacts/`](./validation_artifacts/)
8. See how CAP applies to LLM dialogue: [`05_applications/llm_dialogue_proxy.md`](./05_applications/llm_dialogue_proxy.md) and [`examples/anti_self_justification_loop.md`](./examples/anti_self_justification_loop.md)
9. Read the full-stack Gold Case: [`gold_cases/anti_self_justification_loop_gold.md`](./gold_cases/anti_self_justification_loop_gold.md)
10. Compare CAP against prompt-only, RAG-only, validators, fine-tuning, and hybrid stacks: [`04_extensions/comparative_positioning.md`](./04_extensions/comparative_positioning.md)
11. Inspect the current deployable architecture demo: [`04_extensions/deployable_architecture_comparison.md`](./04_extensions/deployable_architecture_comparison.md)
12. Inspect the LLM dialogue proxy coverage report: [`validation_artifacts/llm_dialogue_proxy/benchmark_report.md`](./validation_artifacts/llm_dialogue_proxy/benchmark_report.md)
13. Inspect the LLM dialogue benchmark scaffold: [`validation_artifacts/llm_dialogue_benchmark/scaffold_report.md`](./validation_artifacts/llm_dialogue_benchmark/scaffold_report.md)
14. Inspect the first live LLM dialogue benchmark run: [`validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_silicon_report.md`](./validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_silicon_report.md)
15. Inspect the third-model transfer probe: [`validation_artifacts/llm_dialogue_benchmark/model_outputs/third_model_transfer_note.md`](./validation_artifacts/llm_dialogue_benchmark/model_outputs/third_model_transfer_note.md)
16. Inspect the Qwen reasoning-budget run: [`validation_artifacts/llm_dialogue_benchmark/model_outputs/qwen35_9b_run_note.md`](./validation_artifacts/llm_dialogue_benchmark/model_outputs/qwen35_9b_run_note.md)
17. Inspect the hard-holdout status map, stress track, and release-gate boundary pack: [`validation_artifacts/llm_dialogue_benchmark/hard_holdout/evaluation_status.md`](./validation_artifacts/llm_dialogue_benchmark/hard_holdout/evaluation_status.md)
18. See how to embed CAP Lite in an OpenAI-compatible or RAG pipeline: [`05_applications/integration_guide.md`](./05_applications/integration_guide.md)
19. Inspect the copyable CAP Lite middleware: [`reference/python/cap_lite.py`](./reference/python/cap_lite.py)
20. Read compact failure traces: [`trace_library/`](./trace_library/)
21. Review likely objections and current limits: [`CRITIQUES_AND_RESPONSES.md`](./CRITIQUES_AND_RESPONSES.md)
22. View text and Mermaid diagrams: [`assets/`](./assets/)

## Deployment ladder

CAP can be implemented at multiple levels:

1. **Prompt-level CAP** - telemetry tags are stored in context and audited by
   the model.
2. **Proxy-level CAP** - telemetry is parsed by an external policy layer.
3. **Full runtime CAP** - RAG confidence, transition cost, validator
   enforcement, source hierarchy, and self-audit memory are integrated into the
   system.

See [`04_extensions/comparative_positioning.md`](./04_extensions/comparative_positioning.md).

The smallest runnable integration surface is CAP Lite:

```text
messages + optional retrieval + optional prior telemetry
  -> CAP Lite policy
  -> system instruction + warnings + telemetry stub
```

See [`05_applications/integration_guide.md`](./05_applications/integration_guide.md)
and [`reference/python/cap_lite.py`](./reference/python/cap_lite.py).

## For different readers

**If you are a philosopher or cognitive scientist:**
Start with [`01_foundations/thesis.md`](./01_foundations/thesis.md) and [`01_foundations/positioning.md`](./01_foundations/positioning.md). These show what CAP claims and how it relates to Goodman, Varela, Clark, Friston, and Lieder & Griffiths.

**If you are an AI safety or LLM engineer:**
Start with [`05_applications/integration_guide.md`](./05_applications/integration_guide.md), [`reference/python/cap_lite.py`](./reference/python/cap_lite.py), [`05_applications/llm_dialogue_proxy.md`](./05_applications/llm_dialogue_proxy.md), [`examples/anti_self_justification_loop.md`](./examples/anti_self_justification_loop.md), [`gold_cases/anti_self_justification_loop_gold.md`](./gold_cases/anti_self_justification_loop_gold.md), [`trace_library/`](./trace_library/), [`validation_artifacts/llm_dialogue_benchmark/scaffold_report.md`](./validation_artifacts/llm_dialogue_benchmark/scaffold_report.md), and [`04_extensions/comparative_positioning.md`](./04_extensions/comparative_positioning.md). These show how CAP applies to RAG confidence gating, anti-sycophancy, self-audit telemetry, benchmark scaffolding, integration, failure traces, and comparative deployment trade-offs.

**If you are a reviewer or grant evaluator:**
Start with [`PITCH_ONE_PAGER.md`](./PITCH_ONE_PAGER.md), [`03_validation/methodology.md`](./03_validation/methodology.md), [`03_validation/falsifiability.md`](./03_validation/falsifiability.md), [`validation_artifacts/`](./validation_artifacts/), and [`validation_artifacts/case_design_policy.md`](./validation_artifacts/case_design_policy.md). These document what CAP has and has not shown empirically, and how public-facing benchmark cases are kept review-safe.

**If you want machine-readable specs:**
Start with [`spec/`](./spec/) and the [`reference/python/`](./reference/python/) validator. The COM-Log schema, operator alphabet, runtime telemetry, response policy, validator result, and self-audit schemas are all machine-checkable.

**If you need term definitions:**
See [`GLOSSARY.md`](./GLOSSARY.md) for all CAP terminology.

**If you want one document only:**
Read [`PAPER.md`](./PAPER.md) — the full framework in paper form.

## One-line compression

> **Legacy systems compress reality. COM parses it. LLM interpolates it. Telemetry limits it. Risk throttling protects it.**
