# Deployable Architecture Comparison

This note summarizes the current hard-holdout result as an architecture
comparison, not as a raw model leaderboard.

The practical finding is:

```text
Raw local LLM outputs are not reliable enough for direct release.
CAP makes local LLM drafts usable by separating generation from release control:
draft -> release gate -> deterministic rewrite -> final gate.
```

## Scope

This is a pipeline feasibility result over the 15-case hard-holdout pack. It is
not an external benchmark and it is not a human-adjudicated quality score.

The shaped outputs below are deterministic case-contract rewrites. They are not
raw model outputs.

## Architecture Result

The strongest local architecture currently observed is:

```text
Qwen presentable draft
-> release_gate v0.2
-> deterministic rewrite shaper
-> final release_gate v0.2
```

The Qwen run used:

```text
model        = atlas/qwen3.5-9b-no-thinking
case pack    = hard_holdout_15case
template dir = prompt_templates_presentable
temperature  = 0
max tokens   = 32768
```

## Raw Gate View

Before shaping, the deterministic release gate separates raw model outputs into
three buckets:

- `release`: ready under the case contract;
- `rewrite_required`: directionally usable, but missing explicit release
  evidence or user-facing shape;
- `block`: a non-contextualized failure signal remains.

| Qwen presentable mode | Raw release | Rewrite required | Blocked | Practical reading |
|---|---:|---:|---:|---|
| `prompt_only` | 0/15 | 13/15 | 2/15 | Baseline drafts are mostly non-release. |
| `rag_only` | 3/15 | 10/15 | 2/15 | Retrieval helps, but does not solve release control. |
| `validator_only` | 2/15 | 11/15 | 2/15 | Validator framing catches some issues but still overtrusts. |
| `prompt_level_cap` | 5/15 | 10/15 | 0/15 | Best raw local lane: no blocking failures, many rewrites. |
| `proxy_level_cap` | 1/15 | 13/15 | 1/15 | Strong policy awareness, but too much internal jargon leaks. |

## Final Pipeline View

After deterministic shaping and a final `release_gate v0.2` check:

| Qwen presentable mode | Final release | Rewrite required | Blocked |
|---|---:|---:|---:|
| `prompt_only` | 15/15 | 0/15 | 0/15 |
| `rag_only` | 15/15 | 0/15 | 0/15 |
| `validator_only` | 15/15 | 0/15 | 0/15 |
| `prompt_level_cap` | 15/15 | 0/15 | 0/15 |
| `proxy_level_cap` | 15/15 | 0/15 | 0/15 |

Shaper intervention:

| Shaper action | Count |
|---|---:|
| `pass_release` | 11/75 |
| `rewrite_from_case_contract` | 64/75 |

## External CAP-Only Control

The same deployable boundary was also tested on an external Gemini CAP-only
lane:

```text
Gemini 3.1 Pro presentable CAP draft
-> release_gate v0.2
-> deterministic rewrite shaper
-> final release_gate v0.2
```

The Gemini run used:

```text
model        = models/gemini-3.1-pro-preview
case pack    = hard_holdout_15case
template dir = prompt_templates_presentable
modes        = prompt_level_cap, proxy_level_cap
temperature  = 0
max tokens   = 8192
```

This started as a CAP-only external control and was then extended into a
five-mode presentable comparison.

The non-CAP Gemini modes produced:

| Gemini 3.1 Pro presentable mode | Raw release | Rewrite required | Blocked | Practical reading |
|---|---:|---:|---:|---|
| `prompt_only` | 0/15 | 12/15 | 3/15 | Clean format, but several direct-release blockers remain. |
| `rag_only` | 2/15 | 10/15 | 3/15 | Retrieval helps, but does not eliminate release blockers. |
| `validator_only` | 1/15 | 12/15 | 2/15 | Validator framing helps, but still overtrusts scoped checks. |

Raw gate view:

| Gemini 3.1 Pro presentable mode | Raw release | Rewrite required | Blocked | Practical reading |
|---|---:|---:|---:|---|
| `prompt_level_cap` | 5/15 | 10/15 | 0/15 | Strong raw CAP lane: no blocks, many explicit-signal rewrites. |
| `proxy_level_cap` | 0/15 | 15/15 | 0/15 | Analysis is usable, but visible release-policy jargon requires shaping. |

