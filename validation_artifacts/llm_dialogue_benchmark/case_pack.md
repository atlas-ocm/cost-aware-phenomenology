# LLM Dialogue Benchmark Case Pack

Status: scaffold for future LLM-in-the-loop comparison.

Scope:

```text
The cases define prompts and scoring criteria.
The default report uses synthetic fixture outputs.
No LLM call is made by the benchmark scorer.
```

Modes intended for live runs:

| Mode | Description |
|---|---|
| `prompt_only` | Base instruction without retrieval or CAP policy. |
| `rag_only` | Includes retrieved context, but no CAP release policy. |
| `validator_only` | Uses post-generation validation framing only. |
| `prompt_level_cap` | Gives the model CAP telemetry and asks it to self-audit. |
| `proxy_level_cap` | External policy is treated as release constraint. |

Cases:

| Case | Failure mode |
|---|---|
| `ldb_01_self_justification_counter_source` | Self-justification after a user counter-source. |
| `ldb_02_sycophancy_false_frame` | Agreement with a false user frame. |
| `ldb_03_weak_rag_overclaim` | High-strength claim over weak RAG support. |
| `ldb_04_stale_cross_turn_anchor` | Reuse of a stale cross-turn anchor. |
| `ldb_05_validator_accepted_weak_claim` | Validator acceptance treated as proof. |
