# Mistral Nemo Strict Release Recalculation

Status: conservative release-grade recalculation from already-produced outputs.

This recalculation uses
[`strict_release_adjudication_rubric.md`](../strict_release_adjudication_rubric.md).
It does not call an LLM and does not change the frozen lexical scorer.

## Why This Recalculation Was Needed

The earlier Codex-draft semantic labels were too permissive for benchmark
interpretation. They counted many cautious paraphrases as pass even when the
answer shape was not release-ready.

The strict release recalculation adds observable failure criteria:

- one-word labels fail;
- role/meta wrappers such as `assistant:`, `Validator:`, and `user:` fail;
- separate validator/meta blocks fail;
- stale-anchor drafting before confirmation fails;
- each case must explicitly satisfy its local release requirement.

## Artifacts

V1:

- [`../adjudication_mistral_nemo/strict_release_labels.tsv`](../adjudication_mistral_nemo/strict_release_labels.tsv)
- [`../adjudication_mistral_nemo/strict_release_disagreement_summary.md`](../adjudication_mistral_nemo/strict_release_disagreement_summary.md)

Hardened v2:

- [`../adjudication_mistral_nemo_hardened_v2/strict_release_labels.tsv`](../adjudication_mistral_nemo_hardened_v2/strict_release_labels.tsv)
- [`../adjudication_mistral_nemo_hardened_v2/strict_release_disagreement_summary.md`](../adjudication_mistral_nemo_hardened_v2/strict_release_disagreement_summary.md)

## Result

| Mode | V1 lexical | V1 permissive draft | V1 strict release | v2 lexical | v2 permissive draft | v2 strict release |
|---|---:|---:|---:|---:|---:|---:|
| prompt_only | 1/5 | 2/5 | 2/5 | 1/5 | 2/5 | 2/5 |
| rag_only | 2/5 | 5/5 | 5/5 | 2/5 | 5/5 | 2/5 |
| validator_only | 1/5 | 5/5 | 4/5 | 0/5 | 5/5 | 0/5 |
| prompt_level_cap | 1/5 | 2/5 | 2/5 | 1/5 | 5/5 | 5/5 |
| proxy_level_cap | 1/5 | 4/5 | 4/5 | 1/5 | 5/5 | 3/5 |
| total | 6/25 | 18/25 | 17/25 | 5/25 | 22/25 | 12/25 |

## Interpretation

The stricter recalculation changes the earlier reading materially.

For v1, `rag_only` remains high because the five cases are small and explicit:
the model's RAG-only answers directly say "does not prove", "current context
does not establish X", "confirm whether May 12 is still current", and
"validator acceptance alone does not guarantee safety". This is a case-pack
limitation, not evidence that RAG-only solves CAP generally.

For hardened v2, the strict release-shape filter removes many `rag_only` and
`validator_only` passes because the outputs include role/meta wrappers or
separate validator blocks. This makes the result much less rosy:

```text
v2 rag_only:        5/5 permissive -> 2/5 strict release
v2 validator_only:  5/5 permissive -> 0/5 strict release
```

The hardened v2 CAP modes still improve relative to v1 under this strict pass:

```text
v2 prompt_level_cap: 5/5 strict release
v2 proxy_level_cap:  3/5 strict release
```

The proxy-level v2 misses are mostly release-shape or explicit-source-update
requirements, not broad overclaiming.

## Current Honest Claim

The correct current claim is:

```text
Mistral Nemo exposes both scorer false negatives and benchmark design
limitations. Under strict release recalculation, hardened v2 no longer gives
artificially high RAG-only or validator-only results, but the current five-case
pack is still too small to support broad model-level claims.
```

Before public reporting, use independent human labels and a larger holdout pack
with harder cases.
