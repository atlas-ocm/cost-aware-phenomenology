# Semantic Review Subject Omission

**Unofficial draft. NON-CANONICAL. `WITHDRAWN_TRIGGER_FALSIFIED` — superseded forensic dossier. Not a canonical AICE code.**

> ⛔ **WITHDRAWN — DO NOT USE AS EVIDENCE OF AN INCIDENT.** This dossier's originating episodes
> were later shown by stronger **primary** evidence to *falsify* load-bearing trigger predicates
> (the reviewable subject was present and consumed). It is retained, not deleted, for provenance
> and as a **negative control**. It is not an active candidate, reserves no number, and may not be
> promoted from its cited episodes. See **Retraction Determination** below. The original hypothesis
> and all analysis are preserved unchanged for the historical record.

See [the candidate surface README](./README.md) for the authority status of this directory and the
`WITHDRAWN_TRIGGER_FALSIFIED` lifecycle. This record reserves no number and defines no canonical
code.

## Identity

| Field | Value |
|---|---|
| working_title | Semantic Review Subject Omission |
| machine_name | `SEMANTIC_REVIEW_SUBJECT_OMISSION` |
| previous_proposed_working_title | Verifier Subject Evidence Omission |
| previous_proposed_machine_name | `VERIFIER_SUBJECT_EVIDENCE_OMISSION` |
| status | `WITHDRAWN_TRIGGER_FALSIFIED` |
| active_candidate | `false` |
| canonical_code | `UNASSIGNED` |
| canonical_number_reserved | `false` |
| promotion_status | `FORBIDDEN_FROM_CITED_EPISODES` |
| dossier_retention | `SUPERSEDED_FORENSIC_RECORD` |
| primary_episode_status | `FALSIFIED` |
| abstract_boundary_status | `HYPOTHETICAL_UNVALIDATED` |
| reopen_condition | `NEW_INDEPENDENT_PRIMARY_EPISODE_SATISFYING_ALL_TRIGGER_PREDICATES` |
| original_source_class | `OPERATOR_SUPPLIED_EPISODE_REPORT` |
| original_raw_trace_attached | `false` |
| superseding_evidence_class | `PERSISTED_PRIMARY_EVIDENCE_REVIEW` |
| superseding_evidence_result | `FALSIFIES_ORIGINATING_EPISODES` |

> The previous proposed identity is historical working provenance only. It is **not** a second
> candidate, and the withdrawal targets the **current** identity `SEMANTIC_REVIEW_SUBJECT_OMISSION`
> (`PREVIOUS_PROPOSED_IDENTITY != CURRENT_CANDIDATE_IDENTITY`). The preferred name centers the
> omission of the *review subject* rather than evidence *about the verifier*.

## Retraction Determination

The candidate was initially raised from an operator-supplied episode report claiming that the
real-repository verifier handoff contained hashes, tests, or narrative but **omitted** the changed
executable subject. A later falsification-first investigation inspected **persisted primary
evidence** and established the opposite.

Primary evidence inspected (authorized external scratch; read-only):

```
episode DB:        F:/tmp/cap_processor_e2e_loop_episode_evolution_v0/c2b1a_episode.db
                     attempt sha256:7734fa4e…  state=COMPLETED_PASS
verifier bundle:   .../651b714ddba64ce3/bundle.json   (verifier_job_id sha256:651b714d…)
anchored receipt:  .../c2b1a_receipts/anchored_1784817977159-20260723T144617Z.json
                     receipt_hash sha256:bb076a07…   head 5779a12a…
evidence object:   .../_source_store/51c29f2e…   (3735 bytes; recomputed sha256 == 51c29f2e…)
preimage snapshot: .../c2b1a_receipts/preimage_anchored_1784817977159_3bc1e32e9f89c7a7.snap
```

Findings:

- the examined persisted real-repository B1a verifier bundle contained a non-empty `patch_text`;
- `patch_text` was a real preimage-to-postimage unified diff
  (`--- a/… +++ b/… @@ -238,6 +238,46 @@ …`) with bound `before_hashes`/`after_hashes`;
- exact changed executable bytes were present for `MCP/cap_mvp_auto_real_repo_coder_v0.py`;
- handoff identity was bound to the diff-bearing evidence: `patch_handoff_sha256 =
  sha256:51c29f2e…` equals the attempt `evidence_hash` and `transport_proof.evidence_hash`, and the
  evidence object's recomputed SHA-256 equals that value;
