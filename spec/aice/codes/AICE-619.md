# AICE-619 — Registry Entry Exists, Summary Not Found

**Unofficial draft (AICE v0.12.0).**

## Canonical identifier

`AICE-619`

## Human-readable alias

`HTTP 619 — Registry Entry Exists, Summary Not Found`

The canonical title is `Registry Entry Exists, Summary Not Found` (the AICE-604 / AICE-607 /
AICE-617 pattern: _X Exists, Y Not Found_). The descriptive alias
`Implementation Exists, Documentation Not Found` is presentation metadata only. The canonical
machine identity is `AICE-619` / `CANONICAL_SUMMARY_ENTRY_OMISSION`.

A plural rendering — _Registry Entries Exist, Summary Not Found_ — is an episode-specific
presentation of an instance with more than one omitted entry. It carries no separate class
identity; the singular title is canonical.

## Intent

Catch the case where the canonical bytes are **correct** and the reader is nonetheless **not
served them**. A canonical entry is implemented and published; a public summary that presents
itself as the current projection of that canonical registry has its currency asserted for the
release; the entry is absent, stale, or contradicted in that summary; and publication closure
is claimed anyway.

Canonical machine name: `CANONICAL_SUMMARY_ENTRY_OMISSION`.

The defect is in the **projection**, not in the canonical source. The remedy is therefore
never to retract the entry, roll back the release, or claim the implementation is absent —
only to reconcile the projection.

Canonical boundary:

```
CANONICAL SET   must equal   ITS PUBLISHED PROJECTION

ENTRY_PRESENT_IN_REGISTRY  != ENTRY_PRESENT_TO_THE_READER
CHECKER_PASS               != PUBLIC_SUMMARY_PARITY_ESTABLISHED
DOCUMENT_UPDATED           != DOCUMENT_COMPLETE
PREVIOUS_VERIFIER_PASS     != PASS_FOR_MUTATED_BYTES
```

## Trigger condition

All of the following hold:

1. the canonical entry exists (`CANONICAL_ENTRY_EXISTS`);
2. it is included in a published release (`CANONICAL_ENTRY_IS_PUBLISHED`);
3. a public summary exists (`PUBLIC_SUMMARY_EXISTS`);
4. that summary purports to represent the current canonical set
   (`PUBLIC_SUMMARY_PURPORTS_TO_REPRESENT_CURRENT_CANONICAL_SET`);
5. its currency for the current release was asserted — its enumeration was edited in the
   release, or the document was explicitly restamped or reaffirmed as the current
   projection (`PUBLIC_SUMMARY_CURRENCY_ASSERTED_FOR_CURRENT_RELEASE`); an edit that
   neither touches the enumeration nor asserts currency does not qualify;
6. the entry is absent, stale, or contradicted there
   (`CANONICAL_ENTRY_ABSENT_STALE_OR_CONTRADICTED_IN_SUMMARY`);
7. publication or documentation closure is claimed
   (`PUBLICATION_OR_DOCUMENTATION_CLOSURE_CLAIMED`).

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

Predicate 5 is load-bearing and distinguishes this incident from ordinary documentation
debt, and the discriminating act is the **currency assertion**, not the byte-touch. A
summary whose enumeration was edited in the release, or which was explicitly reasserted as
current for it, and still omits a published entry, is a failed projection. A summary nobody
touched is stale documentation — and so is one that received only an incidental edit
(formatting, a link fix) that neither engaged the enumeration nor asserted currency. A
release-number restamp **is** a currency assertion: a document that says it is current for
this release and omits a published entry fails as a projection, whatever else was edited.

```
SUMMARY_TOUCHED_IN_RELEASE   != SUMMARY_CURRENCY_ASSERTED
CURRENCY_ASSERTED_AND_SHORT  -> FAILED_PROJECTION
TOUCHED_BUT_NO_ASSERTION     -> DOCUMENTATION_ROT
```

## Required observations

