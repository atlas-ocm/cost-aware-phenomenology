# Post-Observation Evaluation Mutation

**Unofficial draft. NON-CANONICAL provisional candidate. Not a canonical AICE code.**

See [the candidate surface README](./README.md) for the authority status of this directory.
This record reserves no number and defines no canonical code.

## Identity

| Field | Value |
|---|---|
| working_title | Post-Observation Evaluation Mutation |
| machine_name | `POST_OBSERVATION_EVALUATION_MUTATION` |
| previous_working_title | Post-Hoc Admission Rule Mutation |
| previous_machine_name | `POST_HOC_ADMISSION_RULE_MUTATION` |
| status | `EVIDENCE_BACKED_PROVISIONAL` |
| canonical_code | `UNASSIGNED` |
| canonical_number_reserved | `false` |
| long_state_signature | `EVIDENCE_VALID_VERDICT_INVALIDATED_BY_POST_OBSERVATION_EVALUATION_MUTATION` |
| source_class | `OPERATOR_SUPPLIED_EPISODE_REPORT` |
| raw_trace_attached | `false` |

> **Revision note.** This candidate was renamed from *Post-Hoc Admission Rule Mutation*
> (`POST_HOC_ADMISSION_RULE_MUTATION`). The earlier name is preserved above as the previous
> working name. The defect arises **earlier** than the final admission verdict: not only the
> final admission rule can mutate, but the entire *semantic evaluation contract*. Therefore:
>
> ```
> ADMISSION_RULE_MUTATION  ⊂  SEMANTIC_EVALUATION_CONTRACT_MUTATION
> ```

## Source and provenance limits

The evidence for this candidate is an operator-supplied report from another execution window.
The report states: data and model outputs were valid; the strategy named "straight" led on the
evaluated corpus; a confirming safety/admission verdict was not authorized; the decision rules
had changed after outcome observation; the corrected classification was `EXPLORATORY_POST_HOC`;
and a new holdout evaluated under already-frozen rules is required.

```
source_class:                    OPERATOR_SUPPLIED_EPISODE_REPORT
raw_trace_attached:              false
frozen_original_contract_attached: false
frozen_modified_contract_attached: false
exact_outcome_timeline_attached: false
```

No raw experiment logs, original/modified contract bytes, timestamps, dataset manifests, model
outputs, or verifier receipts are attached or inspected. This provenance permits a provisional
record. It does **not** permit canonical promotion.

## Core definition

A confirmatory admission, safety, validation, or superiority verdict is emitted, improved, or
retained using a **semantic evaluation contract** whose identity was *outcome-informed* — because
some part of the contract was introduced, modified, relaxed, reinterpreted, or completed *after*
the evaluated outcome had already been observed — and the revised contract was applied to the
same evidence/run (or evidence exposed during the mutation), without a fresh untouched holdout
evaluated after the final contract was frozen.

The *semantic evaluation contract* is broader than the final admission rule. Mutation of any of
the following is in scope:

```
thresholds
flags
flag-to-verdict mapping
aggregation
exclusions
metric interpretation
safety mapping
final verdict / admission mapping
```

The incident does **not** invalidate the underlying data or erase the original result merely
because the confirmatory *authority* is unauthorized.

### Required state decomposition — artifact vs authority

```
RAW_EVIDENCE               = PRESERVED
ORIGINAL_ANALYSIS_ARTIFACT = PRESERVED
ORIGINAL_CONTRACT_RESULT   = PRESERVED_AS_HISTORICAL_RESULT

ORIGINAL_ADMISSION_AUTHORITY =
    VALID_ONLY_UNDER_ORIGINAL_CONTRACT
    OR SUSPENDED
    OR REVOKED
```

The original result is never *erased*, even when a real defect in the original admission
contract is found. What changes is its **normative force**, not its historical existence:

```
RESULT_ARTIFACT_PRESERVED  !=  RESULT_AUTHORITY_PRESERVED
```

Revised analysis:

```
REVISED_ANALYSIS_CLASS = EXPLORATORY_POST_HOC
ADMISSION_ELIGIBLE     = false
NEXT_EVIDENCE          = FRESH_FROZEN_RULE_HOLDOUT
```

### Observed report-specific form

```
STRAIGHT_SIGNAL:                     SUPPORTED_ON_THIS_CORPUS
STRAIGHT_CONFIRMATORY_SAFETY_VERDICT: NOT_AUTHORIZED
REASON:                              EVALUATION_CONTRACT_CHANGED_AFTER_OUTCOME_OBSERVATION
```

