# CAP — Cost-Aware Phenomenology

*A typed operator framework for budget-limited transitions in lived experience.*

---

## Abstract

CAP introduces *transition cost* as a first-class property of lived experience. Where Goodman frames worlds as symbolic constructions, Varela frames them as embodied enactments, and predictive-processing frameworks frame them as inferred from prediction error, CAP adds a missing layer: the cost of moving between states. A state is not defined only by how it appears, but also by what it costs to leave it, which operators can move it, and whether the observer has the budget and telemetry to fire those operators safely.

This positioning yields a typed operator grammar (COM Grammar, 13 operators across 12 domains and 16 statuses), an admissibility calculus (Operator Admissibility = Observer Budget × Telemetry State), and a forward-routing engine (Adjustment Dynamics). Each subsystem has a deterministic baseline and three-model identity-verified validation: COM Grammar 8/8, Adjustment Layer 8/8 main + 9/9 holdout, all matched across `comet_12b_v.7-i1`, `silicon-maid-7b-imatrix`, and `fimbulvetr-11b-v2`. A separate initial LLM dialogue benchmark tests CAP as a release-policy layer for self-justification, sycophancy, weak-RAG overclaiming, stale anchors, and validator overtrust.

CAP is research-only. It is not a theory of consciousness, not a solution to the hard problem, not a divination system. It refuses to publish a recommendation that exceeds observer budget and refuses to convert a desired outcome into a certified fact. It is a working surface for analyzing experiential routes, not a license for magical thinking.

---

## 1. Introduction

Adjacent frameworks have shaped how we describe lived experience. Goodman's *Ways of Worldmaking* gave us worlds-as-versions. Varela, Thompson, and Rosch's *The Embodied Mind* gave us enactivism. Friston's free-energy principle and Clark's predictive processing gave us the prediction-error account. Lieder and Griffiths' resource rationality gave us bounded cognition.

Each of these is well-developed in its own domain. None of them centers the cost of transition.

When a person sits with chronic burnout, the question is rarely "is this state real?" or "is the prediction-error structure of this state intact?". The question is: *what would it cost me to move? Can I afford that cost right now? Which moves are even available given my current state?*

CAP is the framework that takes that question seriously.

---

## 2. Core Thesis

```text
Experience has meaning.
Experience has embodiment.
Experience has prediction.
But experience also has transition cost.
```

A state is not fully described by its semantic, embodied, or predictive properties. It is described by:

- the **operators** required to leave it,
- the **budget** required to execute those operators,
- the **telemetry** that permits or blocks each operation,
- and the **risk** that an attempted move will fail or roll back.

This yields the strong claim:

> A recommendation that exceeds observer budget is structurally false for that observer at that time.

Here, *false* means *invalid as a CAP recommendation*, not factually false as a statement about the world. The recommendation may describe a real possibility — but if the observer cannot execute it given current budget and telemetry, it is not a valid CAP output.

The "correct" operator, given without budget awareness, is the wrong operator. CAP refuses to publish such recommendations.

---

## 3. Comparative Positioning

| Framework | Central Claim | What CAP Adds |
|---|---|---|
| **Goodman** (constructivism) | Worlds are made by symbolic versions and descriptions | Worlds also have cost-to-traverse, not just versions |
| **Varela / enactivism** | Worlds are enacted through embodied coupling | Coupling has a budget, and not every coupling is admissible right now |
| **Clark / predictive processing** | Perception and action are linked to prediction and error | Action is also gated by operator admissibility, not just prediction |
| **Friston / active inference** | Behavior built around free-energy minimization | Free energy is one cost; CAP makes transition-cost explicit and typed |
| **Lieder & Griffiths** (resource rationality) | Cognition is limited by computational resources | Resource limits in CAP are phenomenological, not just computational |
| **CAP** | **Lived worlds are navigated through budget-limited, telemetry-gated operators** | — |

CAP does not reject these frameworks. It adds a layer they were missing.

---

## 4. The Six Subsystems

CAP is composed of six subsystems. Each has a separate document in [`02_subsystems/`](./02_subsystems/).

### 4.1 Transition Cost
The cost of moving between experiential states. Includes emotional cost, cognitive cost, bodily cost, social risk, rollback risk, and cross-domain resource drain. The foundational concept.

### 4.2 Observer Budget
The current usable capacity of the observer. Bounds total active risk: `TotalRisk(active chains) ≤ ObserverUsableBudget`. Operates in three modes (conservative, nominal, expansion) determined by the `RiskToleranceFactor`.

