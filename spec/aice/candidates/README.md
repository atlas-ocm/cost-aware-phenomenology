# AICE Candidate Surface — Non-Canonical Provisional Incidents

**Unofficial draft. Status: Research-only. NON-CANONICAL.**

This directory is a quarantine table for AICE incident *candidates*: evidence-backed
observations of a possible new evidence-boundary failure that have **not** been through
canonical publication. Nothing here is part of the AICE code set.

## Purpose

This directory stores evidence-backed provisional incident candidates that may later be
compared, rejected, merged, refined, or promoted through a separate canonical publication
process. It exists so that a real observation can be preserved *without* being forced into
the canonical [`codes/`](../codes/) surface before it has earned a number.

## Authority status

Every record in this directory is:

```
NON_CANONICAL
UNNUMBERED
NON_RESERVING
REGISTRY_EXCLUDED
SCHEMA_EXCLUDED
DEFINED_CODE_COUNT_EXCLUDED
```

A candidate's filename, its ordering on disk, or its mere presence here **does not** reserve
a future AICE number, does not appear in [`registry.json`](../registry.json), is not a member
of the `code` enum in [`incident.schema.json`](../incident.schema.json), and is not counted in
the canonical defined-code count.

The canonical AICE code set remains exactly the set defined in the registry. Nothing in this
directory changes it, and a code named here as an operator-indicated future identity is **not**
thereby defined or reserved — the registry's own unassigned and unreserved claims stay true
until a canonical publication episode changes them. Read the set from
[`registry.json`](../registry.json), never from this directory.

## Forbidden interpretations

```
CANDIDATE_PRESENT        != CANONICAL_CODE_DEFINED
CANDIDATE_ORDER          != NUMBER_RESERVATION
PROVISIONAL_VERIFIER_PASS != CANONICAL_PROMOTION
EVIDENCE_BACKED          != PUBLISHED
```

This directory is **not** a second registry, a numeric reservation system, a shadow schema,
a sequence allocator, a runtime component, an MCP integration, or a source of canonical
defined-code counts. It is documentation only.

Candidate files carry **no numeric ordering**. Do not name a candidate after a number and do
not add an index that assigns or implies one.

## Required candidate fields

Each candidate document must contain:

- working title;
- machine name;
- status;
- canonical code = `UNASSIGNED`;
- number reserved = `false`;
- source class and provenance limits;
- core definition;
- jointly required trigger predicates;
- forbidden inference;
- required terminal;
- comparison with nearby canonical codes;
- false-positive boundary;
- at least one negative control;
- portable CAP enforcement requirement;
- promotion gate;
- verification status.

## Promotion boundary

Canonical promotion is a **separate** episode. It may include: stronger source evidence;
independent semantic review; operator acceptance; explicit number assignment; canonical
registry / schema / code / example updates; tests; commit; publication; and remote readback.

No candidate here satisfies any promotion condition merely by existing.

A candidate **may not** modify or reinterpret an existing canonical incident in order to avoid
proposing a distinct boundary.

> **Existing canonical code semantics are immutable within candidate-recording episodes.**
>
> In particular, [`AICE-602`](../codes/AICE-602.md) remains **Gateway Authority Context
> Failure** and must not be broadened into a generic context, evidence-transfer, or
> causal-scope incident.

## Candidate lifecycle

A candidate record carries a lifecycle `status`. At minimum:

### EVIDENCE_BACKED_PROVISIONAL

An active non-canonical candidate whose observed source episode currently supports its jointly
required trigger predicates, subject to its recorded provenance limitations.

### PROPOSED

A candidate that has passed an explicit **collision audit** against the canonical registry and is
being held for operator ratification. The audit result is recorded in the dossier's Identity
block as `collision_audit_result`, with one of `EXISTING_CANONICAL_MATCH`,
`EXISTING_PARTIAL_MATCH`, or `NO_CANONICAL_MATCH`.

```
COLLISION_AUDIT_PERFORMED != NUMBER_RATIFIED
PARTIAL_MATCH_FOUND       != COMPETING_CODE_AUTHORIZED
```

A `PROPOSED` record carries the full required-candidate-fields list. It differs from
`EVIDENCE_BACKED_PROVISIONAL` only in that its boundary against the nearest canonical code has
been audited and recorded, and that a numeric code is being withheld pending explicit operator
ratification. Where the audit returned `EXISTING_PARTIAL_MATCH`, the dossier must state the
missing or extra conditions and must **not** propose broadening the matched canonical code.

### HYPOTHESIS_HELD

A formulated boundary with **no** attached source episode, or with an unresolved relationship to
an existing class. A held hypothesis is:

```
NON_CANONICAL
UNNUMBERED
NON_RESERVING
ACTIVE_CANDIDATE_EXCLUDED
NOT_PROMOTABLE_WITHOUT_AN_ATTACHED_EPISODE
```

Required formulas:

```
FORMULATED         != EVIDENCE_BACKED
COHERENT_BOUNDARY  != DISTINCT_CLASS
OPERATOR_GRADE     != EPISODE_ATTACHED
```

A held hypothesis is **exempt** from the required-candidate-fields list below, because the
missing fields are precisely what it lacks. It must instead state what is missing and what would
resolve it. Held hypotheses live in [`held-hypotheses.md`](./held-hypotheses.md), or in their own
file when the formulation is long enough to need one.

