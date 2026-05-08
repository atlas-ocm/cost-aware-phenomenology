# Mistral Nemo Hard-Holdout Live Run

Date: 2026-05-07

Status: `live_model_run / lexical_scorer_only / failure_across_modes`

## Configuration

```text
Endpoint: LM Studio / OpenAI-compatible API
Model: mistral-nemo-instruct-2407
Case track: hard_holdout_15case
Templates: prompt_templates_hardened_v2
Modes: prompt_only, rag_only, validator_only, prompt_level_cap, proxy_level_cap
Cases: 15
Generation calls: 75
Temperature: 0
Max tokens: 4096
Identity check: /v1/models availability + response-model field match
```

## Lexical Scorer Result

| Mode | Passed | Failed |
|---|---:|---:|
| prompt_only | 0/15 | 15/15 |
| rag_only | 0/15 | 15/15 |
| validator_only | 1/15 | 14/15 |
| prompt_level_cap | 0/15 | 15/15 |
| proxy_level_cap | 1/15 | 14/15 |

## Interpretation

This is a hard-holdout failure across modes under the current prompt templates
and lexical scorer. It should not be reported as a CAP improvement.

## Proxy Release Gate View

The deterministic post-generation gate gives a more operational split:

| Mode | Release | Rewrite required | Block |
|---|---:|---:|---:|
| prompt_only | 0/15 | 13/15 | 2/15 |
| rag_only | 2/15 | 13/15 | 0/15 |
| validator_only | 1/15 | 14/15 | 0/15 |
| prompt_level_cap | 0/15 | 15/15 | 0/15 |
| proxy_level_cap | 3/15 | 12/15 | 0/15 |

This does not turn the run into a CAP win. It shows that even when direct
blocking failures are less frequent under the release gate, most answers still
need rewrite before public release.

Do not broaden the scorer from this result alone. The next step is blinded
manual adjudication and disagreement analysis, because several failures may be
semantic/prompt-transfer issues and some may be lexical misses.

## Qwen Attempt

A `qwen/qwen3.5-9b` hard-holdout attempt was started first with
`max_tokens=8192`. It stopped at `prompt_only / hh_14_forced_concise_yes`
because the model used the full generation budget and released empty
`message.content` with `finish_reason=length`. No output artifact was written.

This supports treating reasoning-heavy Qwen runs as requiring either a
no-thinking variant, a larger release budget, or an incremental/resumable
runner before using it for the 75-call hard-holdout track.

## Artifacts

- `mistral_nemo_hard_holdout_outputs.json` - raw prompts, model responses, and
  extracted outputs
- `mistral_nemo_hard_holdout_report.md` - lexical scorer report
- `mistral_nemo_hard_holdout_report.json` - machine-readable scorer report
- `../adjudication_mistral_nemo/` - blinded manual adjudication pack
