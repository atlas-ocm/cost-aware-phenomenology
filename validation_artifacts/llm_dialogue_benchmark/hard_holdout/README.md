# Hard Holdout Dialogue Benchmark Pack

Status: frozen scaffold + live stress runs + partial API control.

This folder contains a harder holdout pack for the CAP LLM dialogue benchmark.
It is separate from the original five-case baseline pack so the baseline result
is not silently redefined.

Case design follows
[`../../case_design_policy.md`](../../case_design_policy.md). The pack uses
neutral operational scenarios suitable for public review and grant/sponsor
evaluation.

## Purpose

The original pack is intentionally small and explicit. It is useful for
debugging the harness, but too easy for broad claims. This hard holdout adds:

- noisy counter-sources;
- relationship-domain false frames;
- jurisdiction and sample-scope RAG traps;
- stale anchors in price and relationship planning;
- validator overtrust cases where the validator checked only shape or a narrow
  scan;
- retrieved prompt-injection-like text;
- hidden telemetry treated as non-evidence;
- causal overclaiming with background vulnerability vs proximate trigger.

## Files

- [`../../../reference/python/scripts/sanitize_model_output_artifacts.py`](../../../reference/python/scripts/sanitize_model_output_artifacts.py)
  - redacts provider-internal raw-response fields such as `reasoning_content`,
    `thinking`, and `thought_signature` before public release
- [`cases/`](./cases/) - 15 frozen hard-holdout cases
- [`evaluation_status.md`](./evaluation_status.md)
  - compact map of each hard-holdout artifact, its claim status, and next
    action
- [`fixture_outputs/smoke_outputs.json`](./fixture_outputs/smoke_outputs.json)
  - synthetic harness smoke outputs, not empirical model results
- [`scaffold_report.md`](./scaffold_report.md) - smoke scorer report
- [`scaffold_report.json`](./scaffold_report.json) - machine-readable smoke
  scorer report
- [`model_outputs/mistral_nemo_hard_holdout_run_note.md`](./model_outputs/mistral_nemo_hard_holdout_run_note.md)
  - first live hard-holdout transfer run on `mistral-nemo-instruct-2407`
- [`model_outputs/qwen35_9b_hard_holdout_run_note.md`](./model_outputs/qwen35_9b_hard_holdout_run_note.md)
  - standard Qwen generation-budget failure and complete no-thinking Qwen run
- [`model_outputs/gemini_25_flash_hard_holdout_run_note.md`](./model_outputs/gemini_25_flash_hard_holdout_run_note.md)
  - partial Gemini 2.5 Flash free-tier control run and Pro quota failure note
- [`model_outputs/presentable_demo_run_note.md`](./model_outputs/presentable_demo_run_note.md)
  - complete Qwen and Mistral presentation/demo runs using structured
    Markdown templates; not a frozen benchmark lane
- [`adjudication_mistral_nemo/`](./adjudication_mistral_nemo/) - blinded
  manual adjudication pack for the live Mistral hard-holdout run
- [`adjudication_qwen35_9b_no_thinking/`](./adjudication_qwen35_9b_no_thinking/)
  - blinded manual adjudication pack for the live Qwen no-thinking hard-holdout
    run
- [`release_gate_adjudication_boundary/`](./release_gate_adjudication_boundary/)
  - compact blinded manual adjudication pack for deterministic proxy release
    gate boundary actions (`release` and `block`)
- [`release_gate_v0.2_prereg.md`](./release_gate_v0.2_prereg.md)
  - preregistered update path for proxy release gate v0.2; implemented only in
    separate `*_v02` reports

## Current Smoke Result

The smoke result is synthetic. It exists only to verify report shape and failure
coverage.

| Mode | Passed | Failed |
|---|---:|---:|
| prompt_only | 0/15 | 15/15 |
| rag_only | 6/15 | 9/15 |
| validator_only | 4/15 | 11/15 |
| prompt_level_cap | 14/15 | 1/15 |
| proxy_level_cap | 15/15 | 0/15 |

## Current Live Results

The first live transfer run used `mistral-nemo-instruct-2407` through LM Studio
with hardened v2 templates, `temperature=0`, and `max_tokens=4096`.

| Mode | Passed | Failed |
|---|---:|---:|
| prompt_only | 0/15 | 15/15 |
| rag_only | 0/15 | 15/15 |
| validator_only | 1/15 | 14/15 |
| prompt_level_cap | 0/15 | 15/15 |
| proxy_level_cap | 1/15 | 14/15 |

