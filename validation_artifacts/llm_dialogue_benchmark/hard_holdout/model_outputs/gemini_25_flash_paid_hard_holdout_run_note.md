# Gemini 2.5 Flash Paid Hard-Holdout Run Note

Date: 2026-05-08

Model: `models/gemini-2.5-flash`

Endpoint: Gemini OpenAI-compatible API

Template set: `prompt_templates_hardened_v2`

Temperature: `0`

Max tokens: `4096`

## Scope

This is a paid-key follow-up to the earlier Gemini 2.5 Flash free-tier partial
run. It is stored as a separate artifact instead of overwriting the free-tier
partial output, because the paid endpoint exposes the model identity as
`models/gemini-2.5-flash`.

The run covers the same three planned modes from the partial Flash control:

- `prompt_only`
- `rag_only`
- `proxy_level_cap`

It does not include `validator_only` or `prompt_level_cap`, and it is not a
Gemini Pro/frontier ceiling benchmark.

## Generation Result

All planned outputs were generated:

| Mode | Completed outputs | Planned outputs |
|---|---:|---:|
| prompt_only | 15 | 15 |
| rag_only | 15 | 15 |
| proxy_level_cap | 15 | 15 |

No empty released outputs were accepted by the runner.

## Scoring Summary

Lexical scorer:

| Mode | Passed | Failed |
|---|---:|---:|
| prompt_only | 0/15 | 15/15 |
| rag_only | 2/15 | 13/15 |
| proxy_level_cap | 3/15 | 12/15 |

Proxy release gate v0.2:

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| prompt_only | 0/15 | 13/15 | 2/15 |
| rag_only | 3/15 | 12/15 | 0/15 |
| proxy_level_cap | 5/15 | 9/15 | 1/15 |

## Interpretation

The paid Flash control is a complete external API transfer-stress run for the
three selected modes. It supports comparison of raw release-boundary behavior
under the deterministic gate, but it is not a human-adjudicated benchmark
result and should not be reported as proof that Gemini Flash solved or failed
the hard-holdout pack.

The old free-tier partial output remains useful only as an access/quota note.

## Artifacts

- `gemini_25_flash_paid_hard_holdout_outputs.json`
- `gemini_25_flash_paid_hard_holdout_report.md`
- `gemini_25_flash_paid_hard_holdout_report.json`
- `gemini_25_flash_paid_proxy_release_gate.md`
- `gemini_25_flash_paid_proxy_release_gate.json`
- `gemini_25_flash_paid_proxy_release_gate_v02.md`
- `gemini_25_flash_paid_proxy_release_gate_v02.json`
