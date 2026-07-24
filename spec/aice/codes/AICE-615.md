# AICE-615 — Accepted-State Rollback Erasure

**Unofficial draft (AICE v0.9.0).**

## Canonical identifier

`AICE-615`

## Human-readable alias

`HTTP 615 — Accepted-State Rollback Erasure`

## Intent

Catch the case where a non-accepting episode rollback restores repository-relative state
instead of the exact episode preimage owned by that rollback authority, thereby erasing
previously accepted or unrelated uncommitted bytes on the target.

The defect governs **restore identity**: *which exact bytes may rollback restore?*

Canonical machine name: `ACCEPTED_STATE_ROLLBACK_ERASURE`.

Canonical invariant:

```
ROLLBACK_TARGET = EXACT_EPISODE_PREIMAGE
not ROLLBACK_TARGET = HEAD
not ROLLBACK_TARGET = INDEX
not ROLLBACK_TARGET = REPOSITORY_BASELINE
not ROLLBACK_TARGET = LAST_COMMIT
```

Forbidden inference:

```
ROLLBACK_EXECUTED
does NOT imply
RESTORED_BYTES_EQUAL_EPISODE_PREIMAGE
```

A rollback that merely ran, or a verdict record that says the episode was cleaned up, is
not proof the restored bytes equal the preimage. The restored digest MUST equal the
preimage digest.

## Trigger condition

All of the following hold:

1. the episode performed a real mutation on an existing target;
2. the episode reached a non-accepting terminal (NONPASS / rejection / block), so rollback
   actually fires;
3. the rollback target is derived from repository-relative state (HEAD / index / commit /
   baseline) rather than from the exact episode preimage;
4. the target's episode preimage contains accepted or unrelated uncommitted bytes that are
   absent from the repository-relative baseline;
5. rollback erases, or may erase, those bytes.

## Required observations

Evidence classes include: the exact pre-mutation snapshot (preimage) bound to
episode/job/attempt/target/path identity; the rollback target derivation (what the restore
reset to); the post-rollback bytes and their digest; the preimage digest; proof that
accepted or unrelated sibling bytes existed at episode start; the non-accepting terminal;
and a comparison showing `restored_sha256 != preimage_sha256`.

Strong evidence includes a fail-before trace: an accepted sibling change `A` on file `F`;
a rejected attempt `B` on the same `F`; `B`'s rollback resetting `F` to the committed
baseline; and the restored digest differing from the episode-preimage digest. A rollback
that only "ran" is not evidence that the restored bytes equal the preimage.

## Missing-evidence condition

No proof exists that the rollback restored the exact episode preimage: the restored bytes
were derived from repository baseline state, the preimage held accepted or unrelated bytes
absent from that baseline, and `restored_sha256 != preimage_sha256` — so previously
accepted uncommitted product bytes were, or may have been, silently lost.

## False-positive guards

AICE-615 MUST NOT fire when:

- an explicitly authorized whole-worktree destructive reset whose intended target *is* the
  worktree by design;
- the target is clean and HEAD is byte-identical to the episode preimage (git-restore and
  exact-restore coincide);
- no accepted or unrelated sibling state existed to erase (nothing to lose);
- an operator-requested reset whose intended target is the repository baseline;
- a rollback that restores the exact preimage and proves it by digest.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

The current candidate is not accepted; the rollback cannot be considered valid; the episode
cannot close as safely restored; any success, clean-state, or preservation claim is
forbidden. Exact-preimage restoration or an explicit blocked terminal is required.
Retryability: `requires_new_evidence`.

## Remediation

The rollback authority (e.g. the runner) owns an exact pre-mutation snapshot bound to
episode/job/attempt/target/path identity, persisted outside the mutable target surface. On
any non-accepting terminal after a real mutation, restore that exact preimage atomically
and digest-verify (`restored_sha256 == preimage_sha256`); on a missing, ambiguous, or
mismatched preimage binding, fail closed with the repository's blocked terminal
(`BLOCKED_EXACT_PREIMAGE_ROLLBACK` / `BLOCKED_PREIMAGE_BINDING_MISMATCH`). Never substitute
Git baseline state (`git restore` / HEAD / index) for episode-owned state.

## Distinction from adjacent codes

- **AICE-616 — Baseline Diff Conflation.** 616 governs the bytes the verifier **reviews**
  (review-input identity); 615 governs the bytes rollback **restores** (restore identity).
  `AICE-616 = wrong bytes are REVIEWED`; `AICE-615 = wrong bytes are RESTORED`. Different
  trigger, owned evidence object, authority boundary, workflow effect, and remediation.
  They share the non-normative `EPISODE_EXACT_IDENTITY_BINDING` family but MUST NOT be
  merged; shared root cause is not sufficient for merging.
- **AICE-613 — Self-Hosting Mutation-Shape Deadlock.** 613 concerns the inability to
  materialize an otherwise required mutation shape through the available self-hosting path;
  615 concerns which bytes a non-accepting terminal restores after a mutation succeeded.
- **AICE-604 — Hash Exists, Reality Not Found.** 604 concerns a claimed artifact/digest
  whose required bytes cannot be found or verified; 615 concerns restoration of the wrong
  existing bytes. Do not broaden AICE-615 into every failed rollback — the accepted-state
  erasure (or equivalent episode-preimage violation) is required.

## Non-normative family: `EPISODE_EXACT_IDENTITY_BINDING`

```text
EPISODE_EXACT_IDENTITY_BINDING            (family label only — NO numeric code assigned)
  ├── AICE-616  review-input identity     (which bytes the verifier reviews)
  └── AICE-615  rollback-restore identity (which bytes rollback restores)
```

The family name is a cross-reference only. It MUST NOT replace, merge, or renumber
615/616, MUST NOT receive its own numeric code, and MUST NOT become a required schema enum
value.

## Example

`REPRESENTATIVE_EXAMPLE` — `NOT_A_VERIFIED_HISTORICAL_INCIDENT`.

File `F` holds accepted uncommitted state `A`. Candidate `B` edits `F` and receives a
non-accepting terminal. The system runs a repository-relative restore against HEAD; both
`B` and `A` disappear, and the restored digest does not equal the episode preimage digest.
This is AICE-615. The negative shape: `F` is clean and byte-identical to HEAD, `B` is
rejected, the exact episode preimage is restored and digest-verified — not AICE-615.

See
[`../../../examples/aice/aice-615-accepted-state-rollback-erasure.json`](../../../examples/aice/aice-615-accepted-state-rollback-erasure.json).
The class was distilled from internal CAP Processor forensic evidence; the example asserts
no commit id, path, digest, receipt, or timestamp as canonical fact.

## Related codes

- [`AICE-616`](./AICE-616.md) — review-input identity (the paired `EPISODE_EXACT_IDENTITY_BINDING` class).
- [`AICE-613`](./AICE-613.md) — inability to materialize a required mutation shape (a distinct boundary).
- [`AICE-604`](./AICE-604.md) — a claimed artifact whose bytes cannot be found or verified.
