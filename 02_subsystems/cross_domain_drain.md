# Cross-Domain Drain

Cross-Domain Drain detects when an unresolved tension, error, or
parasitic structure in one domain starts consuming the budget of
another domain without producing verifiable progress.

---

## Purpose

> Cross-Domain Drain guards budgets from parasitic flow.

The layer answers a single question:

> Which domain is actually paying for this problem, and is there
> verifiable progress that justifies the cost?

It is not about "how much was spent". It is about whether the spend in
one domain (e.g. money / tokens) is buying progress in the domain
where the actual tension lives (e.g. semantic / context / boundary).

---

## Domains (closed enum)

```text
semantic   context   attention   token   compute   money
time       trust     memory      governance        runtime
repo       browser   social      emotional
```

Each tracked resource is one of these.

---

## Drain mechanisms (closed enum)

```text
semantic_ambiguity            context_contamination
loop_repetition               stale_evidence
wrong_boundary                wrong_role
wrong_model                   over_verification
under_specification           authority_confusion
memory_pollution              social_noise_capture
emotional_overweight          provider_cost_leak
runtime_retry_storm           browser_visibility_gap
release_gate_bypass_attempt
```

---

## Drain states (closed enum)

| State | Meaning |
|---|---|
| `no_drain` | Spend is proportional to verifiable progress. |
| `local_drain` | Resource is consumed in the domain where the problem lives. |
| `cross_domain_leak` | Origin domain ≠ drained domain. |
| `parasitic_drain` | A system loop keeps itself alive by consuming a foreign budget. |
| `cascade_drain` | The leak chained across multiple domains. |
| `contained` | Drain was detected and bounded. |
| `critical_budget_collapse` | Continuing is unsafe; stop / replan / human required. |

---

## Containment actions (closed enum)

```text
refresh_mirror          run_looking_glass        clean_context
quarantine_context      switch_role              switch_model_down
switch_model_up_for_verification                 cap_budget
freeze_scope            split_domain             require_explicit_goal
require_human_decision  block_release            rollback   hold
```

---

## Drain ratio

```text
drain_ratio = resource_spent / verified_progress
```

`verified_progress` is **not** "the model produced more text". Allowed
progress signals:

```text
new evidence found
uncertainty reduced
test changed status
boundary confirmed
anchor conflict resolved
rollback path found
release gate received the missing input
```

If `resource_spent` rises and `verified_progress` stays flat, the
verdict is at least `local_drain`; if the origin domain is different
from the drained one, it becomes `cross_domain_leak`.

---

## Invariants

| Id | Statement | Enforcement |
|---|---|---|
| CDD-01 | Resource consumption is not progress. | Schema requires both `estimated_cost` and `verified_progress` records on every drain event. |
| CDD-02 | Cross-domain cost must be attributed. | `state: cross_domain_leak` requires `origin_domain != drained_domain`. |
| CDD-03 | Low progress + repeated cost is a drain signal. | `verified_progress.new_evidence_count == 0` + non-zero spend forbids `state: no_drain`. |
| CDD-04 | Expensive models must not compensate for dirty context. | Mechanism `context_contamination` + recommended action `switch_model_up_for_verification` is rejected; must include `clean_context` or `quarantine_context`. |
| CDD-05 | Governance failures must not be retried as runtime failures. | Mechanism `authority_confusion` requires action `require_human_decision` or `block_release`. |
| CDD-06 | Browser visibility gaps must not be paid by live-write risk. | Mechanism `browser_visibility_gap` requires action `refresh_mirror` or `freeze_scope`. |
| CDD-07 | Candidate memory cannot drain trust by masquerading as canonical. | Mechanism `memory_pollution` requires action `quarantine_context` or `block_release`. |
| CDD-08 | Emotional importance must not upgrade weak evidence. | Mechanism `emotional_overweight` requires action `require_explicit_goal` or `hold`. |
| CDD-09 | Social noise must not override task scope. | Mechanism `social_noise_capture` requires action `freeze_scope` or `switch_role`. |
| CDD-10 | Drain containment must prefer boundary over brute force. | `state: critical_budget_collapse` requires action in `{hold, rollback, require_human_decision}`. |

---

Schema at
[`../spec/cross_domain_drain.schema.json`](../spec/cross_domain_drain.schema.json);
worked example at
[`../examples/cross_domain_drain_event_example.json`](../examples/cross_domain_drain_event_example.json).
