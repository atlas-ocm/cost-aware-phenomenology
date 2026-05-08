# Live LLM Dialogue Benchmark Outputs

Status: initial live benchmark artifact plus exploratory third-model transfer probe.

This folder contains the first LLM-in-the-loop run for the CAP dialogue
benchmark scaffold and a later third-model transfer probe.

## Run Configuration

```text
Endpoint: LM Studio / OpenAI-compatible API
Models: comet_12b_v.7-i1, silicon-maid-7b-imatrix
Modes: prompt_only, rag_only, validator_only, prompt_level_cap, proxy_level_cap
Cases: 5
Generation calls: 50
Temperature: 0
Max tokens: 350
Identity check: /v1/models availability + response model match
```

The generator ran by model first, then mode, then case:

```text
comet_12b_v.7-i1 -> all modes/cases
silicon-maid-7b-imatrix -> all modes/cases
```

The later transfer probe added:

```text
mistral-nemo-instruct-2407 -> all modes/cases
Generation calls: 25
```

## Files

- [`../../../reference/python/scripts/sanitize_model_output_artifacts.py`](../../../reference/python/scripts/sanitize_model_output_artifacts.py)
  - redacts provider-internal raw-response fields such as `reasoning_content`,
    `thinking`, and `thought_signature` before public release
- [`../scorer_audit.md`](../scorer_audit.md) - limitations and audit notes for
  the lexical/heuristic scorer
- [`comet_silicon_outputs.json`](./comet_silicon_outputs.json) - raw prompts,
  raw API responses, extracted outputs, and model identity metadata
- [`comet_silicon_report.md`](./comet_silicon_report.md) - scored report
- [`comet_silicon_report.json`](./comet_silicon_report.json) - machine-readable
  scored report
- [`mistral_nemo_outputs.json`](./mistral_nemo_outputs.json) - third-model raw
  outputs
- [`mistral_nemo_report.md`](./mistral_nemo_report.md) - third-model scored
  report
- [`mistral_nemo_hardened_v2_outputs.json`](./mistral_nemo_hardened_v2_outputs.json) -
  exact-model rerun with hardened v2 templates
- [`mistral_nemo_hardened_v2_report.md`](./mistral_nemo_hardened_v2_report.md) -
  scored hardened v2 report
- [`mistral_nemo_hardened_v2_comparison.md`](./mistral_nemo_hardened_v2_comparison.md) -
  v1 vs hardened v2 comparison
- [`mistral_nemo_codex_draft_adjudication.md`](./mistral_nemo_codex_draft_adjudication.md) -
  first-pass semantic adjudication draft for Mistral v1 and hardened v2
- [`mistral_nemo_strict_release_recalc.md`](./mistral_nemo_strict_release_recalc.md) -
  conservative release-grade recalculation for Mistral v1 and hardened v2
- [`three_model_outputs.json`](./three_model_outputs.json) - combined outputs
  for all three models
- [`three_model_report.md`](./three_model_report.md) - combined scored report
- [`third_model_transfer_note.md`](./third_model_transfer_note.md) - transfer
  interpretation and limitations
- [`qwen35_9b_outputs.json`](./qwen35_9b_outputs.json) - valid Qwen run with
  `max_tokens=8192`
- [`qwen35_9b_report.md`](./qwen35_9b_report.md) - scored Qwen report
- [`qwen35_9b_run_note.md`](./qwen35_9b_run_note.md) - Qwen generation-budget
  note
- [`four_model_outputs.json`](./four_model_outputs.json) - combined outputs for
  comet, silicon, Mistral Nemo, and Qwen
- [`four_model_report.md`](./four_model_report.md) - combined four-model scored
  report

## Scored Result

| Mode | comet | silicon | mistral-nemo | qwen |
|---|---:|---:|---:|---:|
| prompt_only | 0/5 | 0/5 | 1/5 | 1/5 |
| rag_only | 1/5 | 2/5 | 2/5 | 2/5 |
| validator_only | 3/5 | 2/5 | 1/5 | 2/5 |
| prompt_level_cap | 4/5 | 3/5 | 1/5 | 2/5 |
| proxy_level_cap | 5/5 | 5/5 | 1/5 | 4/5 |

## Interpretation

This is a small initial benchmark, not a broad empirical proof. It supports the
engineering claim that an external proxy-level CAP policy can improve release
discipline on the first two selected local models. The Mistral Nemo probe shows
that the current prompt templates and scorer do not transfer cleanly to every
instruct model. The scorer is lexical/heuristic and should be audited before
making stronger claims.

The exact-model hardened v2 rerun did not improve the lexical score for Mistral
Nemo CAP modes. A permissive Codex-draft semantic adjudication suggested that
v2 improved semantic answer shape, but it was too forgiving for benchmark
interpretation. The stricter release recalculation gives a more conservative
reading: v2 `rag_only` drops to 2/5 and v2 `validator_only` drops to 0/5 once
role/meta wrappers and non-release-ready answers are penalized. These drafts are
not independent human ground truth; they are evidence that manual adjudication
and scorer disagreement analysis are needed before further prompt/scorer
changes.

The Qwen run required `max_tokens=8192` because lower generation budgets emitted
empty released content. It supports the need to report generation budget and
released-output validation for reasoning-heavy models.
