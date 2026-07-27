# Wire Lost, Model Blamed

**Unofficial draft. NON-CANONICAL provisional candidate. Not a canonical AICE code.**

See [the candidate surface README](./README.md) for the authority status of this directory.
This record reserves no number and defines no canonical code.

## Identity

| Field | Value |
|---|---|
| working_title | Wire Lost, Model Blamed |
| machine_name | `TRANSPORT_EVIDENCE_ERASURE_MODEL_MISATTRIBUTION` |
| status | `PROPOSED` |
| canonical_code | `UNASSIGNED` |
| canonical_number_reserved | `false` |
| operator_indicated_number | none — operator explicitly withheld a number pending ratification |
| source_class | `PRIMARY_PERSISTED` (mechanism) + `OPERATOR_ASSERTED_CLASS` (incident shape) |
| raw_trace_attached | `false` (probe records referenced by path) |
| collision_audit_result | `EXISTING_PARTIAL_MATCH` — [`AICE-614`](../codes/AICE-614.md) |

```
OPERATOR_INDICATED_NUMBER != REGISTRY_ASSIGNMENT
CANDIDATE_PRESENT         != CANONICAL_CODE_DEFINED
PARTIAL_MATCH             != COMPETING_CODE
```

No number is proposed. The operator's authority grant for this task explicitly excluded
automatic AICE ratification, and the registry's own claim — `AICE-601`…`AICE-621` defined,
`AICE-600` unassigned, `AICE-622` neither defined nor reserved — is unchanged by this file.

## Source and provenance limits

Two distinct evidence classes, deliberately not merged:

**Mechanism — `PRIMARY_PERSISTED`.** Direct probes of `ollama.com/v1/chat/completions` for
`minimax-m3` (session `91033b6c`, `scratchpad/probe/`) established that a provider can return
HTTP 200 with `[DONE]` seen and `finish_reason=length` while `delta.content` accumulates zero
bytes, because the payload went to a `delta.reasoning` channel the caller does not read. Measured:
34 237 reasoning characters, 0 content characters, 159 choice events.

**Incident shape — `OPERATOR_ASSERTED_CLASS`.** The claim that such an outcome is emitted as a
model-facing defect with attempt consumption and scoring effect is operator-reported. No
durable ledger row demonstrating a model penalty caused by an unresolved wire is attached to
this record.

**The name asserts two injuries. Only one is proven.**

```
WIRE LOST     PRIMARY_PERSISTED — measured. Transport evidence existed;
              the content projection erased it; the observable completion
              state became false-empty.

MODEL BLAMED  NOT ATTACHED — no durable artifact shows this unresolved wire
              state producing model_fault=true, a penalty, or an adverse
              routing decision.

FULL CLASS    NOT ESTABLISHED
```

The parser defect on its own is therefore **not** an exemplar of this class. It satisfies
predicates 1–4 and leaves 5–6 open. A dossier whose title names two damages may not be sealed on
one; that is the same error this class exists to name.

Explicit non-claim, per operator instruction:

```
The measured probe establishes the MECHANISM.
It does NOT establish the CAUSE of any historical invocation.
A mechanism reproduced under one set of conditions is not the cause
of an incident that ran under materially different conditions.
```

## Core definition

A transport or protocol parser discards, ignores, fails to preserve, or cannot interpret direct
wire evidence, and the resulting absence, malformedness, or ambiguity is then emitted as a
model-attributed outcome that affects attempt consumption, scoring, routing, verdict, or
terminal state.

## Trigger predicates — all required

1. `PROVIDER_INVOCATION_OCCURRED` — a real provider/transport invocation started.
2. `MODEL_COMPLETION_NOT_PROVEN` — a valid terminal model completion was not established.
3. `WIRE_OR_PROTOCOL_EVIDENCE_LOST_OR_UNRESOLVED` — relevant response, frame, channel, partial
   content, HTTP error body, terminal state, or parser failure was discarded, ignored, or left
   unresolved.
4. `ABSENCE_OR_MALFORMEDNESS_SUBSTITUTED` — the system substituted the absence of *recognized*
   actionable output for a claim about *model behaviour*.
5. `MODEL_ATTRIBUTION_EMITTED` — the result was classified as model empty output, schema
   failure, malformed answer, or another model-facing defect.
6. `AUTHORITY_EFFECT` — the attribution consumed an attempt, changed routing, created a penalty,
   affected a verdict, or entered durable actor history.

Canonical negative boundary:

```
NO_PROVEN_COMPLETION
→ NO_MODEL_ATTRIBUTION
```

## Forbidden inference

```
PARSER_RECOGNIZED_NOTHING   != MODEL_PRODUCED_NOTHING
ZERO_BYTES_IN_ONE_CHANNEL   != ZERO_BYTES_ON_THE_WIRE
UNREAD_CHANNEL              != ABSENT_CHANNEL
ABSENCE_OF_OBSERVATION      != OBSERVATION_OF_ABSENCE
```

## Required terminal / required response

Classify as transport/protocol/system evidence failure, or `UNKNOWN`. Do not penalize the model;
do not attribute empty or malformed output to it. Preserve bounded wire provenance: HTTP status;
content type; wire bytes and hash; event counters; terminal evidence; partial-output bytes and
hash; parser failure class — secrets excluded. Model attribution is permitted only after terminal
model completion is proven.

## Positive example