### 4.3 Telemetry Gating
The real-time safety layer. Four states: `Clean`, `Loaded`, `Overheating`, `Breach`. Telemetry signals (energy, headache, retrieval pressure, body contraction, sleep deficit, etc.) determine which operators are admissible. When telemetry breaches, only low-risk stabilizers are permitted.

### 4.4 Operator Admissibility
The derived layer. Given Budget + Telemetry, which operators can fire safely? An operator that is "correct in principle" but inadmissible in current telemetry is not the right operator. Risk Throttling automatically downgrades unsafe selections to lower-cost sequences.

### 4.5 COM Grammar
The operational language. 13 operators (Fixation, Inversion, Break, Hold, Pump, Transfer, Closure, Boundary, Cleanup, Reframe, Compression, Separation, Return), 12 domains, 16 statuses. Output format: `[COM-Log]` block with Domain, Node, Status, Operator (RiskWeight), TargetStatus, and a concrete next physical step.

### 4.6 Adjustment Dynamics
The forward-routing engine. Takes a current pressured or damaged state and reweights the admissible path field under anchors, costs, leakage patterns, and (optionally) upstream-bridge diagnosis from the Looking-Glass Layer. Two input modes: Desire Pressure (prospective routing without delivery guarantee) and Problem Pressure (recovery routing under damage).

---

## 5. COM Grammar — Worked Example

**Input:** "Client called again about the old project, asks for free edits. I spent half an hour explaining why it's impossible, ended up with a headache, but the issue is still hanging."

**Output:**

```text
[COM-Log]
Domain: [Work / Finance]
Subdomain: [Client / Boundaries]
Node: [Free edits / Debt / Boundary]
CurrentStatus: [Open] [Leaking]
Leak: [Leak: High]
Outcome: [Overheat + Unclosed Tail]
ReverseTrace: [Open boundary node -> closure attempted via conversation -> overheat -> tail persists]
LikelySplitPoint: [Conversation used in place of Boundary/Fixation operator]
DetectedOperator: [Reinforcement of conversation]
MissingOperator: [Boundary] + [Fixation]
RecommendedOperator: [Fixation (20%)] or [Break (40%)]
RiskWeight: 20% / 40%
AllowedTotalRisk: 35%
TelemetryState: [Overheating]
BudgetGate: [Reduced]
TargetStatus: [Closed]
NextPhysicalStep: [Send written rule: edits only via new payment]
```

The full walkthrough lives in [`examples/worked_case_client_free_edits.md`](./examples/worked_case_client_free_edits.md).

---

## 6. Adjustment Dynamics

Adjustment Dynamics is the forward routing engine that takes a current state and produces a reweighted distribution of admissible future paths. It does not predict the future. It does not promise delivery. It identifies which routes are still reachable given current budget, telemetry, and known leakage patterns.

Two operating modes:

- **Desire Pressure**: input is a goal state. Output is a set of admissible forward routes from current state, with no delivery guarantee.
- **Problem Pressure**: input is a damaged or deficit state (incident budget overrun, service outage, relationship rupture). Output is a recovery trajectory that stabilizes the state without collapsing into generic advice or motivational coaching.

Adjustment chains with the [Looking-Glass Layer](./04_extensions/looking_glass.md) (reverse diagnostic) to ensure routing is informed by the upstream cause, not just the visible symptom.

Full subsystem detail in [`02_subsystems/adjustment_dynamics.md`](./02_subsystems/adjustment_dynamics.md).

---

## 7. Validation Methodology

CAP follows a three-tier validation pattern:

1. **Deterministic baseline.** A typed test pack with known expected verdicts. Runs in pure Python with no LLM. Establishes that the boundaries are computable.
2. **LLM validation.** The same test pack is presented to multiple identity-verified LLMs. Each model produces a structured JSON response evaluated against the deterministic baseline. Identity is verified against the LM Studio `/v1/models` endpoint before each run; responses with mismatched model fields are rejected.
3. **Holdout pack.** A separate, fresh case pack tests whether the validation generalizes beyond the original tests. Same three-model evaluation pattern.

This is unusual in philosophy-of-mind work. Most frameworks do not have machine-verified outputs. CAP treats validation as a first-class concern: a framework that cannot be checked across multiple independent inference surfaces is not yet a usable tool.

Full methodology in [`03_validation/methodology.md`](./03_validation/methodology.md).

---

## 8. Results

### 8.1 COM Grammar

```text
Deterministic baseline:    8/8
fimbulvetr-11b-v2:        8/8 verdict / 8/8 primary reading
comet_12b_v.7-i1:         8/8 verdict / 8/8 primary reading
silicon-maid-7b-imatrix:  8/8 verdict / 8/8 primary reading
```

