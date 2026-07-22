# AICE-604 — Hash Exists, Reality Not Found

**Unofficial draft (AICE v0.5.0).**

## Canonical identifier

`AICE-604`

Symbolic code: `ARTEFACT_METAPHYSICAL` (retained in this legacy spelling only as the
established machine-readable symbol; normative prose uses "artifact").

## Human-readable alias

`HTTP 604 — Hash Exists, Reality Not Found`

## Intent

Catch the case where an artifact is *declared* — optionally with a filename, path,
size, or digest — but the bytes were never independently materialized. A hash string
in a report is a claim about reality, not reality.

## Trigger condition

An artifact is declared, and the required materialization evidence is absent or
contradictory.

## Required observations

At least one trustworthy materialization signal:

- a confirmed path;
- a recorded write/persist event;
- a successful tool or process receipt;
- a `stat`/readback of the file;
- readable bytes;
- a digest **recomputed from the observed bytes** and matching any declared digest.

## Missing-evidence condition

The incident applies when, for example:

- no path can be confirmed;
- no write/persist event is recorded;
- no successful tool/process receipt exists;
- no `stat`/readback succeeds;
- no bytes can be read;
- no digest can be recomputed from observed bytes; or
- the declared digest does not match the digest computed from the observed bytes.

## False-positive guards

A missing write event alone is **not** sufficient if the artifact can be independently
located, read, and verified through another trustworthy evidence path.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

The declared artifact MUST NOT be accepted as existing until its bytes are observed.

## Remediation

`materialize_the_bytes` — produce a confirmed path and readable bytes, then recompute
the digest from those bytes. Repeating the declaration does not resolve the incident.
Retryability: `requires_state_materialization`.

## Example

Sanitized real incident pattern:

- an agent declared `artefact.json`;
- a SHA-256 was included in the report;
- no path or write event could be confirmed;
- another agent searched the repository;
- no independently readable bytes were found.

The digest is recorded honestly as *declared but unverified* — see
[`../../../examples/aice/aice-604-metaphysical-artifact.json`](../../../examples/aice/aice-604-metaphysical-artifact.json),
which represents the absent digest through a boolean declaration field rather than a
fabricated 64-character string.

## Related codes

- [`AICE-606`](./AICE-606.md) — PASS without a verified test run.
- [`AICE-607`](./AICE-607.md) — deployment without an observed production state.
