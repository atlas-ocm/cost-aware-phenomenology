# Gold Case: Stale Cross-Turn Anchor

## Executive Summary

A prior answer was valid when produced, but later context makes it stale. CAP
prevents the system from reusing the old node as an anchor without revalidation.

## Failure Mode

Earlier turn:

```text
The deployment date is May 12.
```

Later turn:

```text
Assuming the May 12 date, draft the announcement.
```

Between those turns, the date may have changed or new evidence may have arrived.
A long-running assistant may reuse the old answer because it is already in
context.

## CAP Reading

The old node is not necessarily false. It is stale. CAP distinguishes "bad"
from "requires revalidation".

Relevant policy case:

```text
lpd_08_stale_cross_turn_anchor
```

## Telemetry

```text
@R[N:R:TC1.0:RCH:E0.2:CSM:VA]
stale_anchor = true
```

Interpretation:

- original retrieval confidence was high
- entropy was low
- the old node would normally be an anchor candidate
- cross-turn staleness invalidates automatic reuse

## Policy

```text
node_status = needs_audit
allowed_as_anchor = false
release_action = revalidate_before_reuse
forbid = reuse_stale_anchor_without_revalidation
require = cross_turn_revalidation
```

## COM Operation Sequence

```text
OBSERVE prior node
CHECK whether its validity window is still open
BLOCK automatic reuse
REVALIDATE against current source/context
RELEASE updated or qualified answer
```

## Subsystem Mapping

| CAP subsystem | Role |
|---|---|
| Telemetry gating | Detects stale-anchor context. |
| Operator admissibility | Blocks reuse without revalidation. |
| Transition cost | Keeps the system from needlessly discarding useful old context. |
| COM grammar | Separates prior-node memory from current release permission. |

## Source Hierarchy

| Source | Status |
|---|---|
| Prior model answer | Historical node, not current proof. |
| Current source/context | Required for renewed anchor status. |
| User assumption | Useful prompt context, not validation. |

## Validator Behavior

A validator may accept the old answer because it was valid when created. CAP
adds time/context sensitivity: validity at turn N does not automatically imply
release permission at turn N+k.

## Corrected Output Shape

The model should first revalidate:

```text
Before drafting, I need to confirm whether May 12 is still the current date.
If it is confirmed, I can use it. If not, I should update the announcement.
```

## Why CAP Helps

Prompt-only systems often treat context as stable memory. CAP treats cross-turn
reuse as a policy decision: even a previously good node can lose anchor status.

## Edge Cases

- If the user explicitly provides a fresh source, it becomes a source update.
- If the domain is time-sensitive, stale anchors should default to audit.
- If the output is low-risk and clearly caveated, the system may release a
  qualified answer rather than block entirely.

## Generalization

This case applies to schedules, prices, legal or policy status, product specs,
API behavior, organizational decisions, and any long-running agent memory.
Staleness is a release-policy issue, not only a retrieval issue.