Evidence classes include: the canonical entry in its authoritative source, machine-parsed
rather than read from prose; independent confirmation that the release carrying it is
published (a remote ref, a readback, a persisted artifact — not a console receipt line
recoverable only from a transcript); the public summary's own defined set, machine-parsed from
its rows or list items; the summary's scope framing, quoted from the document itself; the diff
showing the summary was edited or reaffirmed in the release; the closure claim; and the reason
existing automation did not detect the mismatch. Set membership on both sides MUST be parsed,
never inferred from surrounding prose — the surrounding prose is frequently correct while the
enumeration is not, and that divergence is the incident.

## Missing-evidence condition

No evidence exists that the published projection was ever compared to the canonical set. The
closure claim rests on checks whose scope excludes the summary: the canonical source is
validated, the entry is tested, the release is verified, and no surface anywhere is capable of
observing that the reader-facing enumeration is short. A genuine PASS on every existing check
would still be silent here.

## False-positive guards

AICE-619 MUST NOT fire when:

- the document explicitly states it contains **selected examples only**;
- the document is clearly archived or pinned to an older named release;
- the omitted entry is intentionally internal and no public projection is required;
- the canonical entry is itself unpublished — the summary is then *correct*;
- the summary is generated from a different, explicitly declared scope;
- publication closure has not been claimed and the release is openly marked in flight;
- a transient rendering or cache problem exists while the committed source bytes are correct.

```
INTENTIONALLY_PARTIAL_VIEW != INCOMPLETE_CANONICAL_PROJECTION
```

A table framed as a current registry summary is **not** presumed partial merely because rows
are missing. The presumption of completeness must be defeated by an explicit scope statement
in the document itself; it may never be inferred from the omission, and it may never be
supplied retroactively once the omission is found.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_RELEASE
```

`BLOCK_RELEASE` here blocks **publication closure**, not the published canonical bytes. The
release is not retracted, the entry is not removed, the implementation is not called absent.
What is refused is the claim that publication is complete. Two further requirements are
normative but carry no separate enum value in the envelope, and belong in `required_action`:
reconcile the public summary, and establish canonical-to-public set parity. Retryability:
`requires_state_materialization` — the projection must actually be repaired; restating that
the registry is correct resolves nothing.

Minimum repair postcondition:

```
PUBLIC_SUMMARY_DEFINED_SET = CANONICAL_REGISTRY_DEFINED_SET
```

## Remediation

Reconcile the projection against the canonical source, taking titles, identifiers, and effects
**from the source rather than re-authoring them** — a hand-written row that disagrees with the
registry converts an omission into a contradiction. Then add a deterministic parity check that
parses both sets and fails on any missing or extra member, and cover it with an adversarial
tamper test, so the next omission is caught by machinery rather than by a reader. Finally,
re-freeze and independently review the repaired bytes: the earlier verifier pass does not
transfer across a mutation.

```
PREVIOUS_VERIFIER_PASS != PASS_FOR_MUTATED_BYTES
```

## Differentials

- **AICE-605 — Release Exists, Implementation Not Found.** The nearest inverse. 605 requires a
  release claim while the implementation is absent. Here the implementation is present *and*
  the release is present; only the projection is incomplete. The polarity is inverted.
- **AICE-604 — Hash Exists, Reality Not Found.** 604 concerns a claimed artifact identity whose
  bytes are absent or unverified. In 619 the canonical bytes exist and read back correctly.
- **AICE-608 — Verification Exists, Independence Not Found.** In 619 the reviewer may be fully
  independent; the review **contract** simply did not enumerate the projection. Independence is
  not the defect — scope is.
- **AICE-610 — Control Exists, Enforcement Not Found.** 610 requires a declared control that
  is successfully constructed, persisted, parsed, or validated, and whose result is bypassed.
  619 typically arises where **no** parity control was ever declared. See conditional
  co-emission below.
- **AICE-617 — Work Exists, Result Not Found.** 617 concerns process substituting for the
  target outcome. In 619 the outcome genuinely exists; the documentation does not expose it.

## Conditional AICE-610 co-emission

Do not emit AICE-610 merely because the omission went undetected. Emit it only when an
independent predicate holds: `SUMMARY_PARITY_CONTROL_DECLARED = true` — a parity control is
claimed to govern publication and the release path does not consume its result. Where no such
control was ever declared, there is no declared-but-unenforced control and AICE-619 stands
alone.

## Example

`REPRESENTATIVE_EXAMPLE` — derived from an observed episode in this repository.

A registry defines eighteen codes. The document headed `## 6. Registry summary` carries
sixteen rows; two published codes have no row and never had one. The same table was edited in
the publication commit to add the newest code's row, and the prose two lines below the table
restates the full contiguous set correctly. Commit, push, remote readback, checker exit 0, and
a passing test suite are all claimed as closure. The integrity checker reads that document
only for relative-link resolution, so no surface could have observed the gap. All seven
predicates hold and AICE-619 fires: block publication closure, add the missing rows from the
registry values, add a parity guard with a tamper test, and re-review the repaired bytes.