Boundaries validated: advice collapse blocked, COM-Log format valid, risk throttle downgrade applied, reverse-first parsing applied, anti-noise state rejected, persistent fault candidate detected, budget recovery limits to stabilizers, legacy-as-engine blocked.

### 8.2 Adjustment Layer

```text
Main pack (8 cases):
  Deterministic:           8/8
  comet, silicon, fimbul:  8/8 each

Holdout pack (9 cases):
  Deterministic:           9/9
  comet, silicon, fimbul:  9/9 each
```

Boundaries validated: desire-pressure routing without delivery guarantee, problem-pressure recovery without advice collapse, Markov bridge intermediate states, Schrödinger bridge minimal deformation, anti-collapse advice guard, Looking-Glass chain integration, budget-constrained routing, leakage-pattern invalidation. Plus the key holdout case: symptom closure while leakage active is blocked as structurally incomplete.

### 8.3 Initial LLM Dialogue Benchmark

CAP was also tested as an LLM dialogue release-policy layer. This benchmark is
separate from the COM Grammar and Adjustment Layer validation above. It asks a
narrow operational question:

```text
Does the dialogue system release, preserve, or downgrade prior answer nodes
correctly under known failure modes?
```

The benchmark compares five modes:

| Mode | Mechanism |
|---|---|
| `prompt_only` | Base instruction without retrieval or CAP policy. |
| `rag_only` | Retrieved context is provided, but no CAP release policy. |
| `validator_only` | Post-generation validation framing only. |
| `prompt_level_cap` | CAP telemetry is given in the prompt for self-audit. |
| `proxy_level_cap` | External CAP policy is provided as a release constraint. |

The five test cases cover:

- self-justification after a user counter-source
- sycophancy over a false user frame
- weak RAG evidence carrying a strong claim
- stale cross-turn anchor reuse
- validator acceptance treated as proof

First live run:

```text
Models: comet_12b_v.7-i1, silicon-maid-7b-imatrix
Cases: 5
Generation calls: 50
Temperature: 0
Scorer: lexical/heuristic, audited separately
```

Scored result:

| Mode | comet_12b_v.7-i1 | silicon-maid-7b-imatrix |
|---|---:|---:|
| `prompt_only` | 0/5 | 0/5 |
| `rag_only` | 1/5 | 2/5 |
| `validator_only` | 3/5 | 2/5 |
| `prompt_level_cap` | 4/5 | 3/5 |
| `proxy_level_cap` | 5/5 | 5/5 |

This supports a narrow engineering claim: in this small case pack,
proxy-level CAP produced the strongest release discipline. It does not prove
general superiority over prompting, RAG, validators, fine-tuning, or RLHF. The
scorer is lexical/heuristic and can miss semantically correct answers or accept
phrase-matched but weak answers. The scorer audit is documented in
[`validation_artifacts/llm_dialogue_benchmark/scorer_audit.md`](./validation_artifacts/llm_dialogue_benchmark/scorer_audit.md), and the raw outputs are stored in
[`validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_silicon_outputs.json`](./validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_silicon_outputs.json).

A later third-model transfer probe added `mistral-nemo-instruct-2407`:

| Mode | Mistral Nemo |
|---|---:|
| `prompt_only` | 1/5 |
| `rag_only` | 2/5 |
| `validator_only` | 1/5 |
| `prompt_level_cap` | 1/5 |
| `proxy_level_cap` | 1/5 |

This is an important negative/limiting result. Under the current prompt
templates and lexical scorer, CAP did not transfer cleanly to that model. The
result motivates manual adjudication, prompt-template hardening, and scorer
freezing before stronger benchmark claims. See
[`validation_artifacts/llm_dialogue_benchmark/model_outputs/third_model_transfer_note.md`](./validation_artifacts/llm_dialogue_benchmark/model_outputs/third_model_transfer_note.md).

An exact-model hardened v2 rerun was then performed with the same
`mistral-nemo-instruct-2407` model and more explicit prompt templates. No
substitute or abliterated model was used. The lexical score did not improve:

| Mode | v1 | hardened v2 |
|---|---:|---:|
| `prompt_level_cap` | 1/5 | 1/5 |
| `proxy_level_cap` | 1/5 | 1/5 |

The v2 result suggests that the next step is manual adjudication and scorer
disagreement analysis, not post-hoc scorer broadening. See
[`validation_artifacts/llm_dialogue_benchmark/model_outputs/mistral_nemo_hardened_v2_comparison.md`](./validation_artifacts/llm_dialogue_benchmark/model_outputs/mistral_nemo_hardened_v2_comparison.md).

