# CAP One-Pager

## Problem

LLM systems often preserve bad intermediate answers as anchors. Once a weak
claim appears in the dialogue, later turns can defend it, inflate it, or treat a
user correction as a threat. Prompting, RAG, validators, and fine-tuning all
help, but none of them alone gives a clear release policy for whether a prior
node should still be trusted.

## Core Idea

CAP, Cost-Aware Phenomenology, treats each answer or state transition as a
typed node with telemetry:

- retrieval confidence
- claim strength
- entropy
- transition cost
- validator action
- source hierarchy

The system does not ask only "what should the model say?". It asks "is this
node allowed to be reused, defended, released, downgraded, or replaced?".

## Why This Is Not Just Prompting

Prompting changes what the model is asked to do.

Fine-tuning changes what the model tends to do.

CAP changes what the system is allowed to release and preserve as an anchor.

That makes CAP an algorithmic governance layer rather than another instruction
style.

## Current Prototype

The repository contains:

- typed operator grammar and schemas
- deterministic validation artifacts for COM Grammar and Adjustment Layer
- LLM dialogue proxy application notes
- a full anti-self-justification Gold Case
- a copyable CAP Lite middleware and integration guide
- a compact Trace Library for LLM dialogue failure modes
- a runnable dependency-free proxy policy demo
- an 8-case deterministic LLM dialogue proxy policy pack
- a 5-case x 5-mode LLM dialogue benchmark scaffold
- an OpenAI-compatible live output generator for that benchmark
- a Windows reproducibility script
- a GitHub Actions workflow for public verification
- Mermaid / ASCII diagrams and a critiques-and-responses note

Current local check:

```text
unit/schema/policy tests: 47 passing
artifact integrity: 0 issues
LLM proxy policy pack: 8/8
LLM benchmark scaffold: generated from synthetic fixture outputs
Initial live LLM benchmark: proxy-level CAP 5/5 on comet and silicon
Third-model transfer probe: Mistral Nemo exposed prompt/scorer sensitivity
Exact-model hardened v2 rerun: lexical CAP-mode score unchanged
Qwen reasoning-budget run: proxy-level CAP 4/5 with max_tokens=8192
Hard-holdout stress track: complete Mistral + Qwen no-thinking runs, Gemini 2.5 Flash paid 45/45 three-mode control
Release-gate boundary pack: 25 blinded items, Codex draft labels only
Release-gate v0.2: preregistered hardening report, not a benchmark win
Post-gate rewrite shaper: deterministic release-candidate artifacts, not raw model scores
Deployable architecture demo: Qwen + CAP gate/rewrite pipeline produced 75/75 shaped release candidates
External Gemini comparison: Gemini 3.1 Pro presentable 5-mode run; CAP raw blocks 0/30 vs baseline raw blocks 8/45
```

The exact test count may grow; the invariant is that `scripts/check_repo.ps1`
must pass.

## Example Failure Mode

A model makes a strong claim over weak retrieval evidence. The user later
challenges it. A normal assistant may defend the old answer or apologize while
quietly preserving the same anchor.

CAP marks the prior node as deprecated:

```text
forbid: defend_previous_claim
require: recheck_before_answer, downgrade_claim_strength, validator_review
release_action: rewrite_or_retrieve
```

This turns a conversational correction into a machine-checkable release
decision.

## Target Use

CAP is most relevant for:

- RAG assistants that must match claim strength to evidence
- long-running agents that carry cross-turn memory
- systems where sycophancy and self-justification are recurring risks
- safety/reliability teams that need auditable response-policy traces

## Research Status

CAP is research-only. Current artifacts show machine-checkable structure,
deterministic policy behavior, repeatable validation packs, an initial small
live LLM benchmark, transfer-stress runs that exposed prompt and scorer
sensitivity, and a Qwen run showing that reasoning-heavy models need larger
generation budgets and released-output checks. The hard-holdout and
release-gate artifacts are adjudication scaffolds, not final benchmark claims.
The deterministic rewrite shaper demonstrates a gate-to-rewrite pipeline
boundary; shaped outputs are not raw model outputs and should not be read as
model performance. The most presentable local architecture result is that Qwen
drafts plus CAP gate/rewrite/final-gate control produced 75/75 deterministic
release candidates after shaping. A separate Gemini 3.1 Pro presentable
five-mode comparison produced 75/75 drafts; the raw release gate found 8/45
baseline blocks and 0/30 CAP-mode blocks.
These artifacts do not prove real-world deployment safety or broad superiority
over other approaches.

For the current hard-holdout claim status, see
[`validation_artifacts/llm_dialogue_benchmark/hard_holdout/evaluation_status.md`](./validation_artifacts/llm_dialogue_benchmark/hard_holdout/evaluation_status.md).

## Next Work

The integration surface, benchmark scaffold, case pack, modes, scorer, and
report format are now in place. The first live two-model run, transfer probes,
hard-holdout stress track, and release-gate boundary pack show where the
prompt/scorer stack needs preregistered gate changes and independent
adjudication before further tuning. After that, expand with more models and
cases comparing:

- prompt-only
- RAG-only
- validator-only
- prompt-level CAP
- proxy-level CAP

Primary metrics should be claim/evidence calibration, sycophancy resistance,
self-justification prevention, stale-anchor blocking, and auditability.