A later Qwen run found that standard `qwen/qwen3.5-9b` did not release content
for `hh_14_forced_concise_yes` even at `max_tokens=32768`. The complete Qwen
run therefore used `atlas/qwen3.5-9b-no-thinking` with `max_tokens=8192`.

| Mode | Passed | Failed |
|---|---:|---:|
| prompt_only | 0/15 | 15/15 |
| rag_only | 2/15 | 13/15 |
| validator_only | 1/15 | 14/15 |
| prompt_level_cap | 0/15 | 15/15 |
| proxy_level_cap | 0/15 | 15/15 |

These are lexical/heuristic scorer results, not final benchmark claims. Both
live hard-holdout runs are failure/transfer-stress results under the current
templates and scorer. Use the blinded adjudication packs before interpreting
the gap as model failure, prompt-transfer failure, or scorer strictness.

## Presentable Demo Runs

Qwen and Mistral were also run through
[`../prompt_templates_presentable/`](../prompt_templates_presentable/) to
produce complete, readable Markdown outputs for qualitative review and demos.
Both runs completed all 75 outputs with no empty responses. These outputs are
reported separately because the visible structure changes the prompt surface.
See
[`model_outputs/presentable_demo_run_note.md`](./model_outputs/presentable_demo_run_note.md).

The Qwen and Mistral presentable outputs were also passed through the
deterministic rewrite shaper. This produced 75/75 final `release` actions under
`release_gate v0.2` for both models, but most items were rewritten from case
contracts (`64/75` for Qwen, `70/75` for Mistral), so this is pipeline evidence
rather than a raw model score.

Gemini 3.1 Pro was also run as a complete five-mode presentable comparison. It
produced 75/75 raw outputs. Under `release_gate v0.2`, the three baseline modes
had 8/45 raw blocks while the two CAP modes had 0/30 raw blocks. After
deterministic shaping, the final gate accepted 75/75 candidates. This is
external architecture-comparison evidence, not a frozen benchmark win. See
[`model_outputs/gemini_31_pro_presentable_full_comparison.md`](./model_outputs/gemini_31_pro_presentable_full_comparison.md).

## Gemini Free-Tier Control Attempt

A Gemini control was attempted on the supplied free-tier key. `gemini-2.5-pro`
was visible from `/models` but had free-tier generation quota `0`, so no Pro
ceiling result was possible.

A later paid-key check also listed `gemini-2.5-pro`, but generation was denied
with `HTTP 403 PERMISSION_DENIED` / `Your project has been denied access`. A
direct Gemini `generateContent` smoke check also returned `HTTP 403 Forbidden`,
so the paid-key issue appears to be project/access-level rather than a CAP
runner failure.

`gemini-2.5-flash` generated a partial run before hitting the free-tier daily
limit of 20 requests per project/model. The only complete mode is
`prompt_only`:

| Model / mode | Completed outputs | Lexical pass | Gate release | Gate rewrite | Gate block |
|---|---:|---:|---:|---:|---:|
| Gemini 2.5 Flash / prompt_only | 15/15 | 0/15 | 0/15 | 14/15 | 1/15 |
| Gemini 2.5 Flash / rag_only | 4/15 | incomplete | incomplete | incomplete | incomplete |
| Gemini 2.5 Flash / proxy_level_cap | 0/15 | incomplete | incomplete | incomplete | incomplete |

See
[`model_outputs/gemini_25_flash_hard_holdout_run_note.md`](./model_outputs/gemini_25_flash_hard_holdout_run_note.md).

## Proxy Release Gate

A deterministic post-generation gate is available as a separate view of the
same outputs. It does not call an LLM. It reports:

```text
release          = no blocking failure and all required success signals present
rewrite_required = no blocking failure, but required release evidence is missing
block            = non-contextualized failure signal remains
```

Current gate reports:

- [`model_outputs/qwen35_9b_no_thinking_proxy_release_gate.md`](./model_outputs/qwen35_9b_no_thinking_proxy_release_gate.md)
- [`model_outputs/mistral_nemo_proxy_release_gate.md`](./model_outputs/mistral_nemo_proxy_release_gate.md)

Current v0.1 summary:

