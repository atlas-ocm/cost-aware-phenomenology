# Role Orchestration

Role Orchestration is the layer that distributes *bounded operational
functions* across roles. It does not herd a crowd of agents; it decides
which role must currently see, diagnose, clean, plan, mutate, verify,
release, authorize, or execute, and it forces typed hand-offs between
those roles.

---

## Purpose

> Role Orchestration guards the separation of functions.

> Role is not agent identity. Role is a bounded operational function.

The layer answers a single question for every step in the OCM
pipeline:

> Who must do the next move, with what rights, with what context, and
> to whom must they hand the result?

The default failure mode it prevents is the single-actor cycle:

```text
coder -> coder -> coder -> PASS -> seal
```

Even when the actor is correct, that pipeline is structurally
inadmissible. The layer rewrites it into:

```text
observer / scout -> diagnostician -> context_hygienist -> planner
  -> coder -> verifier -> release_governor -> human_authority -> executor
```

---

## Place in OCM

```text
User Intent
  -> Dynamic Subject-State Detection
  -> Role Orchestration
  -> Mirror / Looking-Glass / Context Hygiene / Adjustment / Coder / Verifier
  -> Release Gate
  -> Authorization / Executor
```

Role Orchestration does not replace any of the layers it routes
through. It selects which role and layer must activate next.

---

## Roles (closed enum)

| Role | Purpose | May mutate | May verify | May release | May authorize |
|---|---|---|---|---|---|
| `observer` | Read-only state snapshot. | no | no | no | no |
| `scout` | Read-only search for evidence, files, prior cases. | no | no | no | no |
| `diagnostician` | Reconstruct A from B (Looking-Glass). | no | no | no | no |
| `context_hygienist` | Classify / compress / quarantine context. | no | no | no | no |
| `planner` | Build a CandidateTransition (Adjustment). | no | no | no | no |
| `architect` | Propose a frame change when local repair is insufficient. | no | no | no | no |
| `coder` | Implement a candidate patch within scope. | yes (candidate) | no | no | no |
| `uiux` | UI / presentation / copy / layout within UI scope only. | yes (UI only) | no | no | no |
| `verifier` | Independent check of a candidate. | no | yes | no | no |
| `cap_checker` | Boundary, role-contamination, release-risk review. | no | yes | no | no |
| `release_governor` | Apply Release Gate policy; emit `pass / needs_fix / blocked`. | no | no | yes (process) | no |
| `executor` | Carry out an already-authorized action. | yes (only after release + authorization) | no | no | no |
| `human_authority` | Explicit human approval of irreversible / canonical transitions. | no | no | no | yes |
| `fallback` | Used only when no other role applies; must escalate. | no | no | no | no |

---

## Role actions (closed enum)

```text
read | search | mirror | diagnose | clean_context | plan |
edit | test | verify | release_review | authorize | execute | rollback
```

---

## Orchestration mode

```text
manual         user switches roles
suggest        layer recommends, user confirms
guarded_auto   read-only roles auto-switched; mutating/release/authorize need user
auto           full automation; reserved for telemetry-mature deployments
```

For a v0 of any CAP-style runtime, the recommended default is
`suggest`: never auto-switch into a mutating role.

---

## Decision modes (closed enum)

```text
continue_current_role
switch_role
parallel_review
escalate
hold
```

---

## Data model

The full schema lives at
[`../spec/role_orchestration.schema.json`](../spec/role_orchestration.schema.json).

```text
RoleProfile = {
  role, purpose,
  allowed_actions[], forbidden_actions[],
  allowed_scopes[], forbidden_scopes[],
  input_requirements[], output_contract[],
  may_mutate, may_verify, may_release, may_authorize,
  max_autonomy
}

RoleHandoffPacket = {
  from_role, to_role, task_intent,
  input_state_refs (mirror_frame_id?, looking_glass_trace_id?,
                    context_hygiene_result_id?, adjustment_id?,
                    verifier_verdict_id?),
  summary,
  evidence_refs[],
  open_questions[],
  rejected_hypotheses[],
  allowed_next_actions[], forbidden_next_actions[],
  scope (files?, repo?, branch?, browser_url?, memory_store?),
  requires_return_to_role?
}

RoleOrchestrationDecision = {
  selected_role, reason, mode,
  handoff?,
  required_before_next_step[],
  forbidden_until_satisfied[],
  confidence
}

RoleOrchestrationPolicy = {
  mode (manual | suggest | guarded_auto | auto),
  allow_auto_read_only_switch,
  allow_auto_mutating_switch,
  allow_self_approval                    (const false),
  require_independent_verifier            (const true),
  require_release_gate_for_canonical      (const true),
  require_human_for_irreversible          (const true),
  enforce_role_scope                      (const true),
  preserve_handoff_evidence               (const true),
  interrupt_loops                         (const true)
}
```

Seven policy constants reify the load-bearing invariants.

---

## Invariants

The schema enforces structural invariants directly. Tests enforce
process invariants.

