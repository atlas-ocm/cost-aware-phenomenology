# Registry Entry Exists, Summary Not Found

**Unofficial draft. Status: Research-only. NON-CANONICAL.**

> ✅ **PROMOTED.** This candidate's evidence and reasoning were canonically published as
> [`AICE-619`](../codes/AICE-619.md). This dossier is retained as promotion provenance — it
> records the state of the class *before* publication and is **not** updated to track later
> edits to `AICE-619.md`, which is authoritative. `status` and `canonical code` below are the
> historical values at candidate time and are preserved, not corrected, per
> `WITHDRAWN != DELETED`-style retention; see [Authority status](./README.md#authority-status).

> This is a candidate record in the [quarantine surface](./README.md). It is **not** part of
> the AICE code set, has **no** number, and reserves none. See
> [Authority status](./README.md#authority-status).

## Identity

```
working title    Registry Entry Exists, Summary Not Found
machine name     CANONICAL_SUMMARY_ENTRY_OMISSION
public alias     Implementation Exists, Documentation Not Found
plural rendering Registry Entries Exist, Summary Not Found   (episode-specific only)

status                 EVIDENCE_BACKED_PROVISIONAL   (historical, at candidate time)
canonical code         UNASSIGNED                    (historical, at candidate time)
number reserved        false                         (historical, at candidate time)
promotion_status       PROMOTED
promoted_to            AICE-619
```

```
NON_CANONICAL
UNNUMBERED
NON_RESERVING
REGISTRY_EXCLUDED
SCHEMA_EXCLUDED
DEFINED_CODE_COUNT_EXCLUDED
```

`AICE-619` is **not** assigned, **not** reserved, and **not** implied by this record.
AICE-619 remains available but unborn. This candidate's filename, its position on disk, and
its existence allocate no number.

Use the **singular** title for the general incident class. The plural rendering is an
episode-specific presentation of the observed instance (two omitted entries) and carries no
separate class identity.

## Core definition

A canonical entry is implemented and included in a published release, and a public summary
that is required or reasonably presented as the current projection of that canonical registry
is updated for the release, but the entry is absent, stale, or contradicted in that summary
while publication closure is claimed.

The defect is in the **projection**, not in the canonical bytes. The registry is correct; the
reader is not served it.

## Trigger predicates — all required

1. `CANONICAL_ENTRY_EXISTS = true`
2. `CANONICAL_ENTRY_IS_PUBLISHED = true`
3. `PUBLIC_SUMMARY_EXISTS = true`
4. `PUBLIC_SUMMARY_PURPORTS_TO_REPRESENT_CURRENT_CANONICAL_SET = true`
5. `PUBLIC_SUMMARY_UPDATED_OR_REAFFIRMED_FOR_CURRENT_RELEASE = true`
6. `CANONICAL_ENTRY_ABSENT_STALE_OR_CONTRADICTED_IN_SUMMARY = true`
7. `PUBLICATION_OR_DOCUMENTATION_CLOSURE_CLAIMED = true`

Required formula:

```
CANONICAL_ENTRY_PRESENT
AND CANONICAL_RELEASE_PUBLISHED
AND CURRENT_PUBLIC_SUMMARY_REQUIRED
AND PUBLIC_SUMMARY_ENTRY_ABSENT_OR_STALE
AND PUBLICATION_CLOSURE_CLAIMED
  -> CANONICAL_SUMMARY_ENTRY_OMISSION
```

Required parity boundary:

```
PUBLIC_SUMMARY_DEFINED_SET = CANONICAL_REGISTRY_DEFINED_SET
```

## Forbidden substitutions

```
ENTRY_PRESENT_IN_REGISTRY  != ENTRY_PRESENT_TO_THE_READER
CHECKER_PASS               != PUBLIC_SUMMARY_PARITY_ESTABLISHED
DOCUMENT_UPDATED           != DOCUMENT_COMPLETE
PREVIOUS_VERIFIER_PASS     != PASS_FOR_MUTATED_BYTES
```

## Required terminal

```
STATE_UNCHANGED
BLOCK_PUBLICATION_CLOSURE
REQUIRE_PUBLIC_SUMMARY_RECONCILIATION
REQUIRE_CANONICAL_TO_PUBLIC_SET_PARITY
```

The terminal MUST NOT remove the canonical entries, roll back the omitted codes, claim the
implementation is absent, or claim the release is absent. The canonical set is correct; only
its public projection is incomplete.

Minimum repair postcondition:

```
PUBLIC_SUMMARY_DEFINED_SET = CANONICAL_REGISTRY_DEFINED_SET
```

## Source and provenance limits

Source class: `PRIMARY_PERSISTED` — committed repository bytes at a published commit, read
directly from Git object storage, plus the published remote ref and the local remote-tracking
ref log. No screenshot, transcript recollection, or narrative report is load-bearing for any
predicate below.

Explicitly **non-load-bearing** (recorded, but no predicate rests on it): the console push
receipt line `8c40f93..389ac4b main -> main` observed during the publication episode. That
exact string is a transcript artifact and is not recoverable from repository bytes. The
publication fact it reports is instead carried by evidence that *is* machine-readable —
`origin/main == 389ac4b`, `ahead/behind 0/0`, and the remote-tracking ref log
(`origin/main@{0} = 389ac4b "update by push"`, `@{1} = 8c40f93`). Ref logs are local
repository state, not published bytes; they are cited as corroboration, not as the primary
publication witness.

Provenance limits:

- The observed instance is a **single** repository (this one) at a **single** commit.
- One instance does not establish a general cross-project class frequency.
- **Author-adjacent evidence.** The publication episode that reaffirmed the defective table
  was authored by the same agent recording this candidate. That is a reason for independent
  review of these bytes, not a reason to soften the record.
- **No intent is claimed.** Selective omission here is an observable byte-state. This record
  asserts nothing about deliberateness, concealment, or motive.

## Observed episode binding

```
canonical repository   F:\VibeCoding\Shard-Theory\CAP
observed commit        389ac4b8bbd58ba64ed5639f3ddd3f6a0838672d
published remote       origin/main == 389ac4b   (ahead/behind 0/0)
canonical version      AICE v0.10.0
defined-code count     18
```

Parsed sets (machine-parsed, not inferred from prose):

```
CANONICAL_DEFINED_SET        AICE-601..AICE-618                       (n=18)
  source: spec/aice/registry.json -> canonical_defined_set
  cross-check: incident.schema.json properties.code.enum == identical set (n=18)

PUBLIC_SUMMARY_DEFINED_SET   AICE-602, AICE-604..AICE-618             (n=16)
  source: AICE.md section "## 6. Registry summary", table rows only (L109-L124)

MISSING_FROM_PUBLIC_SUMMARY  AICE-601, AICE-603
EXTRA_IN_PUBLIC_SUMMARY      (none)
```

Required episode conclusion:

```
SUMMARY_UPDATE_EXECUTED  AND  SUMMARY_PARITY_NOT_ESTABLISHED
```

## Evidence matrix

| # | Predicate | Evidence (exact reference at `389ac4b`) | Result |
|---|---|---|---|
| P1 | AICE-601 canonically defined and published | `spec/aice/codes/AICE-601.md` present; in `registry.json` `canonical_defined_set` **and** `codes[]`; in `incident.schema.json` code enum; example `examples/aice/aice-601-minimum-sufficient-mechanism-bypass.json` | true |
| P2 | AICE-603 canonically defined and published | `spec/aice/codes/AICE-603.md` present; in registry set **and** `codes[]`; in schema enum; example `aice-603-governance-induced-service-unavailability.json` | true |
| P3 | AICE-617 canonically defined and published | `spec/aice/codes/AICE-617.md` present; in registry set **and** `codes[]`; in schema enum; example `aice-617-process-activity-outcome-substitution.json` | true |
| P4 | Table presented as a Registry summary, not a selective examples list | `AICE.md:105` heading `## 6. Registry summary`; no "selected", "partial", "examples only", or scope-limiting qualifier in the section; `AICE.md:129-134` immediately restates the **full** closed set `AICE-601 … AICE-618` (with AICE-600 unassigned and AICE-619 unreserved) as the surrounding prose | true |
| P5 | Summary includes AICE-617 | `AICE.md:123` carries an `AICE-617` row (alias `HTTP 617`, title `Work Exists, Result Not Found`, effect `STATE_UNCHANGED` + `BLOCK_ACCEPTANCE`) | true |
| P6 | Summary omits AICE-601 | no `AICE-601` row in `AICE.md:107-124`; parsed row set excludes it | true |
| P7 | Summary omits AICE-603 | no `AICE-603` row in `AICE.md:107-124`; parsed row set excludes it | true |
| P8 | Summary edited/regenerated for this release (not merely untouched) | `git show 389ac4b -- AICE.md` adds the `AICE-617` row at `AICE.md:123`; the same commit also rewrote the set prose at `AICE.md:129-134` and the version banner. The table was **in scope and edited** during v0.10.0 publication | true |
| P9 | Publication closure claimed | commit `389ac4b` message asserts "Independently verified (non-author): checker exit 0, 237 tests pass"; `origin/main == 389ac4b` with tree `423e4669` identical and ahead/behind `0/0`; ref log `origin/main@{0} = 389ac4b "update by push"`, `@{1} = 8c40f93`. (The console push-receipt string is transcript-only and non-load-bearing — see provenance limits.) | true |
| P10 | Existing closure did not detect the mismatch | `reference/python/scripts/aice/check_aice.py:238` references `AICE.md` **only** inside `link_docs` (relative-link resolution). Zero occurrences of registry-summary/table parity logic anywhere in the checker or the AICE test module | true |

### Origin of the omission (historical, non-load-bearing)

`git log -S` over `AICE.md` finds **zero** commits that ever introduced an `AICE-601` or
`AICE-603` table row. Commit `8c40f93` — the release that canonically published AICE-601 and
AICE-603 — modified `AICE.md` but added no table rows for them. The omission therefore
originated at first publication of those codes and was **carried forward and reaffirmed** at
`389ac4b`. This strengthens P8 (the table is actively maintained across releases) and is
recorded as provenance, not as an additional predicate.

### Scope isolation (other projections are correct)

At `389ac4b` the defect is confined to the `AICE.md` §6 table:

- `spec/aice/README.md` §6 lists **all 18** codes, including AICE-601, AICE-603, AICE-617.
- `README.md:199` states the defined set as `AICE-601`…`AICE-618` — correct.
- `registry.json` and `incident.schema.json` are correct and mutually identical.

This matters twice: it is evidence **against** an "intentionally partial view" reading (the
sibling projections are complete), and it bounds the required repair to one table.

### Secondary, unpublished instance (recorded, not repaired, not load-bearing)

`spec/aice/candidates/README.md:34-36` still describes the canonical set as
"`AICE-602`, `AICE-604`…`AICE-616`, `AICE-618`; `AICE-600`, `AICE-601`, `AICE-603`, `AICE-617`
unassigned" — a pre-v0.9 claim now contradicted by the registry. This file is **untracked and
therefore unpublished**, so predicate P2/P3-style *publication* of the projection is not
established for it and it is **not** part of the primary binding. It is recorded here as a
corroborating in-repo observation of the same shape. It is deliberately **left unrepaired**
during this evidence-capture episode.

## False-positive boundary

This candidate MUST NOT fire when:

- the document explicitly states it contains **selected examples only**;
- the document is clearly archived or pinned to an older named release;
- the omitted entry is intentionally internal and no public projection is required;
- the canonical entry is itself unpublished;
- the summary is generated from a different, explicitly declared scope;
- publication closure has not been claimed;
- a transient rendering or cache problem exists while committed source bytes are correct.

```
INTENTIONALLY_PARTIAL_VIEW != INCOMPLETE_CANONICAL_PROJECTION
```

A public table titled or framed as a current Registry summary is **not** presumed partial
merely because rows are missing. The presumption must be defeated by an explicit scope
statement in the document, not inferred from the omission itself.

## Required controls

### Negative control — declared partial view (must not fire)

A document headed "Selected AICE codes (illustrative subset)" that lists five codes while the
registry defines eighteen. Predicate 4 fails: the summary does not purport to represent the
current canonical set. Not this incident.

### Negative control — pinned historical release (must not fire)

`CHANGELOG-v0.9.md` shows a 17-code table after v0.10.0 ships. The document is pinned to a
named prior release; predicates 4 and 5 fail. Not this incident.

### Negative control — unpublished canonical entry (must not fire)

A code document drafted in a working tree but absent from the published registry and schema,
and therefore absent from the summary. Predicate 2 fails; the summary is *correct*. Not this
incident.

### Negative control — closure not claimed (must not fire)

The table is known-incomplete, the release is explicitly marked in-progress, and no
publication closure, checker PASS, or readback is asserted. Predicate 7 fails. Not this
incident — this is honest work in flight.

### Incident control — the observed episode (should fire)

Registry defines 18 codes; the `## 6. Registry summary` table carries 16; the same table was
edited in the publication commit to add the newest row; commit, push, remote readback,
checker PASS, and test PASS are all claimed as closure. All seven predicates hold. Fires.

## Comparison with canonical AICE

### AICE-605 — Release Exists, Implementation Not Found (nearest inverse)

AICE-605 requires a **release claim while the implementation is absent**. Here the
implementation is present *and* the release is present; only the public projection is
incomplete. The polarity is inverted, so the observed episode is **not** AICE-605.

```
AICE-605                     release claimed, implementation absent
this candidate               implementation present, release present, projection absent
```

### Sibling candidate — "Implementation Exists, Release Not Found" (NOT established here)

A distinct hypothetical sibling requiring implementation present and canonical
release/publication **absent**. The observed episode has commit, push, and verified remote
readback, so the release is present. This sibling is **not** recorded as evidence-backed by
this episode and no record is created for it.

### AICE-610 — Control Exists, Enforcement Not Found

AICE-610 may co-emit **only if** a declared public-summary parity control exists and is not
causally bound to the release path. At `389ac4b` no such control is declared — the checker
never claims to enforce summary parity — so there is no declared-but-unenforced control and
610 does **not** co-emit. This candidate describes the observable projection defect itself,
not an unenforced control.

### AICE-604 — Hash Exists, Reality Not Found

AICE-604 concerns a claimed artifact identity whose bytes are absent or unverified. Here the
canonical bytes exist and were independently read back; their public projection is incomplete.
Different failure surface.

### AICE-617 — Work Exists, Result Not Found

AICE-617 concerns process activity substituting for the target outcome. Here the release
outcome genuinely exists — it is the documentation that does not faithfully expose it. Not a
process-for-outcome substitution.

### AICE-616 / AICE-608 (not applicable)

Not review-input identity (616): no verifier reviewed the wrong episode bytes. Not verifier
independence (608): the reviewer was independent; the review **contract** simply did not
enumerate this artifact. That distinction is the point of
`PREVIOUS_VERIFIER_PASS != PASS_FOR_MUTATED_BYTES`.

## Checker coverage gap

```
check_aice.py enforces   registry <-> codes <-> examples <-> schema <-> links
check_aice.py does NOT   parse AICE.md "## 6. Registry summary" table rows
                         compare that row set to canonical_defined_set
```

`AICE.md` enters the checker only as a link-resolution target
(`check_aice.py:238`, `link_docs`). A code can therefore be fully canonical, fully tested, and
fully published while remaining invisible in the document most readers treat as the registry.
Closure at `389ac4b` *claimed* checker exit 0 and 237 tests passing; that execution is a claim
in the commit message, not persisted independently readable evidence. What is verifiable from
repository bytes is narrower and sufficient: neither surface contains logic capable of
detecting this mismatch, so a genuine PASS on both would still have been silent here.

## Remediation hypothesis (NOT authorized in this episode)

1. Add the missing `AICE-601` and `AICE-603` rows to the `AICE.md` §6 table, in numeric order,
   with titles and default effects taken from `registry.json` (not re-authored).
2. Add a deterministic guard: parse `canonical_defined_set` from the registry, parse the
   `AICE.md` Registry-summary table row set, and fail the checker on any missing or extra
   entry. Cover it with an adversarial tamper test in the existing suite.
3. Re-freeze and independently review the **repaired bytes**. The earlier PASS does not
   transfer:

```
PREVIOUS_VERIFIER_PASS != PASS_FOR_MUTATED_BYTES
```

Neither step is performed in this episode: `AUTHORIZE_PUBLIC_SUMMARY_REPAIR = false` and
`AUTHORIZE_CANONICAL_MUTATION = false`. The public summary is left **intentionally unrepaired**
so the defect stays bound to its exact observed bytes.

## Portable CAP enforcement requirement (non-implemented)

A conforming implementation would treat "publication closure" as requiring
`PUBLIC_SUMMARY_DEFINED_SET == CANONICAL_REGISTRY_DEFINED_SET` for every document that
presents itself as the current registry projection, and would refuse closure otherwise. No
such control is implemented here, and this record does not implement one. Recording the
requirement is not implementing it.

## Promotion gate

Canonical promotion is a separate episode and requires, at minimum: a second independent
primary instance (ideally outside this repository); explicit operator number assignment;
canonical registry / schema / code-document / example updates; checker and test coverage;
independent review of the promotion bytes; commit, push, and remote readback. Nothing in this
record satisfies any of those conditions.

```
CANDIDATE_PRESENT         != CANONICAL_CODE_DEFINED
EVIDENCE_BACKED           != PUBLISHED
PROVISIONAL_VERIFIER_PASS != CANONICAL_PROMOTION
```

## Reopen / withdrawal rule

This record moves to `WITHDRAWN_TRIGGER_FALSIFIED` if stronger primary evidence shows that
`AICE.md` §6 was, at `389ac4b`, an explicitly declared partial or pinned view — which would
falsify predicate 4. Reinterpreting the omission as intentional after the fact does not
sustain the candidate; only the document's own scope statement can defeat predicate 4.

## Repository state at recording

```
HEAD                        389ac4b   (unchanged; == origin/main)
tracked modifications       0
staged paths                0
commits created             0
pushes                      0
canonical bytes             unchanged
AICE.md section 6 table     intentionally UNREPAIRED
```

Untracked paths: six, all under `spec/aice/candidates/`. Exactly **one** is new in this
episode — this record. The five pre-existing candidate paths (`README.md`,
`causal-question-closure-substitution.md`, `post-observation-evaluation-mutation.md`,
`semantic-review-subject-omission.md`, `fixtures/post-observation-straight-admission.md`) were
present at preflight and are byte-identical afterwards, confirmed by SHA-256 comparison. This
record makes no claim that the candidate surface was otherwise empty.

## Verification status

```
author self-review          NOT SUFFICIENT (the author of 389ac4b authored this record)
independent review          see the episode report accompanying these bytes
canonical mutation          none
public summary repair       none (intentionally deferred)
number assignment           none
staged / committed / pushed none
```