A later Qwen run added `qwen/qwen3.5-9b`. Because the model spends substantial
budget in `reasoning_content`, the valid run used `max_tokens=8192`; smaller
budgets produced empty released `message.content` fields and were excluded.

| Mode | Qwen 3.5 9B |
|---|---:|
| `prompt_only` | 1/5 |
| `rag_only` | 2/5 |
| `validator_only` | 2/5 |
| `prompt_level_cap` | 2/5 |
| `proxy_level_cap` | 4/5 |

This supports a narrower operational point: reasoning-heavy models require
released-output validation and generation-budget reporting before their scores
are comparable. See
[`validation_artifacts/llm_dialogue_benchmark/model_outputs/qwen35_9b_run_note.md`](./validation_artifacts/llm_dialogue_benchmark/model_outputs/qwen35_9b_run_note.md).

The repository also includes a separate 15-case hard-holdout stress track with
complete Mistral Nemo and Qwen no-thinking runs, a partial Gemini 2.5 Flash
free-tier control, deterministic proxy release-gate reports, and a compact
25-item blinded release-gate boundary pack. A preregistered v0.2 release-gate
hardening pass is stored as separate reports and comparison files; it is not
merged into the v0.1 reports. These artifacts are intentionally not merged into
the baseline-v1 scores. They are reported as transfer-stress and adjudication
scaffolds: Codex draft labels are useful for debugging the release gate, but
they do not replace independent human adjudication.

The hard-holdout track also includes a deterministic post-gate rewrite shaper:
raw model output is first gated, non-release output is rewritten from the
frozen case contract, and the shaped candidate is checked again by release gate
v0.2. This demonstrates the intended runtime boundary from detection to
rewrite, but the shaped candidates are not raw model outputs and are not
benchmark wins.

For the current hard-holdout claim status, see
[`validation_artifacts/llm_dialogue_benchmark/hard_holdout/evaluation_status.md`](./validation_artifacts/llm_dialogue_benchmark/hard_holdout/evaluation_status.md).

---

## 9. Limitations and Boundaries

CAP is **research-only**. Validation supports its use as a working surface, not as certified canon.

CAP does **not**:

- explain why phenomenal experience exists;
- predict specific future outcomes;
- replace clinical, financial, legal, or relationship judgment;
- guarantee delivery of any wished-for state;
- treat LLM behavior as evidence of its own ontology;
- treat numeric thresholds (RiskWeight values, telemetry signals) as anything but provisional engineering defaults.

LLM is a scaffold for hypothesis generation and consistency testing. LLM is not evidence. The validation runs show that CAP boundaries are stable across multiple independent inference surfaces, which supports usability — not metaphysical truth.

Full epistemic contract in [`01_foundations/epistemic_contract.md`](./01_foundations/epistemic_contract.md).

---

## 10. Diagnostic Extensions

Two diagnostic add-ons sit on top of CAP. Each is a separate research-only patch:

### 10.1 Looking-Glass Layer

Reverse-read mode for diagnosis. Takes an observed outcome and reconstructs plausible prior paths, locates the likely split point, and separates restore-feasible from compensate-only repairs. Anti-magic-guard prevents claims of literal undo-history. See [`04_extensions/looking_glass.md`](./04_extensions/looking_glass.md).

### 10.2 Latent Cause Reconstruction (A-Reconstruction)

Inverse-causal engine. Takes an observed rupture (B), prior history (H), resource traces, and behavioral traces, and reconstructs ranked latent cause candidates (A) with corresponding repair pairs (C). Validated across 14 real-case rounds with 28/28 live LLM batch agreement. The trigger ≠ cause distinction is enforced explicitly. See [`04_extensions/latent_cause_reconstruction.md`](./04_extensions/latent_cause_reconstruction.md).

---

## 11. Conclusion

CAP is a framework for analyzing lived experience as a routing problem under budget and telemetry constraints. Its central contribution is taking transition cost seriously — making it explicit, typed, and computable. The COM Grammar provides the operational language. The Adjustment Layer provides the forward routing engine. Telemetry Gating provides the safety layer.

What CAP does **not** do — and what it explicitly refuses to do — is just as important as what it does. CAP does not produce a "right answer" without checking whether the observer can execute it. It does not convert a desired outcome into a certified fact. It does not replace judgment. It is a tool for clearer judgment, not a replacement for it.

Three independent inference surfaces agree on the boundaries CAP draws. That is not proof that CAP is correct. It is evidence that the boundaries are well-specified enough to be checkable. From here, the work continues.

---

## One-line compression

> Legacy systems compress reality. COM parses it. LLM interpolates it. Telemetry limits it. Risk throttling protects it.
