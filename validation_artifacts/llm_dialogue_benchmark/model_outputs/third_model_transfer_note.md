# Third-Model Transfer Probe

Status: exploratory live benchmark extension.

This note adds `mistral-nemo-instruct-2407` to the initial LLM dialogue
benchmark outputs. It is intentionally reported as a transfer probe, not as a
new broad benchmark claim.

## Configuration

```text
Endpoint: LM Studio / OpenAI-compatible API
Model: mistral-nemo-instruct-2407
Modes: prompt_only, rag_only, validator_only, prompt_level_cap, proxy_level_cap
Cases: 5
Generation calls: 25
Temperature: 0
Max tokens: 350
Identity check: /v1/models availability + response model match
```

Combined three-model artifacts:

- [`three_model_outputs.json`](./three_model_outputs.json)
- [`three_model_report.md`](./three_model_report.md)
- [`three_model_report.json`](./three_model_report.json)

Mistral-only artifacts:

- [`mistral_nemo_outputs.json`](./mistral_nemo_outputs.json)
- [`mistral_nemo_report.md`](./mistral_nemo_report.md)
- [`mistral_nemo_report.json`](./mistral_nemo_report.json)

## Scored Result

| Mode | comet | silicon | mistral-nemo |
|---|---:|---:|---:|
| prompt_only | 0/5 | 0/5 | 1/5 |
| rag_only | 1/5 | 2/5 | 2/5 |
| validator_only | 3/5 | 2/5 | 1/5 |
| prompt_level_cap | 4/5 | 3/5 | 1/5 |
| proxy_level_cap | 5/5 | 5/5 | 1/5 |

## Interpretation

The third-model probe exposed transfer sensitivity. Under the current prompt
templates and lexical/heuristic scorer, `mistral-nemo-instruct-2407` did not
benefit from prompt-level or proxy-level CAP in the same way as comet and
silicon.

This weakens any broad claim that the current prompt templates transfer across
model families. It does not invalidate the deterministic proxy policy pack; it
shows that prompt wording, model instruction-following behavior, and scorer
coverage matter for live model benchmarks.

## Required Follow-Up

Before making stronger claims:

- manually adjudicate the Mistral outputs;
- compare lexical scorer labels against human labels;
- inspect whether failures are semantic failures or scorer false negatives;
- harden prompt templates without changing the frozen case goals;
- rerun after freezing updated scoring and templates.

## Hardened v2 Follow-Up

The exact same model, `mistral-nemo-instruct-2407`, was rerun with hardened v2
prompt templates. A substitute or abliterated model was not used.

Result:

| Mode | v1 | hardened v2 |
|---|---:|---:|
| prompt_only | 1/5 | 1/5 |
| rag_only | 2/5 | 2/5 |
| validator_only | 1/5 | 0/5 |
| prompt_level_cap | 1/5 | 1/5 |
| proxy_level_cap | 1/5 | 1/5 |

See [`mistral_nemo_hardened_v2_comparison.md`](./mistral_nemo_hardened_v2_comparison.md).

This means prompt hardening improved answer shape in places, but did not
improve the current lexical score. The next required step is manual
adjudication and scorer disagreement analysis, not post-hoc scorer broadening.

The strongest current reading is:

```text
CAP proxy policy is machine-checkable and worked on the first two live models.
The third-model probe shows that live prompt transfer is not solved yet.
```
