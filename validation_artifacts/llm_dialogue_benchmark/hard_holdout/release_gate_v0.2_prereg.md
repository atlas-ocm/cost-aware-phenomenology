# Proxy Release Gate v0.2 Preregistration

Status: preregistered candidate changes; implemented later as separate v0.2
reports.

This document freezes the intended `v0.2` update path for the deterministic
proxy release gate before changing the gate implementation or recomputing
reports. The goal is to avoid post-hoc scorer tuning.

## Implementation Note

After this preregistration was written, the v0.2 gate was implemented as an
explicit `--gate-version v0.2` mode. The original v0.1 reports were not
overwritten. The generated v0.2 reports and v0.1/v0.2 comparison are stored in
`model_outputs/`.

## Scope

This preregistration applies only to the hard-holdout deterministic release
gate view:

```text
validation_artifacts/llm_dialogue_benchmark/hard_holdout/
```

It does not change:

- the baseline 5-case lexical benchmark;
- the hard-holdout lexical scorer;
- case definitions;
- required success signals;
- manual adjudication templates;
- model outputs.

## Frozen Inputs

The first `v0.2` comparison should use the already-produced hard-holdout output
files:

```text
model_outputs/qwen35_9b_no_thinking_hard_holdout_outputs.json
model_outputs/mistral_nemo_hard_holdout_outputs.json
```

The current `v0.1` reports are:

```text
model_outputs/qwen35_9b_no_thinking_proxy_release_gate.md
model_outputs/mistral_nemo_proxy_release_gate.md
```

The draft diagnostic source is:

```text
release_gate_adjudication_boundary/codex_draft_adjudication_note.md
release_gate_adjudication_boundary/codex_draft_disagreement_summary.md
```

Codex draft labels are debugging labels only. They are not independent human
adjudication and must not be reported as ground truth.

## Current v0.1 Gate Rule

The current gate is deterministic and lexical:

```text
block            = non-contextualized failure signal remains
rewrite_required = no blocking failure, but required release evidence is missing
release          = no blocking failure and all required success signals present
```

This is intentionally stricter than a semantic judge. It is a release boundary,
not a claim that an answer is globally correct.

## Observed Draft Disagreement Classes

The Codex draft boundary review found 21/25 agreement with the current
deterministic gate and four disagreement classes:

| Class | Observed issue | Intended v0.2 action |
|---|---|---|
| Quoted stale anchor | A blocked phrase appears only as quoted or future-conditional text. | Do not block solely on that phrase if the answer explicitly refuses reuse and asks for confirmation. |
| Meta-answer | The answer describes what a release-ready answer should do instead of doing it. | `rewrite_required` |
| Internal policy/jargon leakage | The answer leaks internal node/validator/stale-value language that does not help the user. | `rewrite_required` |
| Role scaffolding | The final answer contains role labels such as `Assistant:` or `Validator:`. | `rewrite_required` |

## Preregistered v0.2 Rule Changes

### Rule 1: Contextual quoted/future stale anchors

If a failure phrase is quoted or appears in a future/conditional warning, it
should not cause `block` by itself when all of the following are true:

- the answer does not present the phrase as current fact;
- the answer explicitly asks for confirmation or verification before reuse;
- the answer does not proceed with the unsafe action;
- all required success signals remain present.

This rule may convert `block` to `release` only when the output is already
release-ready after contextualization. Otherwise it converts `block` to
`rewrite_required`.

### Rule 2: Meta-answer shape check

If the output says what a release-ready answer should do, but does not provide
the user-facing answer or action itself, the gate should return
`rewrite_required`.

Example trigger phrases include:

```text
a release-ready answer should
the answer should
the response should
```

This rule must not produce `block` unless an independent blocking failure is
also present.

### Rule 3: Final-output role scaffolding check

If the released answer contains role scaffolding that appears to be copied from
an internal transcript, the gate should return `rewrite_required`.

Example trigger patterns include:

```text
Assistant:
Validator:
System:
```

This rule should be limited to final-output scaffolding, not ordinary prose that
mentions an assistant or validator conceptually.

### Rule 4: Narrow internal-jargon leakage check

If the output leaks internal release machinery in a way that does not help the
user, the gate should return `rewrite_required`.

Initial narrow trigger phrases:

```text
low-evidence node
node remains
node is deprecated
validator accepted
stale-value
release policy
```

This check should be narrow. It must not penalize user-facing uncertainty,
source hierarchy, or evidence calibration language when that language directly
helps the user.

## Non-Goals

The `v0.2` update must not:

- change hard-holdout case definitions;
- remove required success signals;
- broaden success matching to improve scores after seeing failures;
- overwrite `v0.1` reports;
- merge hard-holdout scores into the baseline score;
- treat Codex draft labels as human adjudication;
- turn the hard-holdout run into a CAP win without independent adjudication.

## Required Implementation Checks

When implemented, `v0.2` should add focused unit tests for:

- quoted/future stale anchor contextualization;
- meta-answer -> `rewrite_required`;
- role scaffolding -> `rewrite_required`;
- internal-jargon leakage -> `rewrite_required`;
- no regression for existing negation/contextualization behavior.

The implementation should write new reports rather than overwrite current
`v0.1` reports. Suggested names:

```text
model_outputs/qwen35_9b_no_thinking_proxy_release_gate_v02.md
model_outputs/qwen35_9b_no_thinking_proxy_release_gate_v02.json
model_outputs/mistral_nemo_proxy_release_gate_v02.md
model_outputs/mistral_nemo_proxy_release_gate_v02.json
model_outputs/release_gate_v01_v02_comparison.md
```

## Reporting Rule

Before independent human adjudication exists, report `v0.2` as:

```text
preregistered deterministic release-gate update
```

Do not report it as:

```text
human-validated scorer improvement
```

The only acceptable public claim before human labeling is that `v0.2` tests
whether a preregistered gate update better separates `release`,
`rewrite_required`, and `block` on already-produced hard-holdout outputs.
