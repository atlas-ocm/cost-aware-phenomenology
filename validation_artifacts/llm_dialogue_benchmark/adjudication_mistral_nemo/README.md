# Mistral Nemo v1 Adjudication Pack

Status: prepared, with permissive Codex-draft semantic labels.

This folder contains the blinded adjudication package for the
`mistral-nemo-instruct-2407` v1 transfer probe.

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
| Lexical score | 6/25 |
| Codex-draft semantic score | 18/25 |
| Lexical/draft agreement | 13/25 |
| Lexical/draft disagreements | 12/25 |
| Strict release score | 17/25 |

The draft suggests that many v1 failures are scorer false negatives, but this
is not a release-grade adjudication. The high RAG-only and validator-only draft
scores reflect the small explicit case pack and should not be promoted as a
general benchmark claim. V1 still has real answer-shape failures such as
one-word `Rejected` outputs and stale-anchor reuse.
