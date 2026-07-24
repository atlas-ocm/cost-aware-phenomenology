# AICE-616 — Baseline Diff Conflation

**Unofficial draft (AICE v0.9.0).**

## Canonical identifier

`AICE-616`

## Human-readable alias

`HTTP 616 — Baseline Diff Conflation`

## Intent

Catch the case where a repository-relative diff is substituted for the exact current-episode
delta, causing a verifier or acceptance mechanism to evaluate bytes that do not belong
exclusively to the current episode.

The defect governs **review-input identity**: *which exact bytes is the verifier
reviewing?*

Canonical machine name: `BASELINE_DIFF_CONFLATION`.

Canonical invariant:

```
AUTHORITATIVE_REVIEW_PAYLOAD = NORMALIZED_EPISODE_PREIMAGE_TO_POSTIMAGE_DELTA
not AUTHORITATIVE_REVIEW_PAYLOAD = GIT_DIFF_AGAINST_HEAD
```

Forbidden inference:

```
REPOSITORY_DIFF
does NOT imply
CURRENT_EPISODE_DELTA
```

Additionally, a raw preimage→postimage byte diff does not necessarily imply the semantic
episode delta when line-ending or equivalent normalization churn makes unchanged content
appear modified:

```
RAW_BYTE_DIFF
does NOT necessarily imply
SEMANTIC_EPISODE_DELTA
```

## Trigger condition

All of the following hold:

1. the authoritative review or acceptance payload is built from a repository-relative
   baseline diff (e.g. `git diff HEAD`);
2. the repository-relative diff contains bytes not authored by the current episode;
3. those non-episode bytes are presented as part of the current episode;
4. the conflation affects review, verdict, acceptance, scope evaluation, or another
   authority-bearing decision (it is not merely cosmetic diagnostic contamination).

## Required observations

Evidence classes include: the exact episode preimage and postimage; the constructed review
payload and what it was derived from; the repository-relative diff; proof the target was
dirty vs the baseline with bytes not authored by the current episode; the episode-owned
delta and its digest; and the authority-bearing decision the conflated payload drove.

Strong evidence includes a real repository with a prior-accepted uncommitted line where the
baseline diff emits that line conflated with the episode edit (fail-before), and, after the
fix, a review payload equal to the normalization-aware preimage→postimage unified diff
only. Retain the raw repository diff as diagnostic data, not as the authoritative payload.

## Missing-evidence condition

No proof exists that the verifier reviewed exactly the episode-owned delta: the payload was
derived from a repository baseline that carried non-episode bytes, those bytes were
authority-affecting, and the episode identity owns only a subset of what was reviewed — so
the verdict cannot authorize only the current episode.

## False-positive guards

AICE-616 MUST NOT fire when:

- the episode is explicitly repository-wide and its owned scope is the entire diff;
- the worktree is clean and the repository diff is byte-equivalent to the normalized
  episode delta (the payloads coincide);
- the verifier payload is intentionally defined as aggregate/repository state by contract;
- the contamination is purely presentational/diagnostic and cannot affect verdict or
  acceptance;
- normalization differences are explicitly represented and do not change the owned semantic
  delta.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

The verifier verdict cannot authorize only the current episode; scope findings may be
false; acceptance may be unearned. The candidate remains unaccepted until the review input
is rebound to the exact episode delta. Retryability: `requires_new_evidence`.

## Remediation

Compute an episode-local normalized unified delta (preimage→postimage), expose its kind and
digest, and send only that delta as the authoritative verifier payload. Normalize only
according to explicit canonical normalization rules. Retain the repository-relative diff as
non-authoritative diagnostics. Bind preimage, postimage, patch, normalized episode-delta,
scope, job, attempt, and target identities into durable evidence.

## Distinction from adjacent codes

- **AICE-615 — Accepted-State Rollback Erasure.** `AICE-616 = wrong bytes are REVIEWED`
  (review-input identity); `AICE-615 = wrong bytes are RESTORED` (rollback-restore
  identity). Different trigger, owned evidence object, authority boundary, workflow effect,
  and remediation. Shared `EPISODE_EXACT_IDENTITY_BINDING` family; MUST NOT be merged. Do
  not absorb AICE-616 into AICE-615.
- **AICE-608 — Verification Exists, Independence Not Found.** 608 concerns whether
  verification is genuinely independent. AICE-616 may occur even with a fully independent
  verifier, because the independent verifier receives the wrong payload — independence and
  payload identity are distinct properties.
- **AICE-609 — Consensus Exists, Evidence Not Found.** 609 concerns agreement without
  evidence. AICE-616 concerns evidence-object ownership: the payload includes bytes that do
  not belong to the episode being decided.
- **AICE-612 — Actor Path Substitution.** 612 transfers evidence across actor paths; 616
  transfers bytes across episode identities or baseline boundaries.

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

Target `F` is dirty vs HEAD with an accepted `+PRIOR` line; the current episode edits line
`L3`; the review payload is built from `git diff HEAD` and includes `+PRIOR` alongside the
`L3` edit; the verifier votes on both as the current episode. This is AICE-616. The negative
shape: a clean worktree where the repository diff equals the normalized episode delta and
the verifier reviews exactly the episode-owned change — not AICE-616.

See
[`../../../examples/aice/aice-616-baseline-diff-conflation.json`](../../../examples/aice/aice-616-baseline-diff-conflation.json).
The class was distilled from internal CAP Processor forensic evidence; the example asserts
no commit id, path, digest, receipt, or timestamp as canonical fact.

## Related codes

- [`AICE-615`](./AICE-615.md) — rollback-restore identity (the paired `EPISODE_EXACT_IDENTITY_BINDING` class).
- [`AICE-608`](./AICE-608.md) — verification independence (distinct from payload identity).
- [`AICE-609`](./AICE-609.md) — consensus without evidence (distinct from evidence-object ownership).
- [`AICE-612`](./AICE-612.md) — cross-actor evidence transfer (distinct from cross-episode byte transfer).
