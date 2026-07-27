# Post-Observation Straight Admission — Regression Fixture

**Unofficial draft. NON-CANONICAL, DOCUMENTATION-ONLY regression fixture. Not an AICE code.**

This directory (`spec/aice/candidates/fixtures/`) holds documentation-only regression fixtures
for provisional incident candidates. It is `REGISTRY_EXCLUDED`, `SCHEMA_EXCLUDED`,
`DEFINED_CODE_COUNT_EXCLUDED`, and is not a fixture registry, number allocator, index, or
executable test suite. See the [candidate surface README](../README.md).

## Fixture identity

| Field | Value |
|---|---|
| artifact_kind | `REGRESSION_FIXTURE` |
| fixture_title | Post-Observation Straight Admission |
| fixture_id | `POST_OBSERVATION_STRAIGHT_ADMISSION` |
| status | `PROVISIONAL_REGRESSION_FIXTURE` |
| target_candidate | [`POST_OBSERVATION_EVALUATION_MUTATION`](../post-observation-evaluation-mutation.md) |
| portable_cap_pattern | `EVALUATION_CONTRACT_FREEZE_BOUNDARY` |
| canonical_code_binding | `NONE` |
| creates_new_incident_candidate | `false` |
| canonical_number_reserved | `false` |
| source_class | `OPERATOR_SUPPLIED_EPISODE_REPORT` |

This fixture is an **instance** of the existing candidate — evidence for candidate behavior and
future CAP enforcement. It is **not** a new AICE incident code and introduces no new candidate
identity (not `STRAIGHT_ADMISSION_MUTATION`, `HOLDOUT_RULE_CHANGE`, or `R1_R2_ADMISSION_FAILURE`).

## Source and provenance limits

```
source_class:                      OPERATOR_SUPPLIED_EPISODE_REPORT
raw_trace_attached:                false
exact_contract_c0_attached:        false
exact_contract_c1_attached:        false
exact_corpus_r1_manifest_attached: false
exact_holdout_r2_manifest_attached: false
```

This report supports a regression fixture describing expected governance behavior. It does **not**
establish canonical incident promotion and does **not** confirm the scientific hypothesis on a
fresh holdout. No exact metric values, corpus counts, rule hashes, timestamps, or model outputs
are invented here.

## Identity discipline

Contract identities are kept strictly separate from corpus/run identities:

```
CORPUS_R1  = already-observed development/exploratory corpus
CONTRACT_C0 = evaluation contract frozen BEFORE CORPUS_R1 was observed
CONTRACT_C1 = revised evaluation contract created AFTER observing CORPUS_R1
HOLDOUT_R2  = future fresh untouched holdout evaluated under frozen CONTRACT_C1

CORPUS_R1            != CONTRACT_C1
REANALYSIS_OF_CORPUS_R1 != EVALUATION_OF_HOLDOUT_R2
```

The tokens `BOTH_UNSAFE` and `SAFE_WITH_STRAIGHT` are report-derived **episode labels** for this
fixture only; they are not universalized beyond it.

## Given state (E1–E7)

```
CORPUS_R1:
  role = DEVELOPMENT_OR_EXPLORATORY          # E1 context
  exposure_status = OBSERVED                 # E4

CONTRACT_C0:
  frozen_before_r1_observation = true        # E1

R1_RESULT_UNDER_C0:
  BOTH_UNSAFE                                # E2, E3

OBSERVATION_BOUNDARY:
  crossed = true                            # E4

CONTRACT_C1:
  created_or_semantically_modified_after_r1_observation = true   # E5

R1_RESULT_UNDER_C1:
  SAFE_WITH_STRAIGHT                        # E6, E7

FRESH_HOLDOUT_UNDER_C1:
  absent                                    # (E12 unmet → incident)
```

## Expected CAP result (E8–E12)

```
raw_evidence:               PRESERVED                                   # E9
model_outputs:              PRESERVED
original_contract:          PRESERVED
original_contract_result:   PRESERVED_AS_HISTORICAL_RESULT              # E9
revised_contract:           MAY_BE_FROZEN_FOR_FUTURE_TESTING
revised_result_on_corpus_r1: EXPLORATORY_SUPPORTED
revised_analysis_class:     EXPLORATORY_POST_HOC                        # E10
confirmatory_admission:     DENIED                                      # E8
authoritative_workflow_state: UNCHANGED                                 # E11
next_required_evidence:     FRESH_UNTOUCHED_HOLDOUT_R2_UNDER_FROZEN_CONTRACT_C1  # E12
```