- verifier semantic findings cited exact changed lines and introduced identifiers
  (`…coder_v0.py:241-281 — inserts _extract_ops_json and _build_anchored_ops_prompt …`);
- therefore the subject was **available and consumed**;
- hashes and tests were supplemental evidence, not substitutes for absent code.

Decisive predicate result:

```
P1 semantic review required:           VERIFIED
P2 authoritative subject identified:   VERIFIED
P3 reviewable subject unavailable:     FALSIFIED
P4 only derived evidence supplied:     FALSIFIED
P5 semantic PASS claimed:              VERIFIED
P6 authority governed an omitted subject: FALSIFIED
```

```
ANY REQUIRED TRIGGER PREDICATE FALSIFIED  →  INCIDENT NOT ESTABLISHED
```

```
SEMANTIC_REVIEW_SUBJECT_OMISSION:  FALSIFIED_FOR_ORIGINATING_EPISODES
CANDIDATE_ROOT_CAUSE_CLAIM:        RETRACTED
PROMOTION_FROM_CITED_EPISODES:     FORBIDDEN
```

## Honesty caveat — smoke path is not this incident

A distinct non-real-repository **smoke** path may populate `patch_text = ""`. That code property
does **not** establish this incident, because:

- the examined real-repository B1a episodes did not use that path;
- no persisted semantic PASS on an omitted subject was established for it;
- a possible empty-subject path is not equivalent to an observed accepted semantic verdict on it.

```
EMPTY_PATCH_CAPABLE_PATH_EXISTS  !=  SEMANTIC_REVIEW_SUBJECT_OMISSION_OCCURRED
```

This smoke-path observation may motivate a future robustness fixture or fail-closed gate, but it
**cannot** reactivate this candidate.

## Retained negative-control value

The dossier is retained partly to prevent future classifiers from repeating the same false
positive.

```
Given:  semantic code review required;
        exact unified diff embedded in authoritative verifier handoff;
        handoff identity bound to transport evidence;
        verifier findings cite exact changed lines and identifiers;
        semantic PASS emitted.
Expected:
        REVIEWABLE_SUBJECT_AVAILABLE = true
        SUBJECT_CONSUMED = true
        SEMANTIC_REVIEW_SUBJECT_OMISSION = false
```

```
HASHES_HEAVY_PRESENTATION_RECEIPT != HASHES_ONLY_VERIFIER_HANDOFF
PRESENTATION_RECEIPT              != AUTHORITATIVE_ASSIGNMENT_ENVELOPE
REPORT_ABOUT_VERIFIER_INPUT       != VERIFIER_INPUT
```

## Downstream authority correction

Recorded without modifying cap-processor:

```
VERIFIER_EXACT_DELTA_EVIDENCE_BOUNDARY:
  root_cause_fix_authority:       RETRACTED
  mandatory_implementation_authority: ABSENT
  optional_robustness_status:     MAY_BE_RECONSIDERED_ONLY_WITH_NEW_MEASURABLE_VALUE_EVIDENCE
  possible_future_value:          [identity binding, fail-closed completeness, lower variance]
```

Exact-delta work is **not** authorized as a fix for the falsified hashes-only / code-delivery
defect; it is not claimed to have no conceivable value. The separately observed failure shape was:

```
observed_failure:                 REASONING_OUTPUT_BUDGET_EXHAUSTION_SHAPED
semantic_effect_when_output_empty: NO_SEMANTIC_VERDICT, STATE_UNCHANGED
```

Ordinary output-budget exhaustion does not by itself warrant a new AICE candidate unless a separate
episode establishes an unauthorized semantic transition.

---

*The following sections preserve the original (now falsified) hypothesis unchanged, for the
historical record.*

## Source and provenance limits

The evidence for this candidate is an operator-supplied report from another execution window.
The report establishes: a semantic code review was required; changed executable bytes were not
delivered or otherwise made reviewable to the verifier; hashes, tests, identity information, or
narrative evidence were supplied; the verifier was invoked through a reachable transport; a
semantic PASS / completed-review authority was nevertheless claimed; and the exact executable
delta was required to perform the claimed review.

```
source_class:                           OPERATOR_SUPPLIED_EPISODE_REPORT
raw_trace_attached:                     false
exact_review_packet_attached:           false
exact_changed_bytes_attached:           false
verifier_subject_access_trace_attached: false
verifier_consumption_witness_attached:  false
```

