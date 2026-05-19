# Observability Protocol

The Observability Protocol specifies what CAP runtimes must emit so that
the other subsystems (Mirror, Looking-Glass, Context Hygiene,
Cross-Domain Drain, Release Gate, etc.) have evidence to work with. It
is the instrumentation contract.

---

## Purpose

> Observability Protocol guards CAP from operating blind.

A subsystem that has no telemetry to consume cannot enforce its
invariants. Mirror needs read-only observations to make a frame.
Cross-Domain Drain needs cost / progress signals. Release Gate needs an
audit trail. Anti-loop needs repeat counters. The protocol declares the
minimum set every CAP-instrumented runtime must export.

---

## Event categories (closed enum)

```text
mirror_observation        looking_glass_step
context_hygiene_decision  cross_domain_drain
subject_state_change      role_handoff
adjustment_step           verifier_verdict
release_gate_decision     anchor_decay_transition
cycle_transition          memory_dream_step
witness_record            authorization_event
boundary_violation        budget_event
```

---

## Required fields on every event

```text
event_id              opaque unique id
schema_version        e.g. "0.1"
event_kind            one of the event categories above
emitted_at            ISO timestamp
emitter               { kind: agent | tool | runtime | human, id }
scope                 { repo?, branch?, session_id?, role?, shell?, url? }
payload               typed per event_kind
provenance            array of source refs (never empty)
audit_log_ref         present iff event affects canonical state
```

---

## Export levels

| Level | Meaning | Default |
|---|---|---|
| `silent` | Suppressed entirely. Forbidden for canonical-affecting events. | no |
| `local` | Stored in process-local ring buffer; not exported. | yes |
| `comlog` | Written to the COM-Log; available to other CAP layers. | yes for governance events |
| `external` | Forwarded to an external sink (Grafana, Prometheus, etc.). | opt-in |

---

## Invariants

| Id | Statement | Enforcement |
|---|---|---|
| OBS-01 | Every event must carry provenance. | Schema requires `provenance` `minItems: 1`. |
| OBS-02 | Events that affect canonical state must include `audit_log_ref`. | If/then: `event_kind in {release_gate_decision, anchor_decay_transition, authorization_event}` requires `audit_log_ref`. |
| OBS-03 | Silent export is forbidden for canonical-affecting events. | If/then: same events forbid `export_level: silent`. |
| OBS-04 | Emitter identity is required. | `emitter.id` required and non-empty. |
| OBS-05 | Scope leaks are detected. | `scope` is a closed-properties object; `additionalProperties: false`. |
| OBS-06 | Event kinds are from the closed enum. | Schema enum. |
| OBS-07 | The protocol does not store conclusions; only typed payloads. | Schema rejects free-text `conclusion` fields. |

---

Schema at
[`../spec/observability_protocol.schema.json`](../spec/observability_protocol.schema.json);
worked example at
[`../examples/observability_event_example.json`](../examples/observability_event_example.json).
