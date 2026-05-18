# Anti-loop / Context Hygiene

The Anti-loop / Context Hygiene layer manages the working context window:
classify each unit, prune noise, compress traces, quarantine
contamination, detect repeating failed routes, and force a route / role /
evidence-source change before the agent burns its budget in a loop.

---

## Purpose

> Context is not memory. Memory is not evidence. Evidence is not release.
> Release is not execution.

The layer guards three failure modes:

1. The agent repeats a non-working route.
2. Stale, foreign, or false context becomes the agent's current reality.
3. Model output becomes evidence without Mirror / Verifier / Release Gate.

If Mirror protects state `B` from hallucination and Looking-Glass
protects causality from elegant self-deception, Context Hygiene protects
the agent's working memory from turning into a swamp.

---

## Place in OCM

```text
User Intent
  -> Context Assembly
  -> Anti-loop / Context Hygiene
  -> Role Prompt / Agent Step
  -> Tool Execution / Reasoning
  -> Mirror / Looking-Glass
  -> Adjustment
  -> Verifier
  -> Release Gate
```

The layer is not a one-shot pre-answer filter. It runs continuously and
decides:

- what enters the next context window;
- what is dropped;
- what is compressed;
- what is marked stale;
- what is quarantined;
- when to switch route, role, or model;
- when continuing the cycle is futile.

---

## What counts as context waste

Old does not equal garbage. Garbage is context that lowers the quality
of the next transition.

| Kind | Example |
|---|---|
| `stale_tool_result` | green tests from before the latest diff |
| `duplicate_observation` | the same `git status` re-read for the third time |
| `failed_route_residue` | the old tool error keeps pulling the model into the same route |
| `self_generated_claim` | "I already checked", with no evidence |
| `unverified_summary` | summary contains conclusions a verifier never confirmed |
| `contradicted_anchor` | the unit contradicts a canonical anchor still in scope |
| `wrong_scope_context` | data leaks from a different task / fork / branch |
| `wrong_repo_context` | data leaks from a different repository |
| `wrong_shell_context` | bash output applied inside a PowerShell session |
| `wrong_browser_state` | hidden DOM treated as observed |
| `role_contamination` | the coder role starts auditing itself |
| `semantic_drift` | the task drifted from "fix save footer" to "redesign the UI" |
| `emotional_noise` | venting / drama that adds no signal |
| `excessive_trace` | giant tool output that hides the relevant 30 chars |
| `obsolete_plan` | the plan still references a step the new evidence retired |
| `futility_loop` | three attempts of the same class without new information |

---

## Data model

The full schema lives at
[`../spec/context_hygiene.schema.json`](../spec/context_hygiene.schema.json).
Key types:

```text
ContextUnit = {
  id, source, scope, content_hash, created_at, last_verified_at?,
  freshness, evidence_role, canonicality,
  relevance, risk, token_cost, reuse_count
}

ContextHygieneResult = {
  verdict, kept[], compressed[], dropped[], quarantined[],
  refresh_required[],
  loop_signals[], contamination_signals[],
  loop_break_actions[],
  token_accounting, recommended_next_action
}

ContextHygienePolicy = {
  prefer_minimal_sufficient_context (const true),
  allow_model_self_evidence (const false),
  allow_failed_route_as_instruction (const false),
  allow_candidate_memory_as_canonical (const false),
  summaries_must_preserve_provenance (const true),
  max_repeat_without_new_evidence,
  futility_escalation_token_threshold
}
```

The five policy constants reify the load-bearing invariants and cannot
be flipped at the schema level.

---

## Verdicts

| Verdict | Meaning |
|---|---|
| `healthy` | Context is fit for the next step. |
| `prune_recommended` | Excess weight present, not dangerous. |
| `stale_context` | Context is outdated and needs a Mirror refresh. |
| `loop_risk` | Repetition signals are appearing; the loop can still be broken softly. |
| `loop_detected` | One route / failure / hypothesis is repeating without new evidence. |
| `context_contamination` | Material from the wrong role / repo / branch / shell / memory state has entered the window. |
| `quarantine_required` | A block must be retained as contaminated evidence but cannot be canonical. |
| `futility_escalated` | Continuing the current route is futile without a strategy change. |
| `replan_required` | The plan must be reset and rebuilt from a Mirror Frame. |

---

## Loop signals (closed enum)

```text
same_tool_same_args_repeated
same_error_family_repeated
same_plan_rephrased
same_hypothesis_without_new_evidence
test_fix_cycle_without_diff_progress
route_retry_after_boundary_block
model_self_confirmation
summary_reinjects_rejected_claim
context_window_dominated_by_failed_trace
expanding_scope_without_resolution
```

## Contamination signals (closed enum)

```text
wrong_repo
wrong_branch
wrong_session
wrong_role
wrong_shell
wrong_time
wrong_user_intent
unverified_claim_as_fact
candidate_memory_as_canonical
failed_route_as_instruction
old_summary_overrides_recent_evidence
tool_error_exposed_as_context_anchor
```

