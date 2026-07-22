# AICE-609 — Consensus Exists, Evidence Not Found

**Unofficial draft (AICE v0.1.0).**

## Canonical identifier

`AICE-609`

## Human-readable alias

`HTTP 609 — Consensus Exists, Evidence Not Found`

## Intent

Catch the case where multiple agents or models agree on a claim, but none has observed
the required event or postcondition.

Canonical principle:

> Consensus is not evidence.

## Trigger condition

Multiple agents or models agree on a claim, and none has observed the required event or
postcondition.

## Required observations

At least one participating actor must have observed the required event or postcondition
directly — the same evidence any single-actor claim would require (a receipt, a
readback, an independent inspection).

## Missing-evidence condition

Agreement is presented as the basis for acceptance, but no participant inspected the
required event or postcondition; the consensus rests only on shared narrative.

## False-positive guards

Consensus may contribute to prioritization or hypothesis ranking, but cannot replace
required physical evidence.

## Workflow semantics

```
STATE_UNCHANGED
REQUEST_EVIDENCE
```

Agreement alone MUST NOT advance workflow state; the missing evidence MUST be requested.

## Remediation

Obtain the required physical evidence from at least one actor that actually observed the
event or postcondition. Additional agreement does not resolve the incident.
Retryability: `requires_new_evidence`.

## Example

```
CLAIM: "three agents agree the file was written"
observed_evidence: []            # no actor read the bytes
missing_evidence: readback, write_event
workflow_effect: STATE_UNCHANGED, REQUEST_EVIDENCE
```

## Related codes

- [`AICE-606`](./AICE-606.md) — PASS without a verified run.
- [`AICE-608`](./AICE-608.md) — verification lacking independence.