| Id | Statement | Enforcement |
|---|---|---|
| RO-01 | A role cannot expand its own authority. | `policy.allow_self_approval = const false`. The schema has no field through which a role grants itself release or mutate rights. |
| RO-02 | Author and final verifier must be separated. | `policy.require_independent_verifier = const true`. Handoff with `from_role == to_role` is rejected when the target role is `verifier` or `release_governor`. |
| RO-03 | Verifier is read-only. | `role: verifier` in any RoleProfile requires `may_mutate: false` and `may_release: false`. |
| RO-04 | Release Governor does not execute physical seal. | `role: release_governor` requires `may_authorize: false`. The release governor emits process verdicts, not physical actions. |
| RO-05 | Human authorization is required for irreversible transitions. | `policy.require_human_for_irreversible = const true`. A handoff whose `allowed_next_actions` contains `execute` must have `to_role: executor` AND `requires_return_to_role: human_authority`. |
| RO-06 | Handoff must preserve evidence, constraints, and rejected hypotheses. | `policy.preserve_handoff_evidence = const true`. RoleHandoffPacket requires `evidence_refs minItems:1` and `rejected_hypotheses` as a required array. |
| RO-07 | Role switch must not launder contaminated context. | Schema requires every handoff to reference at least one `input_state_refs.*` so the next role inherits the audit trail; `additionalProperties: false` rejects free-text replacements. |
| RO-08 | Read-only roles may be auto-suggested more freely than mutating roles. | `policy.allow_auto_read_only_switch` is a free knob; `policy.allow_auto_mutating_switch` defaults to `false`. |
| RO-09 | UI/UX scope must not leak into runtime / governance scope. | `policy.enforce_role_scope = const true`. `role: uiux` profile must include `runtime` / `governance` / `cap_runtime` in `forbidden_scopes`. |
| RO-10 | Role Orchestration emits routing decision, not truth. | `RoleOrchestrationDecision` has no `passes_release` / `evidence_validated` field. The decision authorizes routing, not quality. |
| RO-11 | Looping role must be interrupted. | `policy.interrupt_loops = const true`. `decision.mode: continue_current_role` is forbidden when an attached `loop_signal_count > 0`. |
| RO-12 | Role outputs must be typed. | Each RoleProfile carries `output_contract[]`; the schema requires this array minItems:1, naming the concrete artifact the role produces. |

---

## Algorithm

```text
orchestrate_next_role(input):
  1. Read current state: mirror frame, context hygiene, subject state,
     looking-glass, adjustment, verifier verdict, release gate result.
  2. Apply rule table:
       - state unknown                -> observer / scout
       - B exists, A unclear          -> diagnostician
       - context stale / contaminated -> context_hygienist
       - B and A known, C not planned -> planner
       - candidate exists, mutation needed -> coder | uiux (by scope)
       - patch exists                 -> verifier
       - verifier pass, release target exists -> release_governor
       - irreversible / canonical     -> human_authority
       - role attempts self-approval  -> switch to verifier; flag risk
  3. Build typed handoff:
       - copy evidence_refs
       - copy rejected_hypotheses
       - declare allowed and forbidden next actions
       - scope locked to relevant files / repo / memory
  4. Emit RoleOrchestrationDecision:
       selected_role, mode, reason, handoff, requires_before / forbidden_until
  5. No mutation. No release. No authorization.
```

---

## Relation to other layers

| Layer | Question | Role Orchestration complement |
|---|---|---|
| Dynamic Subject-State Detection | What agency state is each actor in? | Which role is permitted next? |
| Mirror | What is observed? | Should we route to observer / scout for refresh? |
| Looking-Glass | How did B happen? | Diagnostician role activated. |
| Context Hygiene | What context is safe? | Context hygienist activated on contamination. |
| Adjustment | What route is admissible? | Planner activated; coder receives bounded handoff. |
| Verifier | Is the candidate good? | Verifier role required separate from author. |
| Release Gate | May this be released? | Release governor inspects the role trail (author != verifier). |
| Human authority | Explicit authorization for irreversible / canonical. | Final escalation target. |

---

## COM-Log statuses

```text
RoleAssigned
RoleSwitchSuggested
RoleSwitchApplied
RoleHandoffCreated
RoleConflictDetected
RoleAuthorityBlocked
RoleSelfApprovalBlocked
RoleScopeViolation
RoleEscalationRequired
RoleLoopInterrupted
```

---

## Model routing is not role orchestration

Model routing answers "which model do we use". Role Orchestration
answers "which function is needed". A `verifier` role may run on one
model, a `uiux` role on another; the role is chosen first, the model
is selected to fit the role.

---

## Canonical formula

```text
Mirror sees B.
Looking-Glass explains how B happened.
Context Hygiene cleans the working memory.
Subject-State Detection identifies who is acting.
Role Orchestration decides which role must act next.
Adjustment plans C.
Verifier checks C.
Release Gate decides whether C may become real.
Human Authority permits irreversible execution.
```

Role Orchestration does not let one agent be god, judge, builder, and
notary at once.