HTTP 200 is received. The body carries an error envelope, an unsupported delta shape, a
reasoning-only channel, a damaged SSE frame, or another form not proven to be a terminal
actionable model completion. The parser recognizes no actionable `delta.content`. The system
emits `EMPTY_COMPLETION` or `SCHEMA_INVALID` with `model_fault=true`, and/or `attempt_spent=true`,
and/or a scoring penalty.

Positive **only** where model completion was not proven.

## False-positive boundary — negative controls

1. A valid terminal completion is proven and the model's returned JSON is malformed
   → legitimate model/schema outcome.
2. A valid terminal completion is proven empty with a supported `finish_reason` and no
   unresolved protocol evidence → legitimate `EMPTY_COMPLETION`.
3. Provider reports `finish_reason=length`, evidence is preserved, and the system records
   `OUTPUT_TRUNCATED` without model blame → not this class.
4. Transport evidence is missing, but the system reports `UNKNOWN` or `SYSTEM_OR_POLICY` and does
   not affect model score or blame → evidence gap, no misattribution.
5. Logging omits diagnostic details, but verdict, score, attempt budget, and actor attribution
   are unaffected → observability defect, not this class.
6. An ignored auxiliary reasoning channel consumes output budget and the system records it
   correctly as non-actionable channel starvation → adjacent candidate, not this class.

## Comparison with nearby canonical codes

| Code | Relationship |
|---|---|
| [`AICE-614`](../codes/AICE-614.md) | **Closest match — partial, not equivalent.** Same genus: a non-semantic failure acquires an authority it never earned. Not the same species. 614's trigger predicate 1 is mandatory and reads "a semantic verifier review was required or claimed" ([AICE-614.md:283](../codes/AICE-614.md)), and its fabricated output is a *semantic verdict about the work* attributed to a *verifier* ([:289](../codes/AICE-614.md)). This candidate fires with **no verifier and no semantic review anywhere in the episode** — a coder invocation is enough — and its fabricated output is a *performance claim about the actor* (`model_fault`, penalty, attempt consumption). Absorbing this into 614 would require broadening predicate 1 from "verifier semantic review" to "any provider invocation", which changes what 614 means. Explicitly not proposed. |
| [`AICE-612`](../codes/AICE-612.md) | 612 transfers one actor class's path result to a different actor class. Here there is one actor and one path; the defect is inventing a fact about that actor, not transferring one across actors. |
| [`AICE-621`](../codes/AICE-621.md) | 621 is admission of a task whose minimum deliverable cannot fit the output channel. It concerns *capacity at admission*; this candidate concerns *attribution after the fact*. They can chain: a capacity contradiction produces the unreadable outcome that then gets misattributed. |
| [`AICE-606`](../codes/AICE-606.md) | 606 is a PASS with no test-run receipt. Here no PASS is claimed; a failure is claimed, against the wrong party. |
| `ATTEMPT_CONSUMPTION_OUTCOME_EVIDENCE_GAP` (candidate) | **Complementary opposites, co-emitting.** That candidate fires when an attempt is spent and *no* durable outcome receipt exists. This one fires when a receipt exists and *says the wrong thing*. Silence versus false testimony. |
| `UNACCOUNTED_AUXILIARY_CHANNEL_OUTPUT_STARVATION` | Deliberately **not** merged — see below. Not added by this task. |

## Why auxiliary-channel starvation is not absorbed

They differ in both the mechanism and the injured party:

```
STARVATION            a shared generation budget is consumed by a non-actionable
                      channel, so the actionable channel is truncated or empty.
                      The injury is to the OUTPUT. It occurs even if attribution
                      is later recorded perfectly.

THIS CANDIDATE        evidence about what happened is lost or uninterpreted, and
                      the gap is filled with a claim against the model.
                      The injury is to the ATTRIBUTION. It occurs even when no
                      auxiliary channel exists at all — a dropped HTTP error body
                      is sufficient.
```

Neither entails the other. Merging them would produce a class that fires on every mismeasured
outcome and discriminates nothing.

## Portable CAP enforcement requirement

Any CAP-governed runtime that records actor-attributed outcomes must be able to answer, from
durable evidence alone, whether a recorded model fault rests on a proven terminal completion. A
runtime that cannot distinguish "the model returned nothing" from "we could not read what the
model returned" must record `UNKNOWN` and must not decrement an attempt budget against the actor.

## Promotion gate

Blocking conditions:

1. **A durable incident instance.** Predicates 5 and 6 are currently `OPERATOR_ASSERTED`. A
   ledger row showing a model penalty or attempt consumption traceable to an unresolved wire is
   required. The measured probe supports predicates 2–4 only.
2. **Independent review of the AICE-614 boundary.** The partial-match analysis above is authored
   by the same actor proposing the candidate.
3. **Explicit operator ratification of a number.** None is proposed here.
4. **A negative-control episode** where transport evidence was lost and the system correctly
   recorded `UNKNOWN`, confirming the class discriminates.

## Verification status

```
COLLISION AUDIT           PERFORMED — EXISTING_PARTIAL_MATCH (AICE-614)
MECHANISM                 PRIMARY_PERSISTED (measured probe)
INCIDENT INSTANCE         NOT ESTABLISHED
HISTORICAL CAUSATION      NOT CLAIMED
INDEPENDENT REVIEW        NOT PERFORMED
NUMBER                    NOT PROPOSED, NOT RESERVED
CANONICAL PROMOTION       NOT AUTHORIZED
```