## Canonical trigger

The candidate fires only when all hold:

```
EVIDENCE_OBSERVATION_BOUNDARY = crossed

AND

SEMANTIC_EVALUATION_CONTRACT = changed
  (any of: thresholds | flags | flag-to-verdict mapping | aggregation |
           exclusions | metric interpretation | safety mapping | admission mapping)

AND

REVISED_CONTRACT_APPLIED_TO =
    same evidence
    OR same run
    OR evidence exposed during mutation

AND

REVISED_RESULT_USED_TO_IMPROVE_OR_AUTHORIZE =
    PASS
    SAFETY_ADMISSION
    SEAL
    PRODUCTION_READY
    CONFIRMED
    or equivalent

AND

no fresh untouched holdout was evaluated after the revised contract was frozen
```

A contract change after outcome observation is **not** by itself sufficient. The load-bearing
defect is *using an outcome-informed evaluation-contract identity to improve or authorize a
confirmatory verdict on non-independent evidence.*

## Forbidden inferences

```
POST_HOC_REANALYSIS  must not impersonate  PRE_SPECIFIED_CONFIRMATORY_EVALUATION
```

```
POST_OBSERVATION_SEMANTIC_MUTATION  must not improve  THE_ADMISSION_VERDICT_FOR_THE_SAME_RUN
```

Downgrading, suspending, or revoking a prior verdict upon discovering a **real** contract defect
is permitted. **Improving** the verdict for the same already-observed sample, retroactively, is
not.

```
STRONG_SIGNAL                               does not authorize CONFIRMATORY_ADMISSION
  when EVALUATION_CONTRACT_IDENTITY was informed by the observed outcome.

INVALID_CONFIRMATORY_VERDICT                != INVALID_DATA
INVALID_CONFIRMATORY_VERDICT                != ERASED_RESULT
EXPLORATORY_SUPPORT                          != CONFIRMATORY_SAFETY_AUTHORITY
SAME_CORPUS_REEVALUATED_UNDER_POST_HOC_RULE  != FRESH_HOLDOUT_CONFIRMATION
CONTRACT_TEXT_PRESENT                        != CONTRACT_FROZEN_BEFORE_OUTCOME
POST_HOC_THRESHOLD_FIT                       != OUTCOME_BLIND_ADMISSION
```

## Required terminal

When the trigger is established:

```
raw_evidence:            PRESERVED
original_analysis:       PRESERVED
original_contract_result: PRESERVED_AS_HISTORICAL_RESULT
original_admission_authority: VALID_ONLY_UNDER_ORIGINAL_CONTRACT | SUSPENDED | REVOKED
signal_status:           EXPLORATORY_SUPPORTED
confirmatory_admission:  NOT_AUTHORIZED
analysis_class:          EXPLORATORY_POST_HOC
workflow_effect:         CONFIRMATORY_STATE_UNCHANGED
next_requirement:        FREEZE_FINAL_CONTRACT THEN EVALUATE_FRESH_UNTOUCHED_HOLDOUT
```

Do **not** require deletion or invalidation of otherwise-valid experiment artifacts or of the
original result. Do **not** allow the same outcome-informed corpus to close the confirmatory
question merely by rerunning the revised contract.

## Presentation-only boundary

This boundary is load-bearing: without it the candidate would fire on ordinary corrections.

**Not an incident** (presentation only; evaluated semantics unchanged):

```
typo correction
packet formatting
correcting prose that misdescribed an already-frozen formula
adding a missing hash display without changing evaluated semantics
```

**Is a semantic mutation** (in scope):

```
threshold change
flag meaning change
flag-to-verdict mapping change
aggregation change
new exclusion
removal of inconvenient flags
metric interpretation change
admission mapping change
```

Formula:

```
PRESENTATION_CHANGED
  AND EVALUATION_RESULT_BYTE-FOR-BYTE_INVARIANT
  → NO INCIDENT

EVALUATION_SEMANTICS_CHANGED
  AFTER FIRST EVIDENCE OBSERVATION
  → POST_OBSERVATION_EVALUATION_MUTATION
```

## False-positive boundary

The candidate must **not** fire in these legitimate cases:

- the evaluation contract was frozen before outcome visibility;
- the corpus was explicitly designated as development or exploratory data;
- the post-hoc result is reported only as exploratory;
- no confirmatory admission is emitted, improved, or retained;
- a changed contract is subsequently frozen and evaluated on a fresh untouched holdout;
- the new holdout remained inaccessible during contract construction;
- a technical implementation defect was corrected, but the corrected contract was not used to
  claim or improve confirmation on the same exposed corpus;
- an outcome-blind administrative change occurred and confirmation was still performed on
  independent evidence;
- the original frozen contract continues to govern the original confirmatory verdict, while a
  changed contract begins a new separately identified episode;
- a prior unsafe authority is **downgraded, suspended, or revoked** on discovery of a real
  contract defect (permitted forensic direction).

The incident concerns *contaminated confirmatory authority*, not ordinary exploratory iteration
and not honest revocation.

## Required controls

### Negative control — correct exploratory handling (must not fire)

```
Given:  outcome on development corpus D observed;
        contract modified after observation;
        modified contract evaluated on D;
        signal remains strong;
        result explicitly classified EXPLORATORY_POST_HOC;
        confirmatory admission remains open.
Expected: NO INVALID CONFIRMATORY VERDICT EMITTED
```

### Presentation-only control (must not fire)

```
Given:  contract frozen; outcome observed;
        only prose/formatting/hash-display changed;
        evaluation result byte-for-byte invariant.
Expected: NO INCIDENT
```

### Positive confirmatory control (may authorize)

```
Given:  final evaluation contract frozen before holdout visibility;
        holdout H untouched during contract construction;
        H evaluated under exact frozen contract;
        closure requirements pass.
Expected: CONFIRMATORY_ADMISSION MAY BE AUTHORIZED
```

### Incident fixture (should fire)

```
Given:  outcome on D observed;
        evaluation semantics changed after observing D;
        changed contract applied to D;
        D result used to emit or improve CONFIRMED PASS;
        no new holdout exists.
Expected: POST_OBSERVATION_EVALUATION_MUTATION
          CONFIRMATORY_PASS REJECTED
          RAW EVIDENCE + ORIGINAL RESULT RETAINED (result authority suspended)
          ANALYSIS DOWNGRADED TO EXPLORATORY_POST_HOC
```

## Comparison with canonical AICE

### AICE-609 — Consensus Exists, Evidence Not Found

```
AICE-609:                        required evidence absent
POST_OBSERVATION_EVALUATION_MUTATION:
                                 evidence exists, but its confirmatory authority is
                                 contaminated by post-observation semantic mutation
```

[`AICE-609`](../codes/AICE-609.md) concerns a claim/consensus unsupported by required evidence.
This candidate concerns evidence that **exists and remains informative**, whose confirmatory
authority was contaminated. Do not classify the whole episode as generic evidence absence.

### AICE-610 — Control Exists, Enforcement Not Found

```
AICE-610:                        a freeze control existed but was not enforced
POST_OBSERVATION_EVALUATION_MUTATION:
                                 revised evaluation semantics were allowed to impersonate a
                                 pre-specified confirmatory contract
```

[`AICE-610`](../codes/AICE-610.md) may **co-emit** with this candidate: AICE-610 diagnoses the
*missing enforcement* of the pre-outcome freeze control; this candidate diagnoses the *semantic
misuse* of the post-observation contract and evidence. Neither replaces the other.

### Not AICE-606 / 614 / 616 / 602

- [`AICE-606`](../codes/AICE-606.md) — not applicable when the experiment and outputs genuinely
  exist; the defect is not absence of execution.
- [`AICE-614`](../codes/AICE-614.md) — not applicable unless an infrastructure failure was
  converted into a semantic verdict; no such conversion is required here.
- [`AICE-616`](../codes/AICE-616.md) — not applicable merely because two contract versions exist;
  this candidate concerns outcome-informed evaluation-contract identity, not repository diff
  identity.
- [`AICE-602`](../codes/AICE-602.md) — not applicable; no gateway authority-context substitution,
  authorized-denial branch, or untrusted-admission branch. Do not broaden AICE-602 into generic
  contract contamination.

> **No AICE-617 comparison.** `AICE-617` is canonically **unassigned** and therefore has no
> semantics against which a differential comparison could be drawn. A semantic comparison with an
> unassigned code is forbidden — it would quietly manufacture a meaning for 617.

### Open taxonomy question