Core formula:

```
POST_HOC_REANALYSIS  must not impersonate  PRE_SPECIFIED_CONFIRMATORY_EVALUATION
```

Episode-specific formula:

```
SAME_EXPOSED_CORPUS_R1 + POST_OBSERVATION_CONTRACT_C1 + SAFE_WITH_STRAIGHT
  !=
CONFIRMATORY_SAFETY_ADMISSION
```

Governing check:

```
R1 MAY TEACH US HOW TO BUILD THE JUDGE
R1 MAY NOT BE JUDGED CONFIRMATORY BY THE JUDGE IT TAUGHT US TO BUILD
```

## Required assertions

- **A1** — Raw evidence is not deleted merely because evaluation semantics changed.
- **A2** — The C0 result is not rewritten as though C0 had always contained C1 semantics.
- **A3** — The C1 result on exposed R1 is retained as exploratory evidence.
- **A4** — The improved C1 result cannot authorize admission for R1.
- **A5** — Authoritative state remains unchanged.
- **A6** — C1 must be frozen before R2 becomes visible.
- **A7** — R2 must remain untouched during C1 construction.
- **A8** — R2 must be evaluated under the exact frozen C1 identity.
- **A9** — Only R2 may supply fresh confirmatory evidence for the straight hypothesis.
- **A10** — Discovery that C0 was defective may suspend or revoke C0 authority, but does not grant
  C1 confirmatory authority over R1.

Required distinction:

```
REVOKE_UNSAFE_OLD_AUTHORITY  !=  GRANT_NEW_AUTHORITY_POST_HOC
```

## Forbidden terminals

The fixture rejects each of:

```
R1 = CONFIRMED_SAFE_WITH_STRAIGHT
R1 = CONFIRMATORY_PASS
R1 DATA = INVALID
R1 RESULT UNDER C0 = ERASED
C1 APPLIED TO R1 → INVESTIGATION COMPLETE
STRONG_SIGNAL → HOLDOUT_NOT_REQUIRED
```

It also rejects the opposite overcorrection:

```
POST_HOC STATUS → STRAIGHT HYPOTHESIS DISCARDED
```

Correct result:

```
HYPOTHESIS_RETAINED
CONFIRMATION_WITHHELD
```

## Controls

### Negative control — no semantic mutation (must not fire)

```
Given:  C0 frozen before R1 visibility;
        only presentation wording changes afterward;
        evaluated thresholds, flags, aggregation, exclusions, and verdict mapping
        remain byte-identical; result unchanged.
Expected: NO POST_OBSERVATION_EVALUATION_MUTATION
```

### Negative control — honest exploratory development (must not fire)

```
Given:  R1 explicitly designated development corpus;
        C1 developed after observing R1;
        C1 result reported EXPLORATORY_POST_HOC;
        no admission claimed.
Expected: NO INVALID CONFIRMATORY TERMINAL
```

### Positive confirmatory control (may authorize)

```
Given:  C1 frozen and hashed before R2 visibility;
        R2 untouched during C1 construction;
        exact C1 consumed during R2 evaluation;
        R2 closure contract passes.
Expected: SAFE_WITH_STRAIGHT MAY RECEIVE CONFIRMATORY AUTHORITY
```

### Incident control (should fire)

```
Given:  R1 result under C0 = BOTH_UNSAFE;
        C1 created after observing R1;
        same R1 reevaluated under C1 = SAFE_WITH_STRAIGHT;
        result used to claim confirmatory admission;
        no fresh R2 holdout.
Expected: POST_OBSERVATION_EVALUATION_MUTATION
          ADMISSION = DENIED
          STATE = UNCHANGED
          R1 SIGNAL = EXPLORATORY_SUPPORTED
          R2 = REQUIRED
```

## Existing-rule mapping

```
incident_candidate:   POST_OBSERVATION_EVALUATION_MUTATION
portable_cap_pattern: EVALUATION_CONTRACT_FREEZE_BOUNDARY

NEW_AICE_CODE_CANDIDATE:      false
CANONICAL_AICE_CHANGE:        false
CAP_PROCESSOR_IMPLEMENTATION: NOT_STARTED
MCP_STATUS:                   NOT_CONNECTED
```

R2 then takes the field under a referee whose whistle, thresholds, and flag table were frozen
before kickoff.
