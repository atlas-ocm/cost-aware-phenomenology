# Proxy Release Gate Adjudication

This folder is a blinded manual review pack for deterministic proxy release-gate
actions. It does not call an LLM.

Files:

- `blinded_pack.md` - human-readable blinded review pack
- `blinded_pack.json` - machine-readable blinded pack
- `blinded_key.json` - unblinded gate action key; do not use while labeling
- `manual_labels_template.tsv` - spreadsheet-friendly label sheet
- `manual_labels_template.json` - JSON label template
- `author_review_pack.md` - author-review worksheet; not independent
  adjudication
- `manual_labels_author.tsv` - separate author labels sheet; keep the template
  blank
- `manual_review_protocol.md` - reviewer instructions and reporting rules
- `disagreement_summary.md` - current gate/manual comparison status
- `codex_draft_labels.tsv` - non-human draft labels for debugging
- `codex_draft_disagreement_summary.md` - gate vs Codex draft comparison
- `codex_draft_adjudication_note.md` - short interpretation of draft
  disagreements

Manual action labels:

- `release`
- `rewrite_required`
- `block`

The first compact pass should usually label boundary actions first:
`release` and `block`. Full `rewrite_required` adjudication can be run later if
needed.

See `manual_review_protocol.md` before filling independent labels. In
particular, do not use `blinded_key.json` or any `codex_draft_*` file while
labeling.

For author review, use `author_review_pack.md` and fill
`manual_labels_author.tsv`. Report that result as `author manual review`, not as
independent adjudication.

The Codex draft files are not independent manual adjudication. They are included
only to make release-gate disagreement classes reviewable before human labeling.