No raw transport logs, exact changed bytes, complete verifier prompts, repository snapshots, or
receipts are attached or inspected. This provenance permits a provisional record. It does **not**
permit canonical promotion.

## Core definition

A semantic review is declared complete, successful, or PASS even though the verifier did not have
access to the exact subject required by the review contract. Instead, derived or descriptive
evidence about the subject is supplied as a substitute — subject identifiers, hashes, test
results, manifests, summaries, receipts, declared path lists, author descriptions, claimed
behavior, or build/validation status.

These may be valid *supplemental* evidence. They do **not** replace the executable bytes, exact
normalized delta, frozen repository state, or equivalent reviewable subject needed for semantic
review.

The incident does **not** imply that the verifier is non-independent, that the tests did not run,
that the hashes are incorrect, that the subject does not exist, that transport failed, or that
the supplied derived evidence is worthless. It concerns *claimed semantic-review authority
without a reviewable semantic subject.*

```
DERIVED_EVIDENCE_ABOUT_CODE  !=  CODE_AVAILABLE_FOR_SEMANTIC_REVIEW
```

## Reviewable subject definition

A reviewable subject may be supplied through any one of the following, provided its exact identity
and verifier access are established:

- exact changed executable bytes;
- exact normalized preimage-to-postimage delta;
- exact frozen repository or worktree state;
- immutable commit or artifact locator with proven verifier read access;
- equivalent immutable subject representation sufficient for the contracted semantic review.

Therefore:

```
BYTES_NOT_EMBEDDED_IN_REVIEW_PACKET  !=  SUBJECT_OMITTED
```

…when the verifier can independently retrieve and inspect the exact frozen subject. The
load-bearing condition is:

```
REVIEWABLE_SUBJECT_AVAILABLE_TO_VERIFIER = false     (load-bearing)
BYTES_INLINE_IN_PROMPT = false                        (NOT sufficient by itself)
```

## Trigger predicates — all required

The candidate fires only when all hold:

1. The contracted review kind requires semantic inspection of executable material.
2. The authoritative review subject is identified or claimed.
3. The verifier cannot inspect the exact required subject through: supplied exact bytes; an exact
   normalized delta; an exact frozen repository state; or an immutable locator with proven read
   access.
4. The verifier instead receives only derived or descriptive evidence — hashes, test outcomes,
   manifests, summaries, receipts, filenames, path lists, or claimed semantic conclusions.
5. A semantic terminal is nevertheless emitted or accepted: `PASS`, `APPROVED`,
   `SEMANTIC_REVIEW_COMPLETE`, `VERIFIED`, `NEEDS_NO_FIX`, `RELEASE_READY`, or equivalent.
6. The accepted terminal claims authority over the omitted subject.

A missing inline patch is **not** sufficient when the verifier has proven access to the exact
frozen subject elsewhere. A hash or test report is **not** sufficient when semantic code
inspection is part of the required review contract.

## Forbidden substitutions

```
SUBJECT_IDENTITY + HASHES + TEST_RESULTS + NARRATIVE
  must not impersonate
REVIEWABLE_SUBJECT_EVIDENCE
```

```
SUBJECT_HASH_KNOWN      != SUBJECT_SEMANTICS_REVIEWED
TESTS_PASSED            != CODE_INSPECTED
VERIFIER_INVOKED        != SUBJECT_REVIEWED
SUBJECT_ATTACHED        != SUBJECT_CONSUMED_BY_VERIFIER
TRANSPORT_COMPLETED     != SEMANTIC_REVIEW_COMPLETED
RECEIPT_FOR_THE_SUBJECT != SUBJECT_AVAILABLE_FOR_REVIEW
```

**Core formula:** a receipt for the suitcase is not the contents of the suitcase.

## Required terminal

When the trigger is established:

```
transport_status:          PRESERVED_AS_OBSERVED
verifier_independence:      PRESERVED_IF_OTHERWISE_ESTABLISHED
hashes_and_test_results:    PRESERVED_AS_DERIVED_EVIDENCE
semantic_review:            UNVERIFIABLE
semantic_review_authority:  DENIED
semantic_pass:              FORBIDDEN
workflow_effect:            SEMANTIC_REVIEW_STATE_UNCHANGED
required_next_evidence:     EXACT_REVIEWABLE_SUBJECT
```

The required next evidence may be: exact executable bytes; exact normalized delta; exact frozen
repository state; an immutable locator with proven verifier read access; or an equivalent review
substrate sufficient for the contracted scope.

