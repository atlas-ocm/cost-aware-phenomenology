# Hard-Holdout Evaluation Status

Status: artifact map for the 15-case hard-holdout track.

This file explains how to read the hard-holdout artifacts without merging
stress runs, release-gate checks, rewrite shaping, and adjudication scaffolds
into one misleading score.

## Status Map

| Artifact / track | Status | What it supports | What it does not support | Public-claim use | Next action |
|---|---|---|---|---|---|
| Frozen case pack | Complete | A separate 15-case stress track exists and is not silently merged into the 5-case baseline. | It does not by itself prove model performance. | Yes: cite as frozen hard-holdout scaffold. | Keep case IDs and contracts stable unless a new version is explicitly created. |
| Synthetic smoke fixture | Complete | The scorer/report shape covers the hard-holdout cases. | It is not empirical model evidence. | Yes, as harness smoke only. | Keep as CI/scaffold check. |
| Mistral Nemo live run | Complete stress run | Mistral transfer was weak under the current templates/scorer. | It does not prove CAP failure or success without adjudication. | Yes, as transfer-stress evidence only. | Use adjudication before benchmark claims. |
| Qwen no-thinking live run | Complete stress run | Qwen no-thinking produced complete hard-holdout outputs after standard Qwen generation-budget failures. | It does not prove CAP prompt transfer or broad model quality. | Yes, as stress/generation-budget evidence only. | Keep budget and released-output checks reported. |
| Gemini 2.5 Flash control | Partial API-control attempt | Runner can reach Gemini Flash and records quota/access limits. | It is not a complete external ceiling benchmark. | Yes, as partial/access note only. | Rerun only after provider access and quota are stable. |
| Presentable local demo lane | Complete Qwen + Mistral demo run | Both local models can generate complete, non-empty, professionally structured hard-holdout outputs; Qwen prompt-level CAP has no v0.2 gate blocks but still requires rewrites. | It is not a frozen baseline lane and does not establish benchmark improvement. Mistral still emits gate blocks in CAP modes. | Yes, as qualitative/demo evidence only. | Use Qwen prompt-level CAP as the next rewrite-shaper lane; use Mistral as a weaker comparison. |
| Gemini 3.1 Pro presentable five-mode comparison | Complete external presentation/architecture run | Gemini 3.1 Pro generated 75/75 outputs. Raw baseline modes had 8/45 blocks under `release_gate v0.2`; raw CAP modes had 0/30 blocks. | It is not a frozen benchmark lane and does not prove Gemini solved 75/75 cases, because 67/75 final candidates were deterministic case-contract rewrites. | Yes, as external architecture-comparison evidence. | Use the raw gate table to compare modes; keep shaped results framed as pipeline evidence. |
| Lexical hard-holdout scores | Complete reports | Current raw outputs are mostly not release-ready under the heuristic scorer. | They are not final human-quality benchmark results. | Use cautiously as stress diagnostics. | Compare against manual adjudication before changing scorer. |
| Proxy release gate v0.1 | Complete reports | Raw outputs can be separated into `release`, `rewrite_required`, and `block` instead of one pass/fail score. | It does not decide semantic truth. | Yes, as deterministic boundary diagnostic. | Preserve as baseline gate view. |
| Proxy release gate v0.2 | Preregistered hardening applied | v0.2 catches meta-answers, role scaffolding, internal jargon, and stale-anchor context issues. | It is not a score-improvement claim. | Yes, as release-boundary hardening. | Human-review the changed boundary classes. |
| v0.1/v0.2 comparison | Complete | The v0.2 diff is explicit and separate from v0.1 reports. | It is not a new benchmark leaderboard. | Yes, as preregistered gate-diff evidence. | Keep future gate changes diffed the same way. |
| Rewrite shaper outputs | Complete deterministic pipeline demo | Non-release raw outputs can be rewritten into case-contract release candidates and rechecked. | Shaped outputs are not raw model outputs or model scores. | Yes, as runtime pipeline evidence, not model performance. | Keep shaped artifacts separate from raw results. |
| Qwen presentable gate-to-rewrite pipeline | Complete deterministic pipeline demo | Qwen presentable drafts plus deterministic rewrite shaping produce 75/75 final `release` actions under `release_gate v0.2`. | It does not prove Qwen solved 75/75 cases, because 64/75 outputs were rewritten from case contracts. | Yes, as local CAP pipeline feasibility evidence. | Use this as the local reference lane for demos; keep raw and shaped artifacts separate. |
| Gemini 3.1 Pro CAP-only gate-to-rewrite pipeline | Complete external CAP-only pipeline slice | Gemini 3.1 Pro presentable CAP drafts plus deterministic rewrite shaping produce 30/30 final `release` actions under `release_gate v0.2`. | The CAP-only slice alone is not a full five-mode Gemini benchmark and does not prove Gemini solved the hard-holdout pack, because 25/30 outputs were rewritten from case contracts. | Yes, as external CAP pipeline feasibility evidence. | Use together with the five-mode comparison above. |
| Rewrite pipeline demo | Complete | Three examples show raw output -> gate -> shaper -> gate in human-readable form. | It does not prove the model solved those cases. | Yes, as explanatory evidence. | Add examples only if a new failure class needs illustration. |
| Release-gate boundary pack | Complete blinded scaffold | Independent reviewers can label high-risk `release` and `block` decisions without seeing model/gate identity. | It is not adjudicated until labels are filled. | Yes, as pending manual-review scaffold. | Fill independent manual labels. |
| Manual review protocol | Complete | Reviewers have explicit action definitions and reporting rules. | It does not provide labels itself. | Yes, as methodology. | Use it for independent labeling. |
| Manual disagreement summary | Pending | Tracks whether manual labels are filled. | Currently proves no agreement/disagreement because labels are blank. | Yes, as `pending_manual_labels`. | Fill `manual_labels_template.tsv/json`, then rerun analyzer. |
| Codex draft labels | Debugging only | Draft labels identified candidate v0.2 gate-hardening classes. | They are not independent human adjudication. | Cite only as non-human draft/debug artifact. | Do not mix with manual labels. |

## Public Reporting Rules

- Keep `baseline_simple_5case` and `hard_holdout_15case` separate.
- Do not report shaped outputs as raw model outputs.
- Do not report Codex draft labels as human adjudication.
- Do not treat `rewrite_required` as the same thing as `block`.
- Do not treat v0.2 hardening as a benchmark win.
- Do not report presentable demo outputs as frozen benchmark scores.
- Report Gemini 2.5 Flash as partial.
- Report Gemini 3.1 Pro presentable as a complete five-mode architecture
  comparison, not as a frozen external benchmark.

## Current Short Interpretation

The hard-holdout track currently supports a narrow engineering claim:

```text
CAP can expose release-boundary failures, classify raw outputs into release /
rewrite / block actions, and demonstrate a deterministic gate-to-rewrite
pipeline on frozen case contracts.
```

It does not yet support a broad benchmark claim:

```text
CAP outperforms prompt-only, RAG-only, validator-only, fine-tuning, or other
systems on external human-rated benchmarks.
```

The immediate next evidence step is independent manual adjudication of the
boundary pack, followed by disagreement analysis before any scorer or gate
change is promoted.
