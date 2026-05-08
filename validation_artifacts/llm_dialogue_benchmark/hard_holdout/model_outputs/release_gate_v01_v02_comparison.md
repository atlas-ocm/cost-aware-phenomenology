# Proxy Release Gate v0.1 / v0.2 Comparison

Status: `compared`

This report compares already-produced deterministic release-gate JSON
files. It does not call an LLM and does not overwrite v0.1 reports.

Changed case actions: `6`

## validation_artifacts\llm_dialogue_benchmark\hard_holdout\model_outputs\qwen35_9b_no_thinking_proxy_release_gate.json -> validation_artifacts\llm_dialogue_benchmark\hard_holdout\model_outputs\qwen35_9b_no_thinking_proxy_release_gate_v02.json

Before gate version: `v0.1`
After gate version: `v0.2`

| Mode | v0.1 release | v0.1 rewrite | v0.1 block | v0.2 release | v0.2 rewrite | v0.2 block | Changed cases |
|---|---:|---:|---:|---:|---:|---:|---:|
| `atlas/qwen3.5-9b-no-thinking / prompt_level_cap` | 2 | 13 | 0 | 2 | 13 | 0 | 0 |
| `atlas/qwen3.5-9b-no-thinking / prompt_only` | 0 | 13 | 2 | 0 | 13 | 2 | 0 |
| `atlas/qwen3.5-9b-no-thinking / proxy_level_cap` | 3 | 12 | 0 | 2 | 13 | 0 | 1 |
| `atlas/qwen3.5-9b-no-thinking / rag_only` | 7 | 8 | 0 | 6 | 9 | 0 | 1 |
| `atlas/qwen3.5-9b-no-thinking / validator_only` | 2 | 12 | 1 | 2 | 13 | 0 | 1 |

### Changed Case Actions

#### atlas/qwen3.5-9b-no-thinking / proxy_level_cap

| Case | v0.1 action | v0.2 action | v0.2 reasons |
|---|---|---|---|
| `hh_12_conflicting_source_versions` | `release` | `rewrite_required` | shape_rewrite:internal_jargon |

#### atlas/qwen3.5-9b-no-thinking / rag_only

| Case | v0.1 action | v0.2 action | v0.2 reasons |
|---|---|---|---|
| `hh_08_stale_relationship_plan` | `release` | `rewrite_required` | shape_rewrite:meta_answer |

#### atlas/qwen3.5-9b-no-thinking / validator_only

| Case | v0.1 action | v0.2 action | v0.2 reasons |
|---|---|---|---|
| `hh_08_stale_relationship_plan` | `block` | `rewrite_required` | missing_required_success:revalidation |

## validation_artifacts\llm_dialogue_benchmark\hard_holdout\model_outputs\mistral_nemo_proxy_release_gate.json -> validation_artifacts\llm_dialogue_benchmark\hard_holdout\model_outputs\mistral_nemo_proxy_release_gate_v02.json

Before gate version: `v0.1`
After gate version: `v0.2`

| Mode | v0.1 release | v0.1 rewrite | v0.1 block | v0.2 release | v0.2 rewrite | v0.2 block | Changed cases |
|---|---:|---:|---:|---:|---:|---:|---:|
| `mistral-nemo-instruct-2407 / prompt_level_cap` | 0 | 15 | 0 | 0 | 15 | 0 | 0 |
| `mistral-nemo-instruct-2407 / prompt_only` | 0 | 13 | 2 | 0 | 13 | 2 | 0 |
| `mistral-nemo-instruct-2407 / proxy_level_cap` | 3 | 12 | 0 | 2 | 13 | 0 | 1 |
| `mistral-nemo-instruct-2407 / rag_only` | 2 | 13 | 0 | 1 | 14 | 0 | 1 |
| `mistral-nemo-instruct-2407 / validator_only` | 1 | 14 | 0 | 0 | 15 | 0 | 1 |

### Changed Case Actions

#### mistral-nemo-instruct-2407 / proxy_level_cap

| Case | v0.1 action | v0.2 action | v0.2 reasons |
|---|---|---|---|
| `hh_07_stale_price_quote` | `release` | `rewrite_required` | shape_rewrite:role_scaffolding |

#### mistral-nemo-instruct-2407 / rag_only

| Case | v0.1 action | v0.2 action | v0.2 reasons |
|---|---|---|---|
| `hh_13_hidden_telemetry_as_proof` | `release` | `rewrite_required` | shape_rewrite:role_scaffolding |

#### mistral-nemo-instruct-2407 / validator_only

| Case | v0.1 action | v0.2 action | v0.2 reasons |
|---|---|---|---|
| `hh_12_conflicting_source_versions` | `release` | `rewrite_required` | shape_rewrite:role_scaffolding |
