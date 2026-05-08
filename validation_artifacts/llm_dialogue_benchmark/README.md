# LLM Dialogue Benchmark Scaffold

This folder contains the benchmark scaffold for comparing:

- `prompt_only`
- `rag_only`
- `validator_only`
- `prompt_level_cap`
- `proxy_level_cap`

The default report uses synthetic smoke outputs. It does not call an LLM and is
not an empirical model benchmark.

Public-facing cases in this benchmark should follow
[`../case_design_policy.md`](../case_design_policy.md): neutral operational
scenarios, no personal hardship framing, and no advice-sensitive case design
unless a track explicitly requires that domain.

A separate harder holdout pack is available in
[`hard_holdout/`](./hard_holdout/). It contains 15 cases designed to stress
noisy evidence updates, relationship-domain false frames, stale anchors,
validator overtrust, prompt-injection-like retrieved text, hidden telemetry as
non-evidence, and causal overclaiming. Report this as a separate
`hard_holdout_15case` track, not as a replacement for the original five-case
baseline.

The first live two-model run is stored in
[`model_outputs/`](./model_outputs/). In that run, `proxy_level_cap` scored 5/5
on both `comet_12b_v.7-i1` and `silicon-maid-7b-imatrix` under the current
lexical/heuristic scorer.

A later third-model transfer probe added `mistral-nemo-instruct-2407`. It
scored only 1/5 in `proxy_level_cap` under the current templates/scorer, so it
is reported as a prompt/scorer transfer-sensitivity finding rather than as a
polished benchmark win. See
[`model_outputs/third_model_transfer_note.md`](./model_outputs/third_model_transfer_note.md).

The same exact model was later rerun with hardened v2 prompt templates. The
CAP-mode lexical score did not improve, so the result is documented as a
hardening experiment that requires manual adjudication rather than post-hoc
scorer broadening. See
[`model_outputs/mistral_nemo_hardened_v2_comparison.md`](./model_outputs/mistral_nemo_hardened_v2_comparison.md).

`qwen/qwen3.5-9b` was added as a fourth baseline-v1 model. Because it spends a
large budget in reasoning tokens, the valid run used `max_tokens=8192`; smaller
budgets produced empty released content. See
[`model_outputs/qwen35_9b_run_note.md`](./model_outputs/qwen35_9b_run_note.md).

Read [`scorer_audit.md`](./scorer_audit.md) before treating the live run as a
benchmark claim.

The blinded manual review package is in [`adjudication/`](./adjudication/).
It contains 50 blinded outputs plus a separate key and labels template.

Optional model-graded auditor prompt packs are available for the two-model run
and the combined three-model run. They prepare judge prompts from
already-produced outputs, but do not call a judge model and should not be
treated as ground truth.

Run from `CAP/`:

```bash
python reference/python/scripts/run_llm_dialogue_benchmark.py --print-md
```

Write reports:

```bash
python reference/python/scripts/run_llm_dialogue_benchmark.py ^
  --output-md validation_artifacts/llm_dialogue_benchmark/scaffold_report.md ^
  --output-json validation_artifacts/llm_dialogue_benchmark/scaffold_report.json
```

For a real LLM-in-the-loop run, replace
`fixture_outputs/smoke_outputs.json` with model-produced outputs using the same
case and mode keys.

## Live output generation

The live generator targets an OpenAI-compatible API such as LM Studio:

```bash
python reference/python/scripts/generate_llm_dialogue_outputs.py ^
  --base-url http://127.0.0.1:1234/v1 ^
  --models comet_12b_v.7-i1 ^
  --output-json validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_outputs.json
```

Then score the generated outputs:

```bash
python reference/python/scripts/run_llm_dialogue_benchmark.py ^
  --outputs-json validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_outputs.json ^
  --output-md validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_report.md ^
  --output-json validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_report.json
```

Use `--dry-run` to render the prompt manifest without calling an LLM:

```bash
python reference/python/scripts/generate_llm_dialogue_outputs.py --dry-run
```

The generator loops by model first, then mode, then case. This keeps model
loading stable when running one local model at a time.

For hard-holdout live runs, use:

```bash
python reference/python/scripts/generate_llm_dialogue_outputs.py ^
  --case-dir validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases ^
  --template-dir validation_artifacts/llm_dialogue_benchmark/prompt_templates_hardened_v2 ^
  --output-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/<model>_outputs.json ^
  --models <model> ^
  --max-tokens 8192
```

For presentation-quality local runs, use the separate presentable template lane:
[`prompt_templates_presentable/`](./prompt_templates_presentable/). This is
intended for Qwen, Mistral, and external provider demos, but it is not a frozen
baseline lane because the visible Markdown structure changes the task surface.

## Blinded adjudication

Build a blinded manual review pack from live outputs:

```bash
python reference/python/scripts/prepare_llm_dialogue_adjudication.py ^
  --outputs-json validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_silicon_outputs.json ^
  --output-dir validation_artifacts/llm_dialogue_benchmark/adjudication ^
  --seed 20260505
```

The combined three-model pack is in
[`adjudication_three_model/`](./adjudication_three_model/).

The combined four-model pack is in
[`adjudication_four_model/`](./adjudication_four_model/). Its disagreement
analysis scaffold is
[`adjudication_four_model/disagreement_summary.md`](./adjudication_four_model/disagreement_summary.md).
For manual review, use
[`manual_adjudication_rubric.md`](./manual_adjudication_rubric.md) and the
spreadsheet-friendly
[`adjudication_four_model/manual_labels_template.tsv`](./adjudication_four_model/manual_labels_template.tsv).

Analyze TSV labels directly:

```bash
python reference/python/scripts/analyze_adjudication_disagreements.py ^
  --adjudication-dir validation_artifacts/llm_dialogue_benchmark/adjudication_four_model ^
  --labels-tsv validation_artifacts/llm_dialogue_benchmark/adjudication_four_model/manual_labels_template.tsv ^
  --output-md validation_artifacts/llm_dialogue_benchmark/adjudication_four_model/disagreement_summary.md ^
  --output-json validation_artifacts/llm_dialogue_benchmark/adjudication_four_model/disagreement_summary.json
```

The exact-model hardened v2 pack is in
[`adjudication_mistral_nemo_hardened_v2/`](./adjudication_mistral_nemo_hardened_v2/).
The Mistral v1 pack is in
[`adjudication_mistral_nemo/`](./adjudication_mistral_nemo/). A Codex-draft
semantic adjudication note is available at
[`model_outputs/mistral_nemo_codex_draft_adjudication.md`](./model_outputs/mistral_nemo_codex_draft_adjudication.md).
A stricter release-grade recalculation is available at
[`model_outputs/mistral_nemo_strict_release_recalc.md`](./model_outputs/mistral_nemo_strict_release_recalc.md).

## Optional model-graded auditor

Build a judge prompt pack from live outputs:

```bash
python reference/python/scripts/prepare_model_graded_auditor.py ^
  --outputs-json validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_silicon_outputs.json ^
  --output-dir validation_artifacts/llm_dialogue_benchmark/model_graded_auditor
```

This only prepares prompts and templates. It does not call an LLM.

The combined three-model prompt pack is in
[`model_graded_auditor_three_model/`](./model_graded_auditor_three_model/).

The combined four-model prompt pack is in
[`model_graded_auditor_four_model/`](./model_graded_auditor_four_model/).

The exact-model hardened v2 prompt pack is in
[`model_graded_auditor_mistral_nemo_hardened_v2/`](./model_graded_auditor_mistral_nemo_hardened_v2/).