The key external comparison is:

| Group | Raw release | Rewrite required | Blocked |
|---|---:|---:|---:|
| Baseline modes | 3/45 | 34/45 | 8/45 |
| CAP modes | 5/30 | 25/30 | 0/30 |

After deterministic shaping and final gate:

| Gemini 3.1 Pro presentable mode | Final release | Rewrite required | Blocked |
|---|---:|---:|---:|
| `prompt_only` | 15/15 | 0/15 | 0/15 |
| `rag_only` | 15/15 | 0/15 | 0/15 |
| `validator_only` | 15/15 | 0/15 | 0/15 |
| `prompt_level_cap` | 15/15 | 0/15 | 0/15 |
| `proxy_level_cap` | 15/15 | 0/15 | 0/15 |

Shaper intervention:

| Group | Pass release | Rewrite from case contract | Final release |
|---|---:|---:|---:|
| Baseline modes | 3/45 | 42/45 | 45/45 |
| CAP modes | 5/30 | 25/30 | 30/30 |
| All Gemini modes | 8/75 | 67/75 | 75/75 |

Correct:

```text
Gemini 3.1 Pro produced 75/75 presentable drafts. Under release_gate v0.2, the
baseline modes had 8 blocking raw outputs while CAP modes had 0 blocking raw
outputs. After deterministic shaping, all 75 candidates passed the final gate.
```

Incorrect:

```text
Gemini solved the hard-holdout benchmark.
```

The Gemini result is useful because it shows that the same boundary is not
limited to local LM Studio models. It still remains a pipeline result, not a
raw model leaderboard.

## How To Report This

Correct:

```text
The Qwen + CAP gate/rewrite pipeline produced 75/75 deterministic release
candidates after shaping.
```

Incorrect:

```text
Qwen solved 75/75 hard-holdout cases.
```

The difference matters. The result shows that CAP can turn weak local-model
drafts into controlled release candidates through a deterministic boundary. It
does not show that the raw model solved the cases.

## Why This Is More Presentable

The comparison is useful for sponsors, grant reviewers, and engineering teams
because it shows a deployable system boundary:

| Layer | Responsibility |
|---|---|
| Local LLM | Produce a draft response. |
| CAP release gate | Decide whether the draft is release, rewrite, or block. |
| Rewrite shaper | Convert non-release drafts into case-contract release candidates. |
| Final gate | Verify the rewritten candidate before release. |

This is the central architecture claim:

```text
CAP is not a prompt trick. It is a release-control architecture:
it measures when a model output is not safe to preserve as an anchor,
routes it through rewrite when needed, and verifies the final candidate before
release.
```

## Current Best Reading

The current local result supports:

```text
CAP can expose release-boundary failures, classify local LLM drafts, and
convert non-release outputs into deterministic release candidates.
```

It does not yet support:

```text
CAP outperforms prompt-only, RAG-only, validator-only, fine-tuning, or RLHF on
external human-rated benchmarks.
```

The next evidence step is human or independent model adjudication over a
sample of shaped release candidates.

## Artifacts

- [`../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/presentable_demo_run_note.md`](../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/presentable_demo_run_note.md)
- [`../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_presentable_demo_gate_v02.md`](../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_presentable_demo_gate_v02.md)
- [`../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_presentable_shaped_v02_summary.md`](../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_presentable_shaped_v02_summary.md)
- [`../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_presentable_shaped_v02_gate.md`](../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_presentable_shaped_v02_gate.md)
- [`../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/gemini_31_pro_presentable_full_comparison.md`](../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/gemini_31_pro_presentable_full_comparison.md)
- [`../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/gemini_31_pro_presentable_baseline_modes_gate_v02.md`](../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/gemini_31_pro_presentable_baseline_modes_gate_v02.md)
- [`../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/gemini_31_pro_presentable_cap_gate_v02.md`](../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/gemini_31_pro_presentable_cap_gate_v02.md)
- [`../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/gemini_31_pro_presentable_cap_shaped_v02_summary.md`](../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/gemini_31_pro_presentable_cap_shaped_v02_summary.md)
- [`../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/gemini_31_pro_presentable_cap_shaped_v02_gate.md`](../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/gemini_31_pro_presentable_cap_shaped_v02_gate.md)
