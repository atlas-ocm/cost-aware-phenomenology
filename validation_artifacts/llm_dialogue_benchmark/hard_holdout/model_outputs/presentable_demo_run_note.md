# Presentable Demo Run Note

Status: complete local presentation/demo run, not a frozen benchmark lane.

This note records the first hard-holdout run using
[`prompt_templates_presentable/`](../../prompt_templates_presentable/). These
templates add visible professional Markdown sections such as `## Assessment`,
`## Evidence Check`, `## CAP Release Decision`, and `## Final Response`.

Because this changes the prompt surface, these outputs must not be merged with
the frozen `prompt_templates/` or `prompt_templates_hardened_v2/` benchmark
scores. Treat the lexical scores below as diagnostic shape checks only.

## Run Configuration

Common settings:

```text
case_dir     = validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases
template_dir = validation_artifacts/llm_dialogue_benchmark/prompt_templates_presentable
base_url     = http://127.0.0.1:1234/v1
temperature  = 0
write_partial = true
resume        = true
```

Model-specific settings:

| Model | Output JSON | Max tokens | Generated records | Empty outputs |
|---|---|---:|---:|---:|
| `atlas/qwen3.5-9b-no-thinking` | [`qwen35_9b_presentable_demo_outputs.json`](./qwen35_9b_presentable_demo_outputs.json) | 32768 | 75/75 | 0 |
| `mistral-nemo-instruct-2407` | [`mistral_nemo_presentable_demo_outputs.json`](./mistral_nemo_presentable_demo_outputs.json) | 8192 | 75/75 | 0 |

External CAP-only settings:

| Model | Output JSON | Modes | Max tokens | Generated records | Empty outputs |
|---|---|---|---:|---:|---:|
| `models/gemini-3.1-pro-preview` | [`gemini_31_pro_presentable_cap_outputs.json`](./gemini_31_pro_presentable_cap_outputs.json) | `prompt_level_cap`, `proxy_level_cap` | 8192 | 30/30 | 0 |

External baseline-mode comparison settings:

| Model | Output JSON | Modes | Max tokens | Generated records | Empty outputs |
|---|---|---|---:|---:|---:|
| `models/gemini-3.1-pro-preview` | [`gemini_31_pro_presentable_baseline_modes_outputs.json`](./gemini_31_pro_presentable_baseline_modes_outputs.json) | `prompt_only`, `rag_only`, `validator_only` | 8192 | 45/45 | 0 |

## Heuristic Diagnostic Scores

Qwen presentable diagnostic report:
[`qwen35_9b_presentable_demo_report.md`](./qwen35_9b_presentable_demo_report.md)

| Mode | Passed | Failed |
|---|---:|---:|
| prompt_only | 0/15 | 15/15 |
| rag_only | 1/15 | 14/15 |
| validator_only | 0/15 | 15/15 |
| prompt_level_cap | 2/15 | 13/15 |
| proxy_level_cap | 2/15 | 13/15 |

Mistral presentable diagnostic report:
[`mistral_nemo_presentable_demo_report.md`](./mistral_nemo_presentable_demo_report.md)

| Mode | Passed | Failed |
|---|---:|---:|
| prompt_only | 0/15 | 15/15 |
| rag_only | 1/15 | 14/15 |
| validator_only | 3/15 | 12/15 |
| prompt_level_cap | 3/15 | 12/15 |
| proxy_level_cap | 2/15 | 13/15 |

## Release-Gate v0.2 Diagnostic View

The deterministic release gate is a more useful diagnostic for this lane than
the lexical pass/fail score, because it separates already releasable outputs
from outputs that only need a rewrite.

Qwen presentable gate report:
[`qwen35_9b_presentable_demo_gate_v02.md`](./qwen35_9b_presentable_demo_gate_v02.md)

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| prompt_only | 0/15 | 13/15 | 2/15 |
| rag_only | 3/15 | 10/15 | 2/15 |
| validator_only | 2/15 | 11/15 | 2/15 |
| prompt_level_cap | 5/15 | 10/15 | 0/15 |
| proxy_level_cap | 1/15 | 13/15 | 1/15 |