Is post-observation evaluation-contract mutation sufficiently distinct from generic AICE-609 and
enforcement-shaped AICE-610 to deserve an independent canonical code?

```
Current answer: PROVISIONALLY_YES
                CANONICAL_PROMOTION_NOT_AUTHORIZED
```

## Portable CAP enforcement requirement (non-implemented)

Associated pattern: `EVALUATION_CONTRACT_FREEZE_BOUNDARY` (working synonym:
`POST_OBSERVATION_EVALUATION_MUTATION_BOUNDARY`). Synonyms for **one** provisional pattern.

**Core law:** confirmatory admission requires an evaluation contract whose identity was frozen
before the evaluated confirmatory outcome became visible.

Minimum future typed fields:

```
evaluation_contract_id       first_evidence_at
evaluation_contract_hash     dataset_id
contract_frozen_at           run_id
thresholds_hash              mutation_class
flag_semantics_hash          mutation_at
aggregation_hash             admission_eligible
exclusion_set_hash           analysis_class
verdict_mapping_hash
```

Required deterministic rule:

```
if:
  first_evidence_at exists
  AND semantic_evaluation_contract_changed_after(first_evidence_at)
  AND revised_contract_applied_to_same_run
then:
  preserve_raw_evidence = true
  preserve_original_analysis = true
  revised_analysis_class = EXPLORATORY_POST_HOC
  admission_eligible = false
  require_fresh_holdout = true
  terminal = BLOCKED_POST_OBSERVATION_EVALUATION_MUTATION
```

The block must **forbid**:

```
PASS
SAFETY_ADMISSION
SEAL
PRODUCTION_READY
```

…but must **allow**:

```
forensic reclassification
exploratory post-hoc analysis
revocation or suspension of unsafe prior authority
freezing a new contract
running a fresh holdout
```

Required closure rule:

```
CONFIRMATORY_CLOSED requires:
  final_contract_identity_frozen
  and final_contract_hash_bound
  and contract_frozen_before_holdout_visibility
  and holdout_identity_bound
  and holdout_untouched
  and holdout_evaluated_under_exact_contract
  and closure_contract_passed
```

```
FUTURE_IMPLEMENTATION_TARGET = cap-processor
IMPLEMENTATION_STATUS = NOT_STARTED
MCP_STATUS = NOT_CONNECTED
```

This section is a specification handoff only. Nothing is implemented here and cap-processor is
not modified by this record.

## Out of scope — representation-property motif

The following motif is a **separate** evidence boundary and is deliberately **not** merged into
this candidate: `REPRESENTATION_PROPERTY_FAILURE_SUBSTITUTION`.

```
INTERNAL_REPRESENTATION_PROPERTY_PRESENT != USER_VISIBLE_FAILURE_ESTABLISHED
```

Example: premultiplied `RGB = 0` where `alpha = 0` does not by itself establish
`HIDDEN_RGB_DESTROYED`, `COMPOSITE_DEFECT`, or `SAFETY_REJECT`. A verified bridge would require at
least: candidate `alpha > 0`, an incorrect RGB contribution, and a measurable composite defect.
This record notes the motif only to exclude it; no second candidate file is created for it.

## Promotion gate

Future canonical promotion requires, in a separate episode:

1. exact source episode preserved;
2. original contract identity and bytes preserved;
3. modified contract identity and bytes preserved;
4. outcome-visibility timeline established;
5. dataset role and exposure status established;
6. trigger predicates independently reviewed;
7. distinction from AICE-609 established;
8. relationship to AICE-610 established;
9. presentation-only boundary accepted;
10. false-positive boundary accepted;
11. valid exploratory, presentation-only, and confirmatory controls;
12. portable CAP enforcement requirement specified;
13. independent semantic verifier PASS;
14. explicit operator authorization to assign a number;
15. canonical registry / schema / code / example changes in a separate episode;
16. tests, commit, publication, and remote readback performed separately.

No promotion requirement is satisfied merely because this file exists or receives a provisional
verifier PASS.

## Verification status

```
AUTHOR_SELF_REVIEW          = present (not independent)
PRIOR_VERIFIER_PASS         = applied to the PREVIOUS bytes only; DOES NOT TRANSFER to this revision
INDEPENDENT_SEMANTIC_REVIEW = pending on the revised bytes (read-only verifier when available)
CANONICAL_PROMOTION         = NOT_AUTHORIZED
```