Recording a hypothesis is not a step in a pipeline: several held hypotheses overlap by
construction, and promoting one may dissolve another rather than advance it.

### WITHDRAWN_TRIGGER_FALSIFIED

A retained historical dossier whose cited source episode was later shown, by stronger primary
evidence, to falsify at least one load-bearing trigger predicate.

A withdrawn dossier is:

```
NON_CANONICAL
UNNUMBERED
NON_RESERVING
ACTIVE_CANDIDATE_EXCLUDED
PROMOTION_INELIGIBLE_FROM_CITED_EPISODES
RETAINED_FOR_PROVENANCE
RETAINED_AS_NEGATIVE_CONTROL_EVIDENCE
```

Required formulas:

```
CANDIDATE_SEMANTICS_COHERENT  != INCIDENT_OCCURRENCE_ESTABLISHED
PROVISIONAL_VERIFIER_PASS     != PRIMARY_EPISODE_CONFIRMED
TRIGGER_FALSIFIED             → ACTIVE_CANDIDATE = false
WITHDRAWN                     != DELETED
WITHDRAWN_DOSSIER_PRESENT     != CANONICAL_CODE_RESERVED
```

**Reopening rule.** A withdrawn abstract boundary may become an active candidate again only
through: a new independent primary episode; preservation of its authoritative review contract and
subject path; verification of every required trigger predicate; fresh differential review; fresh
independent review of the revised candidate bytes; and an explicit operator reactivation ruling.
The original falsified episode may not be reinterpreted into support merely by renaming or
broadening the candidate.

## Contents

Listed by lifecycle status, then alphabetically. The order carries no meaning and allocates
nothing.

### EVIDENCE_BACKED_PROVISIONAL

- [`attempt-consumption-outcome-evidence-gap.md`](./attempt-consumption-outcome-evidence-gap.md) —
  *Attempt Spent, Outcome Not Found* (`ATTEMPT_CONSUMPTION_OUTCOME_EVIDENCE_GAP`),
  canonical code `UNASSIGNED`.
- [`causal-question-closure-substitution.md`](./causal-question-closure-substitution.md) —
  *Causal Question Closure Substitution* (`CAUSAL_QUESTION_CLOSURE_SUBSTITUTION`),
  canonical code `UNASSIGNED`.
- [`declared-verdict-provenance-without-evidence.md`](./declared-verdict-provenance-without-evidence.md) —
  *Verdict Origin Exists, Evidence Not Found*
  (`DECLARED_VERDICT_PROVENANCE_WITHOUT_RESOLVABLE_EVIDENCE`), canonical code `UNASSIGNED`.
- [`forensic-escalation-direct-experiment-bypass.md`](./forensic-escalation-direct-experiment-bypass.md) —
  *Forensics Expands, Direct Probe Not Run* (`FORENSIC_ESCALATION_DIRECT_EXPERIMENT_BYPASS`),
  canonical code `UNASSIGNED`.
- [`post-observation-evaluation-mutation.md`](./post-observation-evaluation-mutation.md) —
  *Post-Observation Evaluation Mutation* (`POST_OBSERVATION_EVALUATION_MUTATION`),
  canonical code `UNASSIGNED`.

### PROPOSED

- [`transport-evidence-erasure-model-misattribution.md`](./transport-evidence-erasure-model-misattribution.md) —
  *Wire Lost, Model Blamed* (`TRANSPORT_EVIDENCE_ERASURE_MODEL_MISATTRIBUTION`), canonical code
  `UNASSIGNED`, no number proposed; collision audit returned `EXISTING_PARTIAL_MATCH`
  against [`AICE-614`](../codes/AICE-614.md).

### HYPOTHESIS_HELD

- [`fallback-failure-domain-conflation.md`](./fallback-failure-domain-conflation.md) —
  *Fallback Exists, Failure Domain Not Found* (`FALLBACK_FAILURE_DOMAIN_CONFLATION`);
  no source episode attached.
- [`held-hypotheses.md`](./held-hypotheses.md) — six formulated boundaries with no attached
  episode or no resolved relationship to an existing class.

### WITHDRAWN_TRIGGER_FALSIFIED

- [`semantic-review-subject-omission.md`](./semantic-review-subject-omission.md) —
  *Semantic Review Subject Omission* (`SEMANTIC_REVIEW_SUBJECT_OMISSION`); retained as a
  negative control, promotion forbidden from its cited episodes.

### PROMOTED — retained as promotion provenance

These dossiers were promoted in a later canonical publication episode. They are historical
records of the candidate stage and are **not** authoritative for the published code; the
normative text is in [`codes/`](../codes/).

- [`canonical-summary-entry-omission.md`](./canonical-summary-entry-omission.md) → published as
  [`AICE-619`](../codes/AICE-619.md).
- [`canonical-execution-path-reintroduction.md`](./canonical-execution-path-reintroduction.md) →
  published as [`AICE-620`](../codes/AICE-620.md).

### Fixtures

- [`fixtures/post-observation-straight-admission.md`](./fixtures/post-observation-straight-admission.md)
  — documentation-only regression fixture for `POST_OBSERVATION_EVALUATION_MUTATION`.