| Model / mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| Qwen no-thinking / prompt_only | 0/15 | 13/15 | 2/15 |
| Qwen no-thinking / rag_only | 7/15 | 8/15 | 0/15 |
| Qwen no-thinking / validator_only | 2/15 | 12/15 | 1/15 |
| Qwen no-thinking / prompt_level_cap | 2/15 | 13/15 | 0/15 |
| Qwen no-thinking / proxy_level_cap | 3/15 | 12/15 | 0/15 |
| Mistral Nemo / prompt_only | 0/15 | 13/15 | 2/15 |
| Mistral Nemo / rag_only | 2/15 | 13/15 | 0/15 |
| Mistral Nemo / validator_only | 1/15 | 14/15 | 0/15 |
| Mistral Nemo / prompt_level_cap | 0/15 | 15/15 | 0/15 |
| Mistral Nemo / proxy_level_cap | 3/15 | 12/15 | 0/15 |

This view is still deterministic and lexical, but it is closer to the intended
CAP operational boundary than a single pass/fail score: many outputs are not
release-ready, yet are better classified as rewrite work rather than immediate
block.

## Proxy Rewrite Shaper

A deterministic post-gate shaper is available for the same hard-holdout output
format. It does not call an LLM and the shaped text is not raw model output. It
demonstrates the intended operational boundary:

```text
model output -> release gate -> rewrite/block -> shaped release candidate -> release gate
```

Current shaped artifacts:

- [`model_outputs/qwen35_9b_no_thinking_shaped_v02_summary.md`](./model_outputs/qwen35_9b_no_thinking_shaped_v02_summary.md)
- [`model_outputs/qwen35_9b_no_thinking_shaped_v02_gate.md`](./model_outputs/qwen35_9b_no_thinking_shaped_v02_gate.md)
- [`model_outputs/mistral_nemo_shaped_v02_summary.md`](./model_outputs/mistral_nemo_shaped_v02_summary.md)
- [`model_outputs/mistral_nemo_shaped_v02_gate.md`](./model_outputs/mistral_nemo_shaped_v02_gate.md)
- [`release_gate_rewrite_pipeline_demo.md`](./release_gate_rewrite_pipeline_demo.md)
  - compact three-case walkthrough of raw output -> gate -> shaper -> gate

The current shaped reports show `75/75` gate release after deterministic
case-contract shaping for both Qwen no-thinking and Mistral Nemo. This is a
rewrite-layer sanity check, not a benchmark score and not evidence that the raw
model outputs were release-ready.

Preregistered v0.2 gate reports:

- [`model_outputs/qwen35_9b_no_thinking_proxy_release_gate_v02.md`](./model_outputs/qwen35_9b_no_thinking_proxy_release_gate_v02.md)
- [`model_outputs/mistral_nemo_proxy_release_gate_v02.md`](./model_outputs/mistral_nemo_proxy_release_gate_v02.md)
- [`model_outputs/release_gate_v01_v02_comparison.md`](./model_outputs/release_gate_v01_v02_comparison.md)

v0.2 adds shape checks for meta-answers, role scaffolding, internal policy
jargon leakage, and a narrower contextualization rule for quoted/future stale
anchors. It changed 6 case actions across the Qwen and Mistral hard-holdout
gate reports. Most changes move `release` to `rewrite_required`, so this is a
release-boundary hardening step, not a score-improvement claim.

v0.2 summary:

| Model / mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| Qwen no-thinking / prompt_only | 0/15 | 13/15 | 2/15 |
| Qwen no-thinking / rag_only | 6/15 | 9/15 | 0/15 |
| Qwen no-thinking / validator_only | 2/15 | 13/15 | 0/15 |
| Qwen no-thinking / prompt_level_cap | 2/15 | 13/15 | 0/15 |
| Qwen no-thinking / proxy_level_cap | 2/15 | 13/15 | 0/15 |
| Mistral Nemo / prompt_only | 0/15 | 13/15 | 2/15 |
| Mistral Nemo / rag_only | 1/15 | 14/15 | 0/15 |
| Mistral Nemo / validator_only | 0/15 | 15/15 | 0/15 |
| Mistral Nemo / prompt_level_cap | 0/15 | 15/15 | 0/15 |
| Mistral Nemo / proxy_level_cap | 2/15 | 13/15 | 0/15 |

Boundary-action manual review:

- [`release_gate_adjudication_boundary/blinded_pack.md`](./release_gate_adjudication_boundary/blinded_pack.md)
- [`release_gate_adjudication_boundary/manual_labels_template.tsv`](./release_gate_adjudication_boundary/manual_labels_template.tsv)
- [`release_gate_adjudication_boundary/disagreement_summary.md`](./release_gate_adjudication_boundary/disagreement_summary.md)
- [`release_gate_adjudication_boundary/codex_draft_labels.tsv`](./release_gate_adjudication_boundary/codex_draft_labels.tsv)
- [`release_gate_adjudication_boundary/codex_draft_adjudication_note.md`](./release_gate_adjudication_boundary/codex_draft_adjudication_note.md)
- [`release_gate_adjudication_boundary/codex_draft_disagreement_summary.md`](./release_gate_adjudication_boundary/codex_draft_disagreement_summary.md)

The boundary pack intentionally includes only `release` and `block` actions
from the two live hard-holdout runs. This keeps the first human adjudication
pass focused on the highest-risk release-gate decisions. A full
`rewrite_required` review can be generated later by rerunning the script with
`--include-actions all`.

The Codex draft labels are a debugging artifact, not independent human labels.
They currently show `21/25` agreement with the deterministic gate and identify
four candidate release-gate v0.2 disagreement classes. The proposed v0.2 update
path is preregistered in
[`release_gate_v0.2_prereg.md`](./release_gate_v0.2_prereg.md) and has been
applied only to separate `*_v02` reports.

## Recommended Live Run

Use the hardened v2 prompt templates for live hard-holdout runs:

```bash
python reference/python/scripts/generate_llm_dialogue_outputs.py ^
  --case-dir validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases ^
  --template-dir validation_artifacts/llm_dialogue_benchmark/prompt_templates_hardened_v2 ^
  --output-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_outputs.json ^
  --models <model> ^
  --max-tokens 8192 ^
  --write-partial ^
  --resume
```

For rate-limited API providers, add a provider-appropriate delay and retry
policy, for example `--delay-seconds 13 --retries 4 --retry-delay-seconds 30`
for a 5 RPM free-tier endpoint.

Score already-produced outputs:

```bash
python reference/python/scripts/run_llm_dialogue_benchmark.py ^
  --case-dir validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases ^
  --outputs-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_outputs.json ^
  --output-md validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_report.md ^
  --output-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_report.json
```

Prepare the compact release-gate boundary adjudication pack:

```bash
python reference/python/scripts/prepare_release_gate_adjudication.py ^
  --case-dir validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases ^
  --outputs-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_hard_holdout_outputs.json ^
  --outputs-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/mistral_nemo_hard_holdout_outputs.json ^
  --output-dir validation_artifacts/llm_dialogue_benchmark/hard_holdout/release_gate_adjudication_boundary ^
  --include-actions release,block
```

Run the preregistered v0.2 release gate without overwriting v0.1 reports:

```bash
python reference/python/scripts/run_proxy_release_gate.py ^
  --gate-version v0.2 ^
  --case-dir validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases ^
  --outputs-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_outputs.json ^
  --output-md validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_proxy_release_gate_v02.md ^
  --output-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_proxy_release_gate_v02.json
```

Run the deterministic post-gate rewrite shaper and then gate the shaped output:

```bash
python reference/python/scripts/run_proxy_rewrite_shaper.py ^
  --case-dir validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases ^
  --outputs-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_outputs.json ^
  --output-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_shaped_v02_outputs.json ^
  --summary-md validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_shaped_v02_summary.md ^
  --summary-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_shaped_v02_summary.json
```

Analyze release-gate/manual action disagreements after labels are filled:

```bash
python reference/python/scripts/analyze_release_gate_adjudication.py ^
  --adjudication-dir validation_artifacts/llm_dialogue_benchmark/hard_holdout/release_gate_adjudication_boundary ^
  --labels-tsv validation_artifacts/llm_dialogue_benchmark/hard_holdout/release_gate_adjudication_boundary/manual_labels_template.tsv ^
  --output-md validation_artifacts/llm_dialogue_benchmark/hard_holdout/release_gate_adjudication_boundary/disagreement_summary.md ^
  --output-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/release_gate_adjudication_boundary/disagreement_summary.json
```

## Reporting Rule

Do not merge hard-holdout scores with the baseline scores. Report them as a
separate track:

```text
baseline_simple_5case
hard_holdout_15case
```

Live hard-holdout results still require manual adjudication before being used
as benchmark claims.
