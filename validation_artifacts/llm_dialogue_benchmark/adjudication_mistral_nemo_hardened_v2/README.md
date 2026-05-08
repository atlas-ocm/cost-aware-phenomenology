# Mistral Nemo Hardened v2 Adjudication Pack

Status: prepared, with permissive Codex-draft semantic labels.

This folder contains the blinded adjudication package for the exact-model
`mistral-nemo-instruct-2407` hardened v2 prompt experiment.

## Files

- [`blinded_pack.md`](./blinded_pack.md) - human-readable blinded review pack
- [`manual_labels_template.tsv`](./manual_labels_template.tsv) - empty TSV sheet
  for independent manual labels
- [`manual_labels_template.json`](./manual_labels_template.json) - empty JSON
  labels template
- [`codex_draft_labels.tsv`](./codex_draft_labels.tsv) - first-pass semantic
  draft labels, not independent human ground truth
- [`codex_draft_disagreement_summary.md`](./codex_draft_disagreement_summary.md)
  - lexical vs draft semantic disagreement report
- [`strict_release_labels.tsv`](./strict_release_labels.tsv) - conservative
  release-grade labels
- [`strict_release_disagreement_summary.md`](./strict_release_disagreement_summary.md)
  - lexical vs strict-release disagreement report
- [`blinded_key.json`](./blinded_key.json) - private key mapping item ids back
  to model, prompt mode, case id, and lexical score

## Draft Result

| Measure | Result |
|---|---:|
| Lexical score | 5/25 |
| Codex-draft semantic score | 22/25 |
| Lexical/draft agreement | 8/25 |
| Lexical/draft disagreements | 17/25 |
| Strict release score | 12/25 |

The draft suggests that hardened v2 substantially improved semantic answer
shape, especially in CAP modes, while the frozen lexical scorer missed many
paraphrased success signals. The high RAG-only and validator-only draft scores
reflect the small explicit case pack and permissive semantic rubric; they should
not be promoted as a general benchmark claim. Under stricter release-grade
criteria, v2 `rag_only` drops to 2/5 and v2 `validator_only` drops to 0/5.
