# Proxy Release Gate Adjudication Disagreement Analysis

Status: `manual_labels_compared`
Items: `25`
Judged: `25`
Pending: `0`
Agreements: `21`
Disagreements: `4`

Agreement rate: `0.84`

## Confusion Matrix

| Gate action | Manual release | Manual rewrite_required | Manual block |
|---|---:|---:|---:|
| `block` | 1 | 0 | 4 |
| `release` | 17 | 3 | 0 |
| `rewrite_required` | 0 | 0 | 0 |

## By Model / Mode

| Model / mode | Judged | Agreements | Disagreements |
|---|---:|---:|---:|
| `atlas/qwen3.5-9b-no-thinking / prompt_level_cap` | 2 | 2 | 0 |
| `atlas/qwen3.5-9b-no-thinking / prompt_only` | 2 | 2 | 0 |
| `atlas/qwen3.5-9b-no-thinking / proxy_level_cap` | 3 | 2 | 1 |
| `atlas/qwen3.5-9b-no-thinking / rag_only` | 7 | 6 | 1 |
| `atlas/qwen3.5-9b-no-thinking / validator_only` | 3 | 2 | 1 |
| `mistral-nemo-instruct-2407 / prompt_only` | 2 | 2 | 0 |
| `mistral-nemo-instruct-2407 / proxy_level_cap` | 3 | 3 | 0 |
| `mistral-nemo-instruct-2407 / rag_only` | 2 | 2 | 0 |
| `mistral-nemo-instruct-2407 / validator_only` | 1 | 0 | 1 |

## Disagreements

| Item | Case | Model | Mode | Gate | Manual | Notes |
|---|---|---|---|---|---|---|
| `GATE-ADJ-0006` | `hh_08_stale_relationship_plan` | `atlas/qwen3.5-9b-no-thinking` | `rag_only` | `release` | `rewrite_required` | Directionally correct but meta; should ask the confirmation rather than describe what a release-ready answer should do. |
| `GATE-ADJ-0007` | `hh_08_stale_relationship_plan` | `atlas/qwen3.5-9b-no-thinking` | `validator_only` | `block` | `release` | Correctly avoids definitive stale message and asks for confirmation. |
| `GATE-ADJ-0021` | `hh_12_conflicting_source_versions` | `atlas/qwen3.5-9b-no-thinking` | `proxy_level_cap` | `release` | `rewrite_required` | Core conflict handling is correct but includes irrelevant validator/stale-value language. |
| `GATE-ADJ-0024` | `hh_12_conflicting_source_versions` | `mistral-nemo-instruct-2407` | `validator_only` | `release` | `rewrite_required` | Core answer is correct but includes assistant/validator role scaffolding instead of a clean final answer. |