Mistral presentable gate report:
[`mistral_nemo_presentable_demo_gate_v02.md`](./mistral_nemo_presentable_demo_gate_v02.md)

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| prompt_only | 0/15 | 13/15 | 2/15 |
| rag_only | 1/15 | 13/15 | 1/15 |
| validator_only | 1/15 | 12/15 | 2/15 |
| prompt_level_cap | 3/15 | 10/15 | 2/15 |
| proxy_level_cap | 0/15 | 13/15 | 2/15 |

This supports a practical feasibility conclusion:

```text
Qwen can produce an acceptable draft stream for the hard-holdout cases when CAP
prompting is used and a release gate is allowed to rewrite non-final outputs.
Mistral is usable for demonstrations, but still emits blocking failures in
CAP modes and should not be trusted as a raw release candidate generator.
```

The most promising local raw-draft lane is therefore:

```text
Qwen presentable prompt_level_cap -> release_gate v0.2 -> rewrite shaper -> final gate
```

Mistral remains useful as a weaker local demonstration lane, but it should be
reported as more rewrite-dependent than Qwen.

The main remaining blockers are not formatting problems. They are missing or
implicit release signals:

- frame correction for false user frames;
- explicit evidence calibration;
- explicit validator-scope review;
- explicit revalidation of stale anchors;
- removal of CAP/internal release-policy jargon from final user-facing text.

## Qwen Gate-to-Rewrite Pipeline Result

The Qwen presentable outputs were passed through the deterministic rewrite
shaper and then rechecked with `release_gate v0.2`.

Shaper artifacts:

- [`qwen35_9b_presentable_shaped_v02_outputs.json`](./qwen35_9b_presentable_shaped_v02_outputs.json)
- [`qwen35_9b_presentable_shaped_v02_summary.md`](./qwen35_9b_presentable_shaped_v02_summary.md)
- [`qwen35_9b_presentable_shaped_v02_gate.md`](./qwen35_9b_presentable_shaped_v02_gate.md)

Shaper summary:

| Shaper action | Count |
|---|---:|
| `pass_release` | 11 |
| `rewrite_from_case_contract` | 64 |

Final gate result after shaping:

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| prompt_only | 15/15 | 0/15 | 0/15 |
| rag_only | 15/15 | 0/15 | 0/15 |
| validator_only | 15/15 | 0/15 | 0/15 |
| prompt_level_cap | 15/15 | 0/15 | 0/15 |
| proxy_level_cap | 15/15 | 0/15 | 0/15 |

This is a pipeline-boundary result, not a model-performance result:

```text
The local model produced complete drafts; the deterministic CAP shaper converted
non-release drafts into case-contract release candidates; the final gate then
accepted all shaped candidates.
```

Do not report this as:

```text
Qwen solved 75/75 hard-holdout cases.
```

Report it as:

```text
The Qwen + CAP gate/rewrite pipeline produced 75/75 deterministic release
candidates after shaping.
```

## Mistral Gate-to-Rewrite Pipeline Result

The Mistral presentable outputs were also passed through the deterministic
rewrite shaper and then rechecked with `release_gate v0.2`.

Shaper artifacts:

- [`mistral_nemo_presentable_shaped_v02_outputs.json`](./mistral_nemo_presentable_shaped_v02_outputs.json)
- [`mistral_nemo_presentable_shaped_v02_summary.md`](./mistral_nemo_presentable_shaped_v02_summary.md)
- [`mistral_nemo_presentable_shaped_v02_gate.md`](./mistral_nemo_presentable_shaped_v02_gate.md)

Shaper summary:

| Shaper action | Count |
|---|---:|
| `pass_release` | 5 |
| `rewrite_from_case_contract` | 70 |

Final gate result after shaping:

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| prompt_only | 15/15 | 0/15 | 0/15 |
| rag_only | 15/15 | 0/15 | 0/15 |
| validator_only | 15/15 | 0/15 | 0/15 |
| prompt_level_cap | 15/15 | 0/15 | 0/15 |
| proxy_level_cap | 15/15 | 0/15 | 0/15 |

This is a pipeline-boundary result, not a model-performance result:

```text
The local model produced complete drafts; the deterministic CAP shaper converted
non-release drafts into case-contract release candidates; the final gate then
accepted all shaped candidates.
```

Do not report this as:

```text
Mistral solved 75/75 hard-holdout cases.
```

Report it as:

```text
The Mistral + CAP gate/rewrite pipeline produced 75/75 deterministic release
candidates after shaping, with a heavier rewrite load than Qwen.
```

## Gemini 3.1 Pro Full Mode Comparison

Gemini 3.1 Pro was also run across the three non-CAP modes, giving a complete
five-mode presentable comparison over 75/75 generated records.

Summary report:

- [`gemini_31_pro_presentable_full_comparison.md`](./gemini_31_pro_presentable_full_comparison.md)

Raw release-gate v0.2 comparison:

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| prompt_only | 0/15 | 12/15 | 3/15 |
| rag_only | 2/15 | 10/15 | 3/15 |
| validator_only | 1/15 | 12/15 | 2/15 |
| prompt_level_cap | 5/15 | 10/15 | 0/15 |
| proxy_level_cap | 0/15 | 15/15 | 0/15 |

The key comparison is:

```text
baseline modes: 8/45 raw blocks
CAP modes:      0/30 raw blocks
```

After deterministic shaping, all five modes reached final `release`, but this
is a pipeline result and not raw model performance.

## Gemini 3.1 Pro CAP-Only Pipeline Result

Gemini 3.1 Pro was run as an external CAP-only control using the same
presentable templates, limited to `prompt_level_cap` and `proxy_level_cap`.
This section is preserved as the CAP-only slice of the full comparison above.

Raw Gemini artifacts:

- [`gemini_31_pro_presentable_cap_outputs.json`](./gemini_31_pro_presentable_cap_outputs.json)
- [`gemini_31_pro_presentable_cap_report.md`](./gemini_31_pro_presentable_cap_report.md)
- [`gemini_31_pro_presentable_cap_gate_v02.md`](./gemini_31_pro_presentable_cap_gate_v02.md)

Raw release-gate v0.2 result:

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| prompt_level_cap | 5/15 | 10/15 | 0/15 |
| proxy_level_cap | 0/15 | 15/15 | 0/15 |

The raw outputs had no blocking failures, but most items still needed explicit
release-signal or user-facing shape rewrites.

Shaper artifacts:

- [`gemini_31_pro_presentable_cap_shaped_v02_outputs.json`](./gemini_31_pro_presentable_cap_shaped_v02_outputs.json)
- [`gemini_31_pro_presentable_cap_shaped_v02_summary.md`](./gemini_31_pro_presentable_cap_shaped_v02_summary.md)
- [`gemini_31_pro_presentable_cap_shaped_v02_gate.md`](./gemini_31_pro_presentable_cap_shaped_v02_gate.md)

Shaper summary:

| Shaper action | Count |
|---|---:|
| `pass_release` | 5 |
| `rewrite_from_case_contract` | 25 |

Final gate result after shaping:

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| prompt_level_cap | 15/15 | 0/15 | 0/15 |
| proxy_level_cap | 15/15 | 0/15 | 0/15 |

Report this as:

```text
The Gemini 3.1 Pro + CAP gate/rewrite pipeline produced 30/30 deterministic
CAP-mode release candidates after shaping.
```

Do not report this as a full Gemini benchmark win or as raw model performance.

## Interpretation

The run supports a narrow operational claim:

```text
Qwen and Mistral can both produce complete, non-empty, professionally structured
hard-holdout outputs under the presentable prompt lane.
```

It also supports a pipeline claim:

```text
Qwen and Mistral presentable drafts can both be converted into 75/75
deterministic release candidates by the CAP gate/rewrite layer, but Mistral is
more rewrite-dependent.
```

It does not support a benchmark claim:

```text
CAP improved model performance under the frozen hard-holdout scorer.
```

The low lexical scores mainly show that the existing heuristic scorer remains
strictly tied to the frozen case-contract signals and does not evaluate
presentation quality or semantic adequacy of the visible Markdown sections.

Use these files for demos, qualitative review, and manual adjudication
preparation. Do not cite them as a leaderboard result.