Negative shapes that are **not** AICE-619: a document headed "Selected AICE codes
(illustrative subset)" listing five of eighteen (predicate 4 fails); a `CHANGELOG-v0.9.md`
showing a seventeen-code table after v0.10.0 ships (predicates 4 and 5 fail — it is pinned);
a current-looking summary that received only a formatting or typo edit in the release, with
no enumeration change and no currency restamp (predicate 5 fails — documentation rot, not a
failed projection);
a code document drafted in a working tree, absent from the published registry and therefore
absent from the summary (predicate 2 fails — the summary is correct); a table known to be
incomplete in a release explicitly marked in progress with no closure asserted (predicate 7
fails — this is honest work in flight).

See
[`../../../examples/aice/aice-619-canonical-summary-entry-omission.json`](../../../examples/aice/aice-619-canonical-summary-entry-omission.json).

## Promotion provenance and operator waiver (non-normative)

This code was promoted on **one** observed instance. Its candidate record required, as a
promotion condition, *a second independent primary instance, ideally outside this repository*.
That condition was **not met**. The operator waived it explicitly on 2026-07-25. The waiver is
recorded here rather than left implicit, because a reader is entitled to know how thin the
evidentiary base of a canonical code is.

Instance ledger at promotion — one qualifying, three examined and rejected:

| Candidate instance | Verdict |
|---|---|
| The registry-summary table at the published commit: 16 rows against 18 defined codes, both sets machine-parsed | **qualifying** — `PRIMARY_PERSISTED`, published, origin-verified |
| A second in-repository document of the same shape, listing an obsolete set | rejected — untracked, therefore unpublished; predicates 2 and 7 fail |
| A published index line naming a stale specification version | rejected — it projects a *version*, not a defined set, so the parity boundary cannot be evaluated. Adjacent shape, not an instance |
| Mirrored copies of the code index in four external repositories — recorded at promotion as **eleven**, corrected in v0.12.0 to **twelve** | rejected at promotion as "verified negative — all correct and complete against the published registry". That sentence was recorded without repository identities, revisions, parsed sets, or a persisted sweep artifact, so it was never independently checkable, and its count was arithmetically wrong. Superseded by the v0.12.0 sweep correction below |

The rationale offered for the waiver is that the mechanism is structural rather than local: an
integrity check that validates machine-readable artifacts while treating the human-readable
projection only as a link target cannot observe this defect in *any* project organised that
way. That is an argument, not a second instance, and it is recorded as such.

**Measurement warning.** During the promotion search, an automated sweep reported the
external copies (then recorded as eleven; see the correction below) as instances of this very
incident. That finding was false: the copies had been
measured against an uncommitted working tree rather than against published bytes. This
incident's predicates 2 and 7 require a *published* canonical entry and a *claimed* closure. A
projection cannot lag a version that has not been released.

```
UNCOMMITTED_WORKING_TREE != CANONICAL_PUBLISHED_STATE
PROJECTION_BEHIND_UNRELEASED_CANON != CANONICAL_SUMMARY_ENTRY_OMISSION
```

### Projection-sweep correction (v0.12.0, 2026-07-25)

Two defects in the ledger row above are corrected here rather than silently rewritten:

1. **The count was arithmetically false.** The physical inventory contains **twelve**
   mirror surfaces, not eleven: four repositories, each carrying `AGENTS.md`, `GEMINI.md`,
   and `.claude/skills/aice-core/SKILL.md`.
