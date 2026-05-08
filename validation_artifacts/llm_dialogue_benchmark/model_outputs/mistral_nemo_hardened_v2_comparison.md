# Mistral Nemo Hardened v2 Comparison

Status: prompt-hardening experiment after the third-model transfer probe.

This file compares `mistral-nemo-instruct-2407` under the original v1 prompt
templates and the hardened v2 prompt templates.

The model is exactly the same in both runs:

```text
mistral-nemo-instruct-2407
```

No abliterated or substitute model is included in this comparison.

## Why v2 Was Added

The v1 transfer probe showed that Mistral Nemo often failed to operationalize
CAP prompt instructions. Some outputs were one-word labels such as `Rejected`
or short meta-responses instead of final user-facing answers.

Hardened v2 templates were added to test whether the issue was primarily weak
prompt transfer:

- require final assistant answers;
- forbid one-word labels;
- make proxy-level CAP constraints explicit;
- spell out the expected operation for counter-sources, false frames, stale
  anchors, weak evidence, and validator overtrust.

Because v2 was created after inspecting failures, it is a prompt-hardening
experiment, not a frozen benchmark result.

## Artifacts

V1:

- [`mistral_nemo_outputs.json`](./mistral_nemo_outputs.json)
- [`mistral_nemo_report.md`](./mistral_nemo_report.md)

V2:

- [`mistral_nemo_hardened_v2_prompt_manifest.json`](./mistral_nemo_hardened_v2_prompt_manifest.json)
- [`mistral_nemo_hardened_v2_outputs.json`](./mistral_nemo_hardened_v2_outputs.json)
- [`mistral_nemo_hardened_v2_report.md`](./mistral_nemo_hardened_v2_report.md)

Review packs:

- [`../adjudication_mistral_nemo/`](../adjudication_mistral_nemo/)
- [`../adjudication_mistral_nemo_hardened_v2/`](../adjudication_mistral_nemo_hardened_v2/)
- [`../model_graded_auditor_mistral_nemo_hardened_v2/`](../model_graded_auditor_mistral_nemo_hardened_v2/)
- [`mistral_nemo_codex_draft_adjudication.md`](./mistral_nemo_codex_draft_adjudication.md)
- [`mistral_nemo_strict_release_recalc.md`](./mistral_nemo_strict_release_recalc.md)

## Scored Result

| Mode | V1 | Hardened v2 | Delta |
|---|---:|---:|---:|
| prompt_only | 1/5 | 1/5 | +0 |
| rag_only | 2/5 | 2/5 | +0 |
| validator_only | 1/5 | 0/5 | -1 |
| prompt_level_cap | 1/5 | 1/5 | +0 |
| proxy_level_cap | 1/5 | 1/5 | +0 |

## Interpretation

The hardening did not improve the lexical/heuristic benchmark score for CAP
modes. It did reduce some obvious instruction-transfer problems, but the scorer
still marks many outputs as failures because required success phrases are
missing.

Examples of likely scorer-sensitive misses:

- "new information you've provided" is semantically close to a source update,
  but does not match the current `source_update` phrase list;
- "I'm not finding any established proof" is semantically close to frame
  correction, but does not match all required success groups;
- "recheck before reuse and downgrade" is close to validator/evidence
  calibration, but may miss the current exact lexical signals.

This should not be fixed by silently broadening the scorer after the run.
Instead, the next step is manual adjudication:

```text
lexical score -> manual labels -> disagreement analysis -> frozen scorer update
```

The honest current conclusion is:

```text
Mistral Nemo remains a transfer-sensitive model under both v1 and hardened v2.
The v2 prompt hardening improved answer shape but did not improve the current
lexical score.
```

## Codex-Draft Adjudication Follow-Up

A first-pass semantic draft adjudication now suggests that the lexical scorer
understates Mistral Nemo's performance, especially after hardened v2:

| Mode | V1 lexical | V1 draft semantic | Hardened v2 lexical | Hardened v2 draft semantic |
|---|---:|---:|---:|---:|
| prompt_only | 1/5 | 2/5 | 1/5 | 2/5 |
| rag_only | 2/5 | 5/5 | 2/5 | 5/5 |
| validator_only | 1/5 | 5/5 | 0/5 | 5/5 |
| prompt_level_cap | 1/5 | 2/5 | 1/5 | 5/5 |
| proxy_level_cap | 1/5 | 4/5 | 1/5 | 5/5 |

This draft is not independent human ground truth. It should be used to guide
manual review and scorer disagreement analysis, not as a replacement benchmark
result.

The stricter release-grade recalculation is more conservative:

| Mode | V1 strict release | Hardened v2 strict release |
|---|---:|---:|
| prompt_only | 2/5 | 2/5 |
| rag_only | 5/5 | 2/5 |
| validator_only | 4/5 | 0/5 |
| prompt_level_cap | 2/5 | 5/5 |
| proxy_level_cap | 4/5 | 3/5 |

This stricter pass removes the artificially high hardened-v2 RAG-only and
validator-only results caused by permissive semantic labeling.
