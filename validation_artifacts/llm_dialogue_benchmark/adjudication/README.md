# Blinded Manual Adjudication Pack

Status: prepared, not yet manually labeled.

This folder contains a blinded manual review package for the first live CAP LLM
dialogue benchmark run.

## Files

- [`blinded_pack.md`](./blinded_pack.md) - human-readable blinded review pack
- [`blinded_pack.json`](./blinded_pack.json) - machine-readable blinded review
  pack
- [`manual_labels_template.json`](./manual_labels_template.json) - empty manual
  labels file to fill during review
- [`blinded_key.json`](./blinded_key.json) - private key mapping item ids back
  to model, prompt mode, case id, and lexical score

## Scope

The pack contains 50 blinded items:

```text
2 models x 5 prompt modes x 5 cases = 50 outputs
```

The reviewer sees case context, evidence, output text, and manual questions. The
reviewer does not see model id, prompt mode, or lexical scorer result.

## Manual Labels

`manual_labels_template.json` uses this shape:

```json
{
  "item_id": "ADJ-0001",
  "manual_ok": null,
  "manual_failure_modes": [],
  "manual_success_signals": [],
  "notes": ""
}
```

After manual labels are filled, compare them against `blinded_key.json` and the
lexical scorer result:

```bash
python reference/python/scripts/analyze_adjudication_disagreements.py \
  --adjudication-dir validation_artifacts/llm_dialogue_benchmark/adjudication \
  --print-md
```

## Rebuild

From `CAP/`:

```bash
python reference/python/scripts/prepare_llm_dialogue_adjudication.py \
  --outputs-json validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_silicon_outputs.json \
  --output-dir validation_artifacts/llm_dialogue_benchmark/adjudication \
  --seed 20260505
```