2. **The rejection was not falsifiable.** "Verified negative" was published with no
   repository identities, revisions, parsed sets, or persisted result, so no reader could
   re-establish or refute it — which an independent verifier duly reported against
   v0.11.0.

Re-sweep, machine-parsed, with the identities the original row lacked. The four
repositories are local working copies with no configured remotes; they are identified by
path and by `HEAD` at sweep time, and every surface file is git-tracked (working trees
carried unrelated local modifications when swept):

| Repository | HEAD at sweep |
|---|---|
| `F:\VibeCoding\Atlas` | `11c0ff80e8146fdec30322d6acd8e2d38e622692` |
| `F:\VibeCoding\Concept-Arena` | `42c1dacba5a3cc67ccf589ce299532262b4c06ea` |
| `F:\VibeCoding\cap-processor` | `f64c8d81de29963fa08525719754233a462f2e20` |
| `F:\VibeCoding\v5.com.ua` | `6bd7bc38b97e0a0f6982f006799e4c0731b90170` |

Distinct surface contents by SHA-256 (twelve surfaces, four distinct byte states):

- `2709895a2f340a3e30f99bc858e29d2a9a7599f110f0eba01d2defd2986a0153` — `AGENTS.md` in
  Atlas and Concept-Arena;
- `9d5f70cf676a47cee2489e9a4f5159c9826e5b95b3560b7640d3565328762d9e` — `AGENTS.md` in
  v5.com.ua;
- `8ed5b79becb7162dbb35a563512708a900b28ef2039ee0b05ad2bd199f2ccd48` — `GEMINI.md` in all
  four repositories, and `AGENTS.md` in cap-processor;
- `e0fbde29e6b0412403b948fbce9486231963420d22a38292e45e301668701e50` —
  `.claude/skills/aice-core/SKILL.md` in all four repositories.

**Parsed result — enumeration-parsed, not mention-counted: all twelve surfaces pin
`AICE_VERSION = 0.10.0` and `DEFINED_CODE_COUNT = 18`, enumerate exactly
`AICE-601`…`AICE-618`, assert that `AICE-600` and `AICE-619` "are not defined", and do not
mention `AICE-620` at all.** Against the published v0.11.0 canon every mirror therefore
lags by two codes, and its `AICE-619` sentence is a false statement about the current
canon, not merely an omission. The promotion-time sentence "all were correct and complete
against the published registry" is accordingly false as a statement about the current
state. These twelve lagging surfaces are still **not** qualifying AICE-619 instances, on
two independent grounds: each document pins itself to the older named release 0.10.0,
which is this code's own pinned-view false-positive guard; and none was edited or
restamped as current for the v0.11.0 release, so under corrected predicate 5 no currency
assertion exists. They are pinned, unsynced projections pending reconciliation, not failed
projections. (An earlier draft of this very section reported the parsed set as
`AICE-601`…`AICE-619` by counting token mentions — the denial sentence mentions
`AICE-619` — which is exactly the parse-don't-infer error the Required observations
section forbids; corrected here from enumeration rows.) What would falsify this record:
any listed surface at the listed revision parsing to a different enumeration. a genuine second primary instance, ideally in another project,
strengthens the class and retires the waiver. Evidence that the single observed instance was in
fact a declared partial view falsifies predicate 4 and undermines the promotion — see the
reopen rule in the candidate record. Note that the registry provides no rename, supersede, or
retire mechanism, so a withdrawal would not be clean.

## Related codes

- [`AICE-604`](./AICE-604.md) — a declared artifact whose materialization evidence is absent (619's canonical bytes exist and read back).
- [`AICE-605`](./AICE-605.md) — a release claim without an implementation (the inverse polarity of 619).
- [`AICE-608`](./AICE-608.md) — verification without independence (619 survives a fully independent reviewer whose contract omitted the artifact).
- [`AICE-610`](./AICE-610.md) — a control that exists but is not enforced (conditionally co-emitted; not required by 619).
- [`AICE-617`](./AICE-617.md) — process activity substituting for the product outcome (in 619 the outcome exists and only its projection is short).