The five most damaging in practice: `candidate_memory_as_canonical`,
`failed_route_as_instruction`, `wrong_repo`,
`old_summary_overrides_recent_evidence`, and
`tool_error_exposed_as_context_anchor`.

---

## Loop-break actions (closed enum)

When a loop is detected, the layer does not just emit "stop"; it
proposes an axis change. The closed action enum:

```text
refresh_mirror
run_looking_glass
switch_to_verifier
switch_to_scout
reduce_context
drop_failed_trace
quarantine_claim
change_tool_strategy
change_model
ask_for_human_authorization
stop_current_route
```

Rule: three attempts that differ only in wording count as one
attempt. Retry without new evidence is loop fuel, not persistence.

---

## Invariants

The schema enforces structural invariants directly. Tests enforce the
process invariants.

| Id | Statement | Enforcement |
|---|---|---|
| CH-01 | Context is not truth. | `evidence_role` field on every ContextUnit (5-way enum: evidence / claim / trace / noise / instruction). |
| CH-02 | Model output cannot become evidence without external support. | `policy.allow_model_self_evidence = const false`. |
| CH-03 | Failed-route residue must not become next-step instruction. | `policy.allow_failed_route_as_instruction = const false`. Signal `failed_route_as_instruction` is a contamination signal, not an instruction kind. |
| CH-04 | Stale evidence must be refreshed or demoted. | `freshness` field on every ContextUnit (`fresh` / `stale` / `unknown`). |
| CH-05 | Candidate memory cannot be injected as canonical memory. | `policy.allow_candidate_memory_as_canonical = const false`. `canonicality` field has separate `candidate` and `canonical` values. |
| CH-06 | Repetition without new evidence is a loop signal. | `verdict in {loop_risk, loop_detected}` requires `loop_signals minItems:1`. |
| CH-07 | Tool-result compression must preserve failure family and boundary context. | `ContextUnit.scope` is a structured object with `shell`, `repo`, `branch`, `role`, etc. Compression cannot collapse these into a string. |
| CH-08 | Quarantined context can be remembered as danger, not used as authority. | `quarantined[]` array is separate from `dropped[]`; quarantined items still appear in subsequent units with `canonicality: quarantined`. |
| CH-09 | Summaries must not resurrect rejected claims. | `policy.summaries_must_preserve_provenance = const true`. Process invariant; doc-level. |
| CH-10 | Hygiene prefers minimal sufficient context over maximal. | `policy.prefer_minimal_sufficient_context = const true`. Token accounting: `input_tokens_after <= input_tokens_before`. |
| CH-11 | Loop break must change at least one axis. | `verdict in {loop_detected, futility_escalated}` requires `loop_break_actions minItems:1`. |
| CH-12 | Futility escalation must happen before budget collapse. | `verdict: futility_escalated` requires `recommended_next_action` in `{stop_and_replan, ask_verifier}`. |

---

## Algorithm

```text
run_context_hygiene(context_window, current_task):
  1. Segment context into ContextUnits
  2. Attach scope (repo, branch, session, role, shell, url, timestamp)
  3. Classify each unit: evidence | claim | trace | noise | instruction
  4. Check freshness against latest diff / state / tool result
  5. Detect contamination
  6. Detect loop patterns
  7. Decide hygiene action per unit: keep | compress | drop | quarantine
       | refresh | revalidate
  8. Build CleanContextPack for the next step (minimal sufficient set)
  9. Emit COM telemetry: pruned tokens, quarantined units, verdict
  10. Route if needed: continue | Looking-Glass | Verifier | replan | stop
```

---

## Token accounting

The layer records what changed in the context window. The schema
requires:

```text
input_tokens_before
input_tokens_after          # <= input_tokens_before (CH-10)
prunable_tokens
cumulative_prunable_tokens?  # optional running total
```

Cumulative prunable is an estimate, not a billing guarantee: provider
caching and routing affect actual cost. The doc and schema flag the
field as `estimated`, not `guaranteed billing saved`.

---

## Relation to other layers

| Layer | Question | Hygiene complement |
|---|---|---|
| Mirror | What is observed? | Decide which observations to carry into the next window. |
| Looking-Glass | How did we get here? | Decide which parts of the prior trajectory are safe to keep. |
| Release Gate | May this candidate be released? | Reject any candidate built on stale / contaminated context. |
| Memory Dreaming | Compile candidate memory. | Hygiene runs upstream of Dreaming so the Dream Compiler sees a clean transcript. |
| Tool-result pruner | Save tokens. | Pruner is the executor; Hygiene is the policy that says what is safe to prune. |

A `release_candidate` whose evidence depends on an unhygienic context
trail must be flagged `needs_fix` until the Hygiene audit is rerun.

---

## Canonical formula

```text
Mirror sees what is real.
Looking-Glass explains how we got here.
Context Hygiene decides what context is safe to carry forward.
Adjustment plans the next transition.
Verifier checks the transition.
Release Gate decides whether it may become real.
```

Anti-loop guards the route. Context Hygiene guards the fuel.
