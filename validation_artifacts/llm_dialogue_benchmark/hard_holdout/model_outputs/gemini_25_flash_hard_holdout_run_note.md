# Gemini 2.5 Flash Hard-Holdout Partial Run Note

Date: 2026-05-07

Model: `gemini-2.5-flash`

Endpoint: Gemini OpenAI-compatible API

Template set: `prompt_templates_hardened_v2`

Temperature: `0`

Max tokens: `4096`

## Pro Attempt

`gemini-2.5-pro` was checked first as the intended frontier/ceiling control.
The model was visible from `/models`, but generation failed on the supplied
free-tier key:

```text
HTTP 429 RESOURCE_EXHAUSTED
generate_content_free_tier_requests limit: 0
generate_content_free_tier_input_token_count limit: 0
model: gemini-2.5-pro
```

Therefore this run is not a Pro ceiling result.

## Paid-Key Follow-Up

A later paid-key check also listed `gemini-2.5-pro` from `/models`, but
generation was denied before any benchmark output was produced:

```text
OpenAI-compatible chat/completions:
HTTP 403 PERMISSION_DENIED
message: Your project has been denied access. Please contact support.

Direct Gemini generateContent:
HTTP 403 Forbidden
```

This indicates a project/access-level block, not a CAP runner failure and not a
free-tier quota exhaustion. No paid-key benchmark output was generated.

## Flash Partial Run

`gemini-2.5-flash` was available and generated successfully, but the free-tier
quota stopped the run at the daily project/model limit:

```text
GenerateRequestsPerDayPerProjectPerModel-FreeTier limit: 20
model: gemini-2.5-flash
```

One request was used for a smoke test. The main hard-holdout artifact contains
19 generated outputs:

| Mode | Completed outputs | Planned outputs |
|---|---:|---:|
| prompt_only | 15 | 15 |
| rag_only | 4 | 15 |
| proxy_level_cap | 0 | 15 |

Artifacts:

- `gemini_25_flash_hard_holdout_outputs.json`
- `gemini_25_flash_hard_holdout_partial_report.md`
- `gemini_25_flash_hard_holdout_partial_report.json`
- `gemini_25_flash_proxy_release_gate_partial.md`
- `gemini_25_flash_proxy_release_gate_partial.json`
- `gemini_25_flash_smoke_outputs.json`

## Completed Prompt-Only Result

The only complete mode in this partial run is `prompt_only`.

Lexical scorer:

| Mode | Passed | Failed |
|---|---:|---:|
| prompt_only | 0/15 | 15/15 |

Proxy release gate:

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| prompt_only | 0/15 | 14/15 | 1/15 |

This should not be interpreted as "Gemini fails all cases." The current lexical
scorer is intentionally strict and often requires explicit marker phrases. Many
Gemini prompt-only answers are semantically cautious but miss required release
signals, so the release gate classifies them as `rewrite_required` rather than
`block`.

## Operational Finding

This free-tier key is useful for smoke tests and small partial control runs. It
is not sufficient for a same-day 45-call hard-holdout control run.

To finish the intended Gemini control:

```text
15 cases x 3 modes = 45 generation calls
```

use one of:

- a billed Gemini project/key;
- a higher-quota key;
- multiple days with `--resume`;
- a smaller selected-case control pack.

## Runner Hardening Added

The live generator now supports:

```text
--resume
--delay-seconds
--retries
--retry-delay-seconds
```

These options are required for free-tier or unstable API endpoints.
