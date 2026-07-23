# AICE-607 — Deployment Exists, Production Not Found

**Unofficial draft (AICE v0.8.0).**

## Canonical identifier

`AICE-607`

## Human-readable alias

`HTTP 607 — Deployment Exists, Production Not Found`

## Intent

Catch the case where a deployment is reported as successful, but the target
environment's expected post-deployment state is unobserved, unchanged, or
contradictory.

## Trigger condition

A deployment is reported successful, and the target environment's expected
post-deployment state is unobserved, unchanged, or contradictory.

## Required observations

At least one signal of the target's actual state:

- a deployment receipt;
- the target revision;
- a production asset digest;
- a health/readiness result;
- an externally observed version;
- behavior or configuration expected to change.

## Missing-evidence condition

A successful deployment is claimed, but the target's post-deployment state cannot be
observed, is unchanged from before, or contradicts the claim.

## False-positive guards

A no-op deployment may be legitimate if it is explicitly declared and consistent with
the deployment contract.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_DEPLOYMENT
```

The deployment MUST NOT be accepted as effective until the target's expected state is
independently observed.

## Remediation

Observe the target revision, health result, or externally visible change, and confirm
it matches the deployment claim; otherwise correct the claim. Retryability:
`requires_new_evidence`.

## Example

Consistent with this repository's own publication discipline: a push/publish is
reported, but the remote reference is not independently observed at the expected
commit. Until `git ls-remote` (or an equivalent independent read) shows the target
reference at the expected revision, the publication remains `physical_state:
UNOBSERVED` and `STATE_UNCHANGED`.

## Related codes

- [`AICE-604`](./AICE-604.md) — declared artifact without materialized bytes.
- [`AICE-605`](./AICE-605.md) — release without an observed implementation delta.
