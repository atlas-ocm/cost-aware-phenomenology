# AICE-605 — Release Exists, Implementation Not Found

**Unofficial draft (AICE v0.4.0).**

## Canonical identifier

`AICE-605`

## Human-readable alias

`HTTP 605 — Release Exists, Implementation Not Found`

## Intent

Catch the case where a release, version bump, or implementation change is claimed, but
the claimed implementation or behavior delta cannot be observed anywhere.

## Trigger condition

A release/version/implementation change is claimed, and the implied implementation or
behavior delta cannot be observed.

## Required observations

At least one observable delta consistent with the release narrative:

- an implementation diff in the relevant source;
- a change in observable behavior;
- a changelog entry tied to a concrete implementation change;
- an artifact or test that exercises the claimed new behavior.

## Missing-evidence condition

The incident applies when:

- version metadata changes;
- implementation files and observable behavior remain unchanged; and
- the release narrative nonetheless implies a functional delta.

## False-positive guards

- an explicitly documented metadata-only release is valid;
- dependency republishing, provenance repair, packaging correction, or administrative
  version alignment may be legitimate;
- do **not** emit AICE-605 merely because a diff is small.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_RELEASE
```

The release MUST NOT be accepted as delivering the claimed functional change until an
implementation delta is observed or the release claim is corrected.

## Remediation

Provide an implementation diff (or other observable behavior delta) that supports the
release claim, or revise the release notes to describe it accurately (for example, as a
metadata-only release). Retryability: `requires_state_materialization`.

## Example

Genericized, synthetic example:

- a Rust package version advances in `Cargo.toml`;
- no implementation delta is observed;
- the release claims a behavioral or implementation change.

See
[`../../../examples/aice/aice-605-release-without-implementation.json`](../../../examples/aice/aice-605-release-without-implementation.json).
The example is marked synthetic; no third-party project is named.

## Related codes

- [`AICE-604`](./AICE-604.md) — declared artifact without materialized bytes.
- [`AICE-607`](./AICE-607.md) — deployment without an observed production state.