Do **not** invalidate genuine test results merely because they cannot substitute for semantic
review. Do **not** declare the artifact nonexistent merely because the verifier could not inspect
it.

## False-positive boundary

Do **not** classify as this incident when:

- the verifier has read-only access to the exact frozen subject;
- the verifier retrieves the subject through an immutable verified locator;
- exact bytes are not embedded in the prompt but are independently accessible;
- the contracted review is explicitly integrity-only;
- the contracted review is explicitly test-result-only;
- the contracted review does not require executable semantic inspection;
- hashes and test results are presented only as supplemental evidence;
- the verifier returns `UNVERIFIABLE` or `BLOCKED` instead of semantic PASS;
- no executable bytes changed and the requested scope does not require their inspection;
- a generated artifact is reviewed through a valid alternative subject contract bound to exact
  source and build provenance;
- an exact normalized delta is supplied even when the full repository is not;
- the verifier demonstrably opens and consumes the exact subject.

The incident concerns *unauthorized semantic-review authority*, not every review packet that omits
inline source code.

## Required controls

### Negative control — exact repository access (must not fire)

```
Given:  semantic code review required;
        patch bytes are not embedded in the prompt;
        verifier has read-only access to exact frozen commit C;
        commit identity is bound;
        verifier opens the changed files and completes review.
Expected: NO SUBJECT-OMISSION INCIDENT
```

### Negative control — narrower review contract (must not fire)

```
Given:  review kind is integrity-only;
        subject hash and provenance are available;
        semantic code review is not claimed.
Expected: NO SUBJECT-OMISSION INCIDENT
```

### Incident fixture (should fire)

```
Given:  semantic code review required;
        changed executable bytes exist;
        verifier receives only hash, tests, manifest, and author summary;
        verifier cannot retrieve exact bytes or exact delta;
        semantic PASS is accepted.
Expected: SEMANTIC_REVIEW_SUBJECT_OMISSION
          SEMANTIC_REVIEW = UNVERIFIABLE
          SEMANTIC_PASS = FORBIDDEN
          TESTS_AND_HASHES = PRESERVED
          EXACT_REVIEWABLE_SUBJECT = REQUIRED
```

### Positive closure control (may emit a verdict)

```
Given:  exact normalized delta supplied;
        subject hash bound;
        verifier independently consumes the delta;
        review scope completed against that exact subject.
Expected: SEMANTIC REVIEW MAY EMIT A VERDICT
```

## Comparison with canonical AICE

### AICE-604 — Hash Exists, Reality Not Found (nearest)

Overlap: a hash or declared identity exists while required underlying bytes are not established or
available.

Distinction: [`AICE-604`](../codes/AICE-604.md) concerns failure to establish artifact reality
from a hash claim. `SEMANTIC_REVIEW_SUBJECT_OMISSION` permits the subject to *physically exist and
be correctly hash-identified*, while remaining unavailable to the semantic verifier; the
specialized defect is accepting completed semantic-review authority without verifier access to the
subject.

Possible co-emission:

```
artifact bytes absent or irretrievable                         → AICE-604-shaped
artifact exists but verifier cannot inspect it and PASS claimed → SEMANTIC_REVIEW_SUBJECT_OMISSION-shaped
both conditions established                                     → both may apply
```

### AICE-606 — PASS Exists, Test Run Not Found

Not applicable merely because semantic review is unverifiable; [`AICE-606`](../codes/AICE-606.md)
tests may genuinely have run and may remain valid.

### AICE-608 — Verification Exists, Independence Not Found

Distinct: the verifier may be genuinely independent; the missing element is the *reviewable
subject*. [`AICE-608`](../codes/AICE-608.md) may co-emit if independence is also absent.

### AICE-609 — Consensus Exists, Evidence Not Found

Nearby because required semantic-review evidence is absent. Distinction: this candidate identifies
the *specialized substitution of derived evidence for the primary semantic-review substrate*. Use
generic [`AICE-609`](../codes/AICE-609.md) when no more precise subject-omission boundary is
established.

### AICE-610 — Control Exists, Enforcement Not Found

[`AICE-610`](../codes/AICE-610.md) may co-emit when semantic subject binding is declared as a
control but not enforced in the authoritative review path. Distinction: AICE-610 diagnoses the
missing causal enforcement; this candidate diagnoses the resulting *claim of completed semantic
review without the reviewable subject*.

### Not AICE-611 / 612 / 614 / 616 / 602

