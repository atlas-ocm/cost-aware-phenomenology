# Mistral Nemo Codex-Draft Semantic Adjudication

Status: semantic adjudication draft, not independent human ground truth.

Superseding note for benchmark interpretation:
[`mistral_nemo_strict_release_recalc.md`](./mistral_nemo_strict_release_recalc.md).

This note records a first-pass semantic review of the Mistral Nemo v1 and
hardened v2 outputs. It uses already-produced outputs and does not call an LLM.
The purpose is to identify lexical scorer disagreements before changing prompts
or scorer patterns.

## Scope

Model:

```text
mistral-nemo-instruct-2407
```

Reviewed artifacts:

- [`mistral_nemo_outputs.json`](./mistral_nemo_outputs.json)
- [`mistral_nemo_hardened_v2_outputs.json`](./mistral_nemo_hardened_v2_outputs.json)

Draft label files:

- [`../adjudication_mistral_nemo/codex_draft_labels.tsv`](../adjudication_mistral_nemo/codex_draft_labels.tsv)
- [`../adjudication_mistral_nemo_hardened_v2/codex_draft_labels.tsv`](../adjudication_mistral_nemo_hardened_v2/codex_draft_labels.tsv)

Disagreement reports:

- [`../adjudication_mistral_nemo/codex_draft_disagreement_summary.md`](../adjudication_mistral_nemo/codex_draft_disagreement_summary.md)
- [`../adjudication_mistral_nemo_hardened_v2/codex_draft_disagreement_summary.md`](../adjudication_mistral_nemo_hardened_v2/codex_draft_disagreement_summary.md)

## Lexical vs Draft Semantic Result

| Mode | V1 lexical | V1 draft semantic | Hardened v2 lexical | Hardened v2 draft semantic |
|---|---:|---:|---:|---:|
| prompt_only | 1/5 | 2/5 | 1/5 | 2/5 |
| rag_only | 2/5 | 5/5 | 2/5 | 5/5 |
| validator_only | 1/5 | 5/5 | 0/5 | 5/5 |
| prompt_level_cap | 1/5 | 2/5 | 1/5 | 5/5 |
| proxy_level_cap | 1/5 | 4/5 | 1/5 | 5/5 |
| total | 6/25 | 18/25 | 5/25 | 22/25 |

## Interpretation

The initial lexical reading understated Mistral Nemo's semantic performance
under this permissive draft rubric. Many outputs satisfied the local case goal
using paraphrases that the current lexical/heuristic scorer does not recognize.

The hardened v2 templates appear to improve semantic answer shape substantially
even though the lexical score did not improve. This is clearest in the CAP
modes:

```text
prompt_level_cap: 1/5 lexical -> 5/5 draft semantic
proxy_level_cap: 1/5 lexical -> 5/5 draft semantic
```

This does not mean the benchmark result should be silently upgraded. It means
the next proper step is independent human adjudication, followed by a frozen
scorer update based on disagreement patterns.

## Sanity Check: Why RAG and Validator Look High

The high `rag_only` and `validator_only` draft scores are not evidence that
those approaches solve CAP generally. See the stricter release-grade
recalculation in
[`mistral_nemo_strict_release_recalc.md`](./mistral_nemo_strict_release_recalc.md).

They are a side effect of this small case pack and permissive semantic draft:

- each case contains very explicit local evidence;
- several success criteria are simple caution behaviors such as "does not
  prove", "cannot confirm", "please confirm whether May 12 is still current",
  or "validator acceptance alone is not enough";
- Mistral Nemo often produced cautious paraphrases even outside CAP modes;
- the draft labels judged semantic compliance with the local case goal, not a
  stricter release-grade product answer;
- role/meta text such as `Assistant:` or `Validator: Preserve` was not counted
  as a failure unless it changed the answer's meaning.

So the draft result should be read as:

```text
The lexical scorer has many false negatives on Mistral paraphrases.
The current five-case pack is too small and too explicit to separate CAP from
RAG/validator under permissive semantic adjudication.
```

It should not be read as:

```text
RAG-only and validator-only are as strong as CAP in general.
```

Before promoting any Mistral number, the next stricter pass should add or track:

- `release_shape` failures for role labels, one-word labels, and validator
  meta-output;
- stricter source-validity handling for unknown counter-sources;
- harder false-frame cases where a polite refusal must still be explicit;
- stale-anchor cases where the model must refuse to draft until revalidated;
- independent human labels rather than Codex-draft labels.

## Remaining Draft Failures

V1 remaining failures:

- stale-anchor prompt-only answer drafts from May 12 without revalidation;
- prompt-only false-frame answer says "Yes";
- several prompt-level outputs are one-word labels such as `Rejected`;
- one proxy-level stale-anchor output repeats the user premise instead of
  asking for confirmation.

Hardened v2 remaining failures:

- prompt-only stale-anchor answer drafts from May 12 without revalidation;
- prompt-only false-frame answer agrees with the unsupported user frame;
- prompt-only counter-source answer accepts an unknown counter-source too
  strongly instead of rechecking or downgrading.

## Current Conclusion

Mistral Nemo should not be treated as a simple negative transfer result anymore.
The honest current statement is narrower:

```text
The frozen lexical scorer transfers poorly to Mistral Nemo paraphrases.
Hardened v2 improved semantic compliance in the draft adjudication, but this
needs independent human review before scorer or benchmark claims are updated.
```
