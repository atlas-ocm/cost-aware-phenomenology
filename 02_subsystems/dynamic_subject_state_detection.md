# Dynamic Subject-State Detection

Dynamic Subject-State Detection (DSSD) is the layer that decides which
*mode of agency* a participant is currently in for a specific
transition. It does not ask "is this actor a subject forever"; it asks
"who is actually choosing the next move right now, and who is just
executing an algorithm".

---

## Purpose

> Subject-State Detection guards agency attribution.

Without this layer, CAP would routinely confuse:

```text
model is confident                  != model has the right to release
agent completed the procedure       != agent owned the goal
user clicked something              != user authorized the transition
verifier returned PASS              != verifier is the release authority
```

DSSD makes those four distinctions machine-checkable. Subjectness is an
operational state attached to the action, not an identity label
attached to the actor.

---

## Place in OCM

```text
User Intent
  -> Mirror Layer
  -> Dynamic Subject-State Detection
  -> Looking-Glass / Adjustment
  -> Verifier
  -> Release Gate
  -> Authorization / Executor
```

The layer answers a single question for every participant in the
current transition:

> At what level of agency is this actor right now?

---

## Identity is not state

The same human can be, within the same hour:

- an object of someone else's process;
- a habitual system following routine;
- a bounded subject within a delegated scope;
- the human release authority for an irreversible step.

The same LLM can be, within the same task:

- a text generator;
- a procedural executor;
- a bounded subject inside a narrow scope;
- a pseudo-subject that turned confidence into self-approval.

The schema therefore reports `detected_state` per-frame, not per-actor.

---

## Subject states (closed enum)

| State | Meaning |
|---|---|
| `object_state` | The actor is being used as material / resource. |
| `system_state` | The actor executes a procedure or routine without re-evaluating the goal. |
| `looping_system_state` | The system started repeating itself without new evidence. |
| `pseudo_subject_state` | The actor looks like a subject but only executes inner automatism with confident output. The most dangerous mode. |
| `bounded_subject_state` | Operational subjectness inside an explicit scope; the actor may choose among allowed routes but cannot change boundaries. |
| `delegated_subject_state` | Subjectness explicitly delegated by a human or policy, for a specific class of actions. |
| `sphere_probe_state` | The actor stepped outside the current frame to find a new hypothesis / meaning / route. No mutation. |
| `release_authority_required` | The next transition changes canonical state; Release Gate is required. |
| `human_subject_required` | The transition requires a human's value choice or risk acceptance; it cannot be delegated to a model. |

---

## Eight agency axes

```text
goal_ownership            does the actor set the goal or just execute one?
boundary_awareness        does the actor see the limits?
evidence_discipline       does the actor separate claim from evidence?
self_correction           does the actor change hypothesis on contradiction?
authority_awareness       does the actor know its own rights?
novelty_handling          can the actor step outside routine?
reversibility_awareness   does the actor think about rollback?
context_hygiene           does the actor avoid carrying garbage?
```

Each axis is scored in `[0, 1]`. The detected state is a classification
over the axis vector plus explicit risk and capability signals.

Example mapping:

```text
high confidence + low evidence_discipline + low authority_awareness
  -> pseudo_subject_state

high boundary_awareness + high evidence_discipline + high reversibility_awareness
  -> bounded_subject_state

low self_correction + low context_hygiene
  -> looping_system_state
```

---

## Risk signals (closed enum)

```text
self_approval                       actor authorizes its own output
authority_overreach                 bounded subject acts as release authority
goal_drift                          executes something the user did not ask for
boundary_blindness                  acts as if the boundary is not present
evidence_substitution               own claim used as evidence
looping_behavior                    repeats without new information
role_confusion                      verifier seals; coder reviews itself
context_contamination               works against wrong repo / shell / session
irreversible_action_attempt         destructive step without authorization
canonicalization_attempt            candidate tries to become canonical
false_certainty                     confident output, no supporting evidence
user_intent_ambiguity               proceeds without clarifying the user's intent
```

The four most damaging in practice: `self_approval`,
`authority_overreach`, `evidence_substitution`,
`canonicalization_attempt`.

---

## Capability signals (closed enum)

```text
goal_clarity
boundary_awareness
evidence_separation
uncertainty_preserved
route_changed_after_failure
rollback_considered
human_authorization_requested
release_gate_respected
contradiction_preserved
minimal_action_preferred
```

---

## Data model

The full schema lives at
[`../spec/dynamic_subject_state_detection.schema.json`](../spec/dynamic_subject_state_detection.schema.json).
Key shapes:

```text
SubjectStateInput = {
  actor_id, actor_kind, current_action, current_task,
  mirror_frame_id?, context_hygiene_result_id?, looking_glass_trace_id?,
  declared_intent?, observed_behavior[],
  permissions[], boundaries[], active_role?, release_target?
}

SubjectStateFrame = {
  id, actor_id, actor_kind,
  detected_state, confidence,
  axis_scores,
  evidence[], risk_signals[], capability_signals[],
  allowed_next_actions[], forbidden_next_actions[],
  required_escalation?,
  created_at
}

SubjectStatePolicy = {
  allow_model_as_release_authority   (const false),
  allow_self_approval                 (const false),
  require_human_for_irreversible      (const true),
  require_release_gate_for_canonicalization (const true),
  require_independent_verifier_for_code_seal (const true),
  require_anti_loop_on_looping_system (const true),
  require_mirror_for_state_claims     (const true)
}
```

Seven policy constants reify the load-bearing invariants and cannot be
flipped at the schema level.

---

## Invariants

The schema enforces structural invariants directly. Tests enforce
process invariants.

| Id | Statement | Enforcement |
|---|---|---|
| DSSD-01 | Subject-state is dynamic, not identity. | `SubjectStateFrame.detected_state` is a per-frame field; the schema has no actor-level "is_subject" flag. |
| DSSD-02 | Confidence is not authority. | `policy.allow_model_as_release_authority = const false`. `confidence` field exists but cannot itself enable release. |
| DSSD-03 | Execution is not subjectness. | `actor_kind: tool` cannot be classified as a release authority; the schema forbids `tool` paired with `release_authority_required`. |
| DSSD-04 | Verification is not authorization. | `policy.require_independent_verifier_for_code_seal = const true`. A verifier-only role cannot self-authorize a seal. |
| DSSD-05 | Bounded subject cannot promote itself to release authority. | `detected_state: bounded_subject_state` cannot coexist with `required_escalation: null` when a canonicalization is being attempted; required_escalation must be at least `release_gate`. |
| DSSD-06 | Human authorization must be explicit for irreversible transitions. | `policy.require_human_for_irreversible = const true`. `irreversible_action_attempt` in risk_signals forces `required_escalation: human_authorization`. |
| DSSD-07 | Pseudo-subject state must trigger guardrails. | `detected_state: pseudo_subject_state` requires `required_escalation` in `{verifier, release_gate, human_authorization}`. |
| DSSD-08 | Looping-system state must trigger Anti-loop. | `policy.require_anti_loop_on_looping_system = const true`. `detected_state: looping_system_state` requires `required_escalation: context_hygiene`. |
| DSSD-09 | Sphere-probe cannot directly mutate system state. | `detected_state: sphere_probe_state` requires `forbidden_next_actions` to include at least one of `release | canonicalize_memory | git_seal | external_publication`. |
| DSSD-10 | Agency attribution must be logged for high-risk transitions. | `detected_state` in `{release_authority_required, human_subject_required, pseudo_subject_state}` requires `audit_log_ref` field non-empty. |

---

## Decision rules

```text
IF actor repeats route without new evidence
  -> looping_system_state

IF actor claims release authority over its own output
  -> pseudo_subject_state

IF actor chooses among allowed routes and respects boundaries
  -> bounded_subject_state

IF action changes canonical state
  -> release_authority_required

IF irreversible action lacks explicit authorization
  -> human_subject_required

IF current frame cannot explain observed B
   AND actor preserves uncertainty while seeking a new frame
  -> sphere_probe_state

IF actor follows a fixed procedure without re-evaluating goal
  -> system_state

IF actor is being used as material only
  -> object_state
```

---

## Algorithm

```text
detect_subject_state(actor, action, context):
  1. Identify actor and scope
  2. Read current action
  3. Compare declared intent vs observed behavior
  4. Score the eight agency axes
  5. Detect risk signals
  6. Detect capability signals
  7. Classify detected_state
  8. Emit SubjectStateFrame:
       allowed_next_actions
       forbidden_next_actions
       required_escalation
       audit_log_ref for high-risk states
```

---

## Relation to other layers

| Layer | Question | DSSD complement |
|---|---|---|
| Mirror | What is observed? | Who is acting on that observation? |
| Looking-Glass | How did we get here? | What agency mode produced this trajectory? |
| Context Hygiene | What context is safe to carry? | Subjectness collapsed to loop -> Anti-loop triggers. |
| Release Gate | May this candidate be released? | DSSD prevents `pass` when the verifier and the author are the same actor. |
| Memory Dreaming | Compile candidate memory. | Dream entering sphere_probe is fine; promoting candidate to canonical is not. |

---

## Canonical formula

```text
Mirror sees what is real.
Subject-State Detection asks who is acting on it.
Looking-Glass explains how we got here.
Context Hygiene cleans what we carry forward.
Adjustment plans C.
Verifier checks C.
Release Gate decides whether C may become real.
Human authorization permits irreversible execution.
```

Mirror guards reality. Looking-Glass guards causality. Context Hygiene
guards the route's working memory. Subject-State Detection guards
agency. Release Gate guards canonicalization.