- [`AICE-611`](../codes/AICE-611.md) — not applicable merely because the verifier cannot inspect
  the subject; transport and verifier invocation may be genuinely reachable.
- [`AICE-612`](../codes/AICE-612.md) — no actor-specific execution/observation path is transferred
  by this incident.
- [`AICE-614`](../codes/AICE-614.md) — not applicable when verifier transport completed and the
  omission is in the review payload or subject-access contract.
- [`AICE-616`](../codes/AICE-616.md) — distinct: AICE-616 concerns a supplied review delta
  *contaminated* by bytes outside the current episode; this candidate concerns *absence of any
  sufficient reviewable subject*.
- [`AICE-602`](../codes/AICE-602.md) — not applicable; no gateway authority-context substitution,
  authorized-denial branch, or untrusted-admission branch. Do not broaden AICE-602 into a generic
  missing-context or missing-evidence code.

> **No AICE-617 comparison.** `AICE-617` is canonically **unassigned** and has no semantics; a
> differential comparison with it is forbidden — it would quietly manufacture a meaning for 617.

### Open taxonomy question

Is omission of the semantic-review substrate sufficiently distinct from AICE-604, AICE-609, and
enforcement-shaped AICE-610 to deserve an independent canonical code?

```
Current answer: PROVISIONALLY_YES
                CANONICAL_PROMOTION_NOT_AUTHORIZED
```

## Portable CAP enforcement requirement (non-implemented)

Associated pattern: `SEMANTIC_REVIEW_SUBJECT_BINDING_BOUNDARY`.

**Core law:** a semantic verdict requires the verifier to have reviewable access to the exact
subject governed by that verdict.

Minimum future typed fields:

```
review_id                       verifier_subject_access
review_kind                     verifier_subject_access_method
review_scope                    subject_consumed_by_verifier
subject_id                      consumed_subject_hash
subject_hash                    derived_evidence_ids
subject_form                    transport_status
subject_locator                 verifier_identity
subject_frozen                  verifier_independence
exact_delta_available           semantic_review_status
                                semantic_verdict
```

Required deterministic gate:

```
if:
  review_kind = SEMANTIC_CODE_REVIEW
  and reviewable_subject_available_to_verifier = false
then:
  semantic_review_status = UNVERIFIABLE
  semantic_verdict = FORBIDDEN
  semantic_review_authority = DENIED
  required_next_evidence = EXACT_REVIEWABLE_SUBJECT
```

Required subject-consumption witness:

```
subject_locator_resolved
verifier_opened_subject
verifier_observed_subject_hash
consumed_subject_hash = authoritative_subject_hash
review_scope_completed_against_consumed_subject
```

Required invariants:

```
SUBJECT_AVAILABLE        != SUBJECT_CONSUMED
SUBJECT_HASH_DECLARED    != SUBJECT_HASH_OBSERVED_BY_VERIFIER
VERIFIER_CALLED          != REVIEW_SCOPE_COMPLETED
```

```
FUTURE_IMPLEMENTATION_TARGET = cap-processor
IMPLEMENTATION_STATUS = NOT_STARTED
MCP_STATUS = NOT_CONNECTED
```

This section is a specification handoff only. Nothing is implemented here and cap-processor is not
modified by this record.

## Promotion gate

Future canonical promotion requires, in a separate episode:

1. exact source episode preserved;
2. authoritative review contract preserved;
3. authoritative subject identity preserved;
4. verifier packet or subject-access path preserved;
5. proof that the subject was unavailable or unconsumed;
6. semantic PASS or completed-review claim preserved;
7. trigger predicates independently reviewed;
8. distinction from AICE-604 established;
9. distinction from generic AICE-609 established;
10. relationship to AICE-610 established;
11. false-positive boundary accepted;
12. negative, incident, and closure controls accepted;
13. portable CAP enforcement requirement specified;
14. independent semantic verifier PASS on the candidate bytes;
15. explicit operator authorization to assign a number;
16. canonical registry / schema / code / example changes in a separate episode;
17. tests, commit, publication, and remote readback performed separately.

No promotion requirement is satisfied merely because this file exists or receives a provisional
verifier PASS.

## Verification status

```
AUTHOR_SELF_REVIEW          = present (not independent)
INDEPENDENT_SEMANTIC_REVIEW = pending on these bytes (read-only verifier when available)
CANONICAL_PROMOTION         = NOT_AUTHORIZED
```
