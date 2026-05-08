# Validation Case Design Policy

This policy applies to public-facing CAP validation packs and benchmark tracks.
It exists to keep the repo legible for external reviewers, grant evaluators,
GitHub Sponsors readers, and engineering teams.

## Public-Facing Case Rules

Use neutral, review-safe scenarios by default:

- Prefer engineering, product, documentation, support, incident, and operations
  examples.
- Prefer `budget overrun`, `contingency buffer`, `incident invoice`, `stale
  release note`, `retrieval mismatch`, and `validator overtrust` over personal
  hardship examples.
- Avoid personal finance, medical, family-crisis, donation, charity, and
  debt-repayment framing unless the track is explicitly about that domain.
- Avoid cases that look like financial, medical, legal, or relationship advice.
  CAP benchmark cases should test claim calibration and release control, not
  provide life coaching.
- Avoid real private individuals, identifiable personal logs, and sensitive
  lived-experience examples unless they are fully anonymized and clearly needed.
- Keep causal cases focused on evidence boundaries: background vulnerability,
  proximate trigger, and what the evidence does or does not prove.

## Archived Artifacts

Do not rewrite archived live model outputs just to make them look cleaner.
Those files are evidence of what was actually run. If a public case is
materially renamed or reframed, treat the new case pack as a new benchmark
surface and rerun or clearly mark older outputs as historical.

## Scoring And Reporting

- Synthetic smoke outputs verify harness shape only.
- Lexical scorers are scaffolds, not truth.
- Live model results require manual adjudication before benchmark claims.
- Do not broaden a scorer after seeing a bad result without documenting the
  disagreement and adjudication rationale.
- Report hard holdout tracks separately from baseline tracks.

## Current Preferred Public Pattern

For causal-overclaim cases, use neutral operational examples such as:

```text
background vulnerability:
  contingency buffer reduced by non-critical prototype work

proximate trigger:
  emergency database recovery invoice

bad release:
  "the prototype caused the budget overrun"

good release:
  "the prototype reduced the buffer; the invoice was the proximate trigger;
   the evidence supports contribution, not single-cause attribution"
```

