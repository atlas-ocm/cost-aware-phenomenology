# Cycle State Machine

The Cycle State Machine is the canonical FSM that node states follow
across CAP cycles. It is referenced informally by Observer Budget,
Operator Admissibility, and COM Grammar; this doc and the paired schema
make it explicit.

---

## Purpose

> Cycle State Machine guards the lifecycle of a tracked node.

A node is anything CAP tracks across cycles: a request, an anchor, an
operator instance, a memory candidate. Each node moves through a closed
set of states; transitions are typed; some transitions require external
approval.

---

## States (closed enum)

| State | Meaning |
|---|---|
| `pending` | Declared but not yet evaluated by an operator. |
| `active` | An operator is currently running on the node. |
| `on_hold` | Deferred due to budget exhaustion, evidence wait, or external dependency. |
| `closed` | Operator completed; outcome accepted. |
| `resolved` | Closed AND its downstream effects confirmed. |
| `dropped` | Marked irrelevant; no further work scheduled. |
| `reopened` | Closed/resolved/dropped node returned to active for re-evaluation. |
| `quarantined` | Marked contaminated or contradictory; not used as authority. |

---

## Transitions (closed enum)

```text
declare        ()             -> pending
schedule       pending        -> active
hold           active|pending -> on_hold
resume         on_hold        -> active
close          active         -> closed
resolve        closed         -> resolved
drop           pending|on_hold-> dropped
reopen         closed|resolved|dropped -> reopened
quarantine     any            -> quarantined
```

Transitions that change canonical state (`close`, `resolve`,
`quarantine`, `reopen`) require an audit log reference.

---

## Invariants

| Id | Statement | Enforcement |
|---|---|---|
| CSM-01 | A node has exactly one current state at any time. | Schema field; per-node singleton. |
| CSM-02 | Closed cannot become active directly; it must `reopen` first. | Transition enum. |
| CSM-03 | Quarantined cannot transition back to active without explicit `reopen`. | Transition enum. |
| CSM-04 | Hold transitions must record a reason. | Schema requires `hold_reason` non-empty for `on_hold`. |
| CSM-05 | Reopen requires audit_log_ref. | If-then in schema. |
| CSM-06 | Dropped cannot become closed without reopen. | Transition enum. |

---

## Relation to other layers

| Layer | Relation |
|---|---|
| Observer Budget | Hold is what happens when `TotalRisk > AllowedTotalRisk`. |
| Operator Admissibility | Active is the state where an operator is running. |
| Memory Dreaming | Candidate memory states map to `pending` / `on_hold`. |
| Release Gate | `close` of a release candidate requires gate `pass`. |

The schema lives at
[`../spec/cycle_state_machine.schema.json`](../spec/cycle_state_machine.schema.json);
the worked example is
[`../examples/cycle_node_example.json`](../examples/cycle_node_example.json).
