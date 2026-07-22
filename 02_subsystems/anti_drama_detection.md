# Anti-drama Detection

Anti-drama Detection separates narrative pressure from real signal. It
formalizes the principle already declared in Observer Budget:
*importance does not increase budget*. This layer makes the principle
detectable, not just stated.

---

## Purpose

> Anti-drama Detection guards CAP from upgrading evidence by emotion.

A claim does not become true because the speaker insists. A risk does
not become safe because the actor is desperate to act. A budget does
not grow because the stakes feel high. Anti-drama flags moments where
narrative force is being substituted for evidence.

---

## Drama signals (closed enum)

```text
emphasis_inflation           urgent / critical / must / cannot wait
moral_loading                should / ought / disgrace / shame
identity_invocation          calling on who someone is to justify what to do
sunk_cost_invocation         "we have already invested so much"
fate_framing                 "this is meant to be"
existential_collapse         "everything depends on this"
contempt_payload             dismissing alternatives without analysis
narrator_self_promotion      framing the speaker as uniquely capable
audience_capture             optimizing for audience reaction, not state
adversary_construction       inventing an enemy to justify an action
```

These are the surface signals. The layer never claims the underlying
emotion is invalid; it claims the emotion has not produced evidence.

---

## Drama verdicts (closed enum)

| Verdict | Meaning |
|---|---|
| `no_drama` | Signal-to-narrative ratio is normal. |
| `narrative_pressure_detected` | Signals present, but evidence still load-bearing. |
| `drama_inflation` | Emotion is the primary driver; evidence is secondary. |
| `drama_overrides_evidence` | The claim contradicts available evidence and rests on narrative force. |
| `drama_demands_budget_increase` | Speaker asks for more budget on the strength of importance, not evidence. |

---

## Recommended actions (closed enum)

```text
proceed
downweight_emotional_signal
require_evidence_for_claim
require_explicit_goal
freeze_budget
hold
escalate_to_human
```

The defining response to drama is **not** "ignore the speaker"; it is
"the speaker still owes evidence". Anti-drama is not contempt; it is a
discipline of cost.

---

## Invariants

| Id | Statement | Enforcement |
|---|---|---|
| DRAMA-01 | Importance does not increase observer budget. | `verdict: drama_demands_budget_increase` requires action in `{freeze_budget, hold, escalate_to_human}`. |
| DRAMA-02 | A drama signal alone does not invalidate a claim. | A claim is only downgraded when the verdict is `drama_overrides_evidence` AND a contradicting evidence ref is attached. |
| DRAMA-03 | Drama detection records evidence refs, not emotional judgements. | `evidence_refs` array required (may be empty for `no_drama`); a `narrative_pressure_detected` or stronger verdict requires `minItems:1`. |
| DRAMA-04 | Drama detection cannot itself release or canonicalize anything. | Schema has no release/canonicalize field. |
| DRAMA-05 | The same actor cannot self-clear a drama verdict. | `cleared_by` (when present) must not equal `emitter.id`. |

---

Schema at
[`../spec/anti_drama_detection.schema.json`](../spec/anti_drama_detection.schema.json);
worked example at
[`../examples/anti_drama_event_example.json`](../examples/anti_drama_event_example.json).
