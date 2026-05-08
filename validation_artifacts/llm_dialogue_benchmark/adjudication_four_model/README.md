# Four-Model Blinded Manual Adjudication Pack

Status: prepared, not yet manually labeled.

This folder contains the blinded review package for the combined four-model
baseline-v1 live run.

## Files

- [`blinded_pack.md`](./blinded_pack.md) - human-readable blinded review pack
- [`blinded_pack.json`](./blinded_pack.json) - machine-readable blinded review
  pack
- [`manual_labels_template.tsv`](./manual_labels_template.tsv) - spreadsheet
  friendly manual labels sheet
- [`manual_labels_template.json`](./manual_labels_template.json) - JSON labels
  template
- [`blinded_key.json`](./blinded_key.json) - private key mapping item ids back
  to model, prompt mode, case id, and lexical score
- [`disagreement_summary.md`](./disagreement_summary.md) - current
  lexical/manual comparison status

## Scope

The pack contains 100 blinded items:

```text
4 models x 5 prompt modes x 5 cases = 100 outputs
```

## Review Workflow

From `CAP/`:

1. Read the shared rubric:

```bash
validation_artifacts/llm_dialogue_benchmark/manual_adjudication_rubric.md
```

2. Read and label the blinded items:

```bash
validation_artifacts/llm_dialogue_benchmark/adjudication_four_model/blinded_pack.md
validation_artifacts/llm_dialogue_benchmark/adjudication_four_model/manual_labels_template.tsv
```

Use `pass`, `fail`, or blank in `manual_ok`. Use comma-separated values for
`manual_failure_modes` and `manual_success_signals`.

3. Analyze disagreements directly from TSV:

```bash
python reference/python/scripts/analyze_adjudication_disagreements.py ^
  --adjudication-dir validation_artifacts/llm_dialogue_benchmark/adjudication_four_model ^
  --labels-tsv validation_artifacts/llm_dialogue_benchmark/adjudication_four_model/manual_labels_template.tsv ^
  --output-md validation_artifacts/llm_dialogue_benchmark/adjudication_four_model/disagreement_summary.md ^
  --output-json validation_artifacts/llm_dialogue_benchmark/adjudication_four_model/disagreement_summary.json
```

4. Optionally export the TSV labels back to JSON:

```bash
python reference/python/scripts/adjudication_labels_tsv.py import ^
  --adjudication-dir validation_artifacts/llm_dialogue_benchmark/adjudication_four_model
```

This writes `manual_labels_from_tsv.json` by default so the original template is
not overwritten accidentally.

## Review Rule

Do not edit `blinded_key.json` during review. It exists only for comparison
after labels are filled.
