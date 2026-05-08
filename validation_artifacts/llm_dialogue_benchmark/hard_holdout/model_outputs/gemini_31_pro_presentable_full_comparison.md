# Gemini 3.1 Pro Presentable Full Comparison

Status: complete five-mode presentable comparison over the 15-case hard-holdout
pack.

This is not a frozen benchmark lane. It uses
[`prompt_templates_presentable/`](../../prompt_templates_presentable/), which
adds visible Markdown structure and therefore changes the prompt surface. Treat
the result as a presentation and architecture-comparison artifact.

## Run Scope

```text
model        = models/gemini-3.1-pro-preview
case pack    = hard_holdout_15case
template dir = prompt_templates_presentable
temperature  = 0
max tokens   = 8192
```

Outputs:

| Mode group | Output file | Generated records |
|---|---|---:|
| Baseline modes | [`gemini_31_pro_presentable_baseline_modes_outputs.json`](./gemini_31_pro_presentable_baseline_modes_outputs.json) | 45/45 |
| CAP modes | [`gemini_31_pro_presentable_cap_outputs.json`](./gemini_31_pro_presentable_cap_outputs.json) | 30/30 |

Total generated records: `75/75`.

Provider-internal `thought_signature` fields are redacted in saved raw
responses as `[redacted_provider_internal]`.

## Raw Heuristic Score

The lexical scorer is useful as a strict diagnostic, not as a human-quality
score.

| Mode | Passed | Failed |
|---|---:|---:|
| `prompt_only` | 0/15 | 15/15 |
| `rag_only` | 1/15 | 14/15 |
| `validator_only` | 0/15 | 15/15 |
| `prompt_level_cap` | 4/15 | 11/15 |
| `proxy_level_cap` | 5/15 | 10/15 |

Reading: CAP modes have better raw lexical coverage, but the raw score is still
strict and not enough by itself to call the outputs release-ready.

## Raw Release-Gate v0.2 View

This is the most useful comparison for architecture positioning because it
separates release-ready drafts from rewriteable drafts and blocked drafts.

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| `prompt_only` | 0/15 | 12/15 | 3/15 |
| `rag_only` | 2/15 | 10/15 | 3/15 |
| `validator_only` | 1/15 | 12/15 | 2/15 |
| `prompt_level_cap` | 5/15 | 10/15 | 0/15 |
| `proxy_level_cap` | 0/15 | 15/15 | 0/15 |

Raw comparison:

| Group | Release | Rewrite required | Block |
|---|---:|---:|---:|
| Baseline modes total | 3/45 | 34/45 | 8/45 |
| CAP modes total | 5/30 | 25/30 | 0/30 |

Practical reading:

```text
Gemini 3.1 Pro is strong enough to produce useful drafts in all modes, but the
baseline modes still emit blocking failures. CAP modes did not emit blocking
failures in this run; they shifted the problem from block to rewrite.
```

That is the architectural win: not "CAP makes the raw model perfect", but
"CAP makes the release boundary explicit and keeps unsafe drafts out of direct
release."

## Deterministic Shaping

The rewrite shaper is deterministic and uses the case contract. It is not an
LLM and it is not raw model performance.

| Group | Total | Pass release | Rewrite from case contract | Final gate release |
|---|---:|---:|---:|---:|
| Baseline modes | 45 | 3 | 42 | 45/45 |
| CAP modes | 30 | 5 | 25 | 30/30 |
| All modes | 75 | 8 | 67 | 75/75 |

Final release-gate v0.2 after shaping:

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| `prompt_only` | 15/15 | 0/15 | 0/15 |
| `rag_only` | 15/15 | 0/15 | 0/15 |
| `validator_only` | 15/15 | 0/15 | 0/15 |
| `prompt_level_cap` | 15/15 | 0/15 | 0/15 |
| `proxy_level_cap` | 15/15 | 0/15 | 0/15 |

Correct reporting:

```text
Gemini 3.1 Pro produced 75/75 presentable drafts. Under release_gate v0.2, the
baseline modes had 8 blocking raw outputs while CAP modes had 0 blocking raw
outputs. After deterministic shaping, all 75 candidates passed the final gate.
```

Incorrect reporting:

```text
Gemini solved 75/75 hard-holdout cases.
```

## Artifacts

Raw baseline modes:

- [`gemini_31_pro_presentable_baseline_modes_outputs.json`](./gemini_31_pro_presentable_baseline_modes_outputs.json)
- [`gemini_31_pro_presentable_baseline_modes_report.md`](./gemini_31_pro_presentable_baseline_modes_report.md)
- [`gemini_31_pro_presentable_baseline_modes_gate_v02.md`](./gemini_31_pro_presentable_baseline_modes_gate_v02.md)

Raw CAP modes:

- [`gemini_31_pro_presentable_cap_outputs.json`](./gemini_31_pro_presentable_cap_outputs.json)
- [`gemini_31_pro_presentable_cap_report.md`](./gemini_31_pro_presentable_cap_report.md)
- [`gemini_31_pro_presentable_cap_gate_v02.md`](./gemini_31_pro_presentable_cap_gate_v02.md)

Shaped baseline modes:

- [`gemini_31_pro_presentable_baseline_modes_shaped_v02_summary.md`](./gemini_31_pro_presentable_baseline_modes_shaped_v02_summary.md)
- [`gemini_31_pro_presentable_baseline_modes_shaped_v02_gate.md`](./gemini_31_pro_presentable_baseline_modes_shaped_v02_gate.md)

Shaped CAP modes:

- [`gemini_31_pro_presentable_cap_shaped_v02_summary.md`](./gemini_31_pro_presentable_cap_shaped_v02_summary.md)
- [`gemini_31_pro_presentable_cap_shaped_v02_gate.md`](./gemini_31_pro_presentable_cap_shaped_v02_gate.md)
