# Anchor Decay

Anchor Decay specifies how canonical anchors lose authority over time.
An anchor is not eternal: it was valid against some evidence at some
time, and that evidence ages. The decay layer prevents stale anchors
from quietly overriding fresh evidence.

---

## Purpose

> Anchor Decay guards canonical memory from outliving its evidence.

The layer answers a single question:

> Is this anchor still load-bearing, or has it crossed into stale,
> deprecated, or expired status?

---

## Anchor lifecycle stages

| Stage | Meaning | Authority |
|---|---|---|
| `fresh` | Recent supporting evidence; full authority. | full |
| `aging` | Older than `aging_after_days` but no contradicting evidence yet. | full with watch flag |
| `stale` | Older than `stale_after_days`; downstream consumers must refresh before relying on it. | reduced |
| `deprecated` | Explicitly retired but kept for audit (L1-D). | audit-only |
| `expired` | Past its declared `valid_until`. | none |

---

## Decay drivers

```text
chronological_age      time since last_verified_at
domain_volatility      how fast facts in this domain change
contradiction_signal   new evidence contradicts the anchor
duplicate_anchor       a competing anchor was promoted
upstream_invalidation  the anchor's source was deprecated
schema_version_drift   the underlying schema changed
explicit_supersede     a supersede diff was approved
```

Decay does not delete. It changes the authority weight of an anchor and
routes consumers to refresh / supersede / quarantine when needed.

---

## Invariants

| Id | Statement | Enforcement |
|---|---|---|
| ADEC-01 | An anchor cannot be `fresh` without a `last_verified_at`. | Schema requires `last_verified_at` when `stage: fresh`. |
| ADEC-02 | `expired` requires `valid_until` in the past. | Schema requires `valid_until` for `expired`. |
| ADEC-03 | `deprecated` requires `superseded_by` OR `deprecation_reason`. | Schema requires at least one of the two. |
| ADEC-04 | A `stale` anchor cannot be referenced by a `release_candidate` without explicit refresh. | Doc invariant; downstream Release Gate check. |
| ADEC-05 | Decay cannot promote authority. | Stage transitions are one-way along `fresh -> aging -> stale -> deprecated -> expired`; reverse only via `explicit_refresh` operator. |
| ADEC-06 | Domain volatility must be declared. | Schema requires `domain_volatility` enum on every anchor decay record. |

---

## Schema

The full schema lives at
[`../spec/anchor_decay.schema.json`](../spec/anchor_decay.schema.json);
worked example at
[`../examples/anchor_decay_example.json`](../examples/anchor_decay_example.json).
