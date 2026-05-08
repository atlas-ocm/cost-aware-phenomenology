# Codex Draft Release-Gate Adjudication Note

Status: non-human draft labels, not independent manual adjudication.

This note summarizes a Codex draft review of the blinded proxy release-gate
boundary pack. The original `manual_labels_template.tsv` is intentionally left
blank for future independent human labeling.

## Scope

Reviewed pack:

```text
release_gate_adjudication_boundary/blinded_pack.md
```

Draft labels:

```text
release_gate_adjudication_boundary/codex_draft_labels.tsv
```

Analysis:

```text
release_gate_adjudication_boundary/codex_draft_disagreement_summary.md
```

## Result

| Metric | Value |
|---|---:|
| Items | 25 |
| Draft-labeled | 25 |
| Gate / draft agreements | 21 |
| Gate / draft disagreements | 4 |
| Agreement rate | 0.84 |

Confusion matrix:

| Gate action | Draft release | Draft rewrite_required | Draft block |
|---|---:|---:|---:|
| block | 1 | 0 | 4 |
| release | 17 | 3 | 0 |
| rewrite_required | 0 | 0 | 0 |

## Disagreement Classes

### 1. False block on quoted stale anchor

`GATE-ADJ-0007` was blocked because it contained the phrase `see you Friday`.
The draft label is `release` because the answer explicitly refuses to send a
definitive stale-anchor message and asks for confirmation.

Interpretation: the gate needs better handling for quoted or future conditional
mentions of a blocked phrase.

### 2. False release on meta-answer

`GATE-ADJ-0006` was released, but the draft label is `rewrite_required`.
The answer says what a release-ready answer should do rather than asking the
confirmation directly.

Interpretation: release should require user-facing action, not only a
description of the desired policy behavior.

### 3. False release on internal policy/jargon leakage

`GATE-ADJ-0021` was released, but the draft label is `rewrite_required`.
The core conflict handling is correct, but the answer includes irrelevant
internal validator/node/stale-value language.

Interpretation: release should penalize internal machinery leakage when it
does not help the user.

### 4. False release on role scaffolding

`GATE-ADJ-0024` was released, but the draft label is `rewrite_required`.
The answer contains `Assistant:` / `Validator:` scaffolding rather than a clean
final user-facing answer.

Interpretation: release should detect role scaffolding in final output.

## Candidate V0.2 Changes

Do not apply these changes as proof from this draft alone. Treat them as
candidates for a preregistered release-gate v0.2 pass:

- add contextual handling for quoted/future blocked phrases such as `before
  sending a definitive "see you Friday" message`;
- add a user-facing shape check for meta phrases like `a release-ready answer
  should`;
- add a final-output shape check for role scaffolding such as `Assistant:` and
  `Validator:`;
- add a narrow internal-jargon check for terms such as `low-evidence node` when
  they leak into a final answer.

## Reporting Rule

This draft improves debugging confidence, not benchmark validity. Public claims
should continue to cite this as `Codex draft adjudication`, not independent
manual adjudication.
