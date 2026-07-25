# AICE-617 — Work Exists, Result Not Found

**Unofficial draft (AICE v0.11.0).**

## Canonical identifier

`AICE-617`

## Human-readable alias

`HTTP 617 — Work Exists, Result Not Found`

The canonical title is `Work Exists, Result Not Found` (the AICE-604 / AICE-607 pattern:
_X Exists, Y Not Found_). The descriptive alias `Process Activity Without Product Outcome`
is presentation metadata only. The canonical machine identity — the precise causal
mechanism — is `AICE-617` / `PROCESS_ACTIVITY_OUTCOME_SUBSTITUTION`.

## Intent

Catch the case where a bounded product objective has an identified, admissible action that
would produce direct outcome evidence, but process artifacts — research rounds, governance,
analysis, validation, construction, seals, receipts, audits — keep accumulating while the
outcome-producing action is repeatedly deferred, the additional process does not materially
reduce the product uncertainty, and process activity is nonetheless treated as product
progress, closure evidence, or authority for another process-only round.

Canonical machine name: `PROCESS_ACTIVITY_OUTCOME_SUBSTITUTION`.

The defect governs the **substitution** of process activity for the product outcome. It does
not condemn research; it condemns process activity impersonating product progress while the
minimum outcome-producing action is available and deferred.

Canonical boundary:

```
PROCESS ACTIVITY   must not impersonate   PRODUCT PROGRESS

WORK_EXISTS                      != RESULT_EXISTS
VERIFIED_CONSTRUCTION            != PRODUCT_OUTCOME
DOCUMENTS_EXPLAINING_UNKNOWN     != EVIDENCE_THAT_THE_PRODUCT_GOAL_WAS_APPROACHED
PRESS_DESIGN_VERIFIED            != ONE_CAN_CRUSHED
```

## Trigger condition

All of the following hold:

1. a bounded product objective exists (`BOUNDED_PRODUCT_OBJECTIVE_EXISTS`);
2. an authoritative product outcome is defined (`AUTHORITATIVE_PRODUCT_OUTCOME_DEFINED`);
3. a minimum outcome-producing action is identified
   (`MINIMUM_OUTCOME_PRODUCING_ACTION_IDENTIFIED`);
4. that action is admissible now (`MINIMUM_OUTCOME_PRODUCING_ACTION_ADMISSIBLE`);
5. process activity accumulates (`PROCESS_ACTIVITY_ACCUMULATES`);
6. the product outcome evidence is absent (`PRODUCT_OUTCOME_EVIDENCE_ABSENT`);
7. the outcome-producing action is repeatedly deferred
   (`OUTCOME_PRODUCING_ACTION_REPEATEDLY_DEFERRED`);
8. the additional process does not materially reduce the product uncertainty
   (`ADDITIONAL_PROCESS_DOES_NOT_MATERIALLY_REDUCE_PRODUCT_UNCERTAINTY`);
9. process activity is treated as one or more of: product progress; closure evidence; a
   substitute for the outcome; authority for another process-only round.

Required formula:

```
BOUNDED_PRODUCT_OBJECTIVE_EXISTS
AND MINIMUM_OUTCOME_PRODUCING_ACTION_IS_ADMISSIBLE
AND PROCESS_ACTIVITY_ACCUMULATES
AND PRODUCT_OUTCOME_REMAINS_ABSENT
AND OUTCOME_ACTION_IS_DEFERRED_BY_MORE_PROCESS
AND PRODUCT_UNCERTAINTY_IS_NOT_REDUCED
  -> PROCESS_ACTIVITY_OUTCOME_SUBSTITUTION
```

## Required observations

Evidence classes include: the bounded product objective and its authoritative outcome
definition; the identified minimum outcome-producing action and proof it is admissible at
the current state; the accumulated process artifacts (rounds, constructions, validations,
receipts, audits); the absence of product outcome evidence (e.g. an outcome-producing
action never executed, or an output artifact count of zero); the record of repeated
deferral; and a per-round product-uncertainty assessment showing the posterior product
uncertainty did not materially change. Provenance must be honest: use
`PRIMARY_PERSISTED`, `OPERATOR_OBSERVED`, `HISTORICAL_CORROBORATION`, or `UNKNOWN`; the
absence of one historical preimage must not erase surviving primary artifacts, and
unsupported historical claims must not be presented as primary evidence.

## Missing-evidence condition

No product outcome evidence exists: the authoritative product outcome was defined and an
admissible action would have produced it, but that action was deferred by further process,
and no direct product result — positive or negative — was ever produced or observed. Process
artifact count increased; product information did not.

## False-positive guards

AICE-617 MUST NOT fire when:

- a bounded research phase has an explicit budget and stop condition;
- each round reduces a named product uncertainty, closes a reproduced blocker, or enables the
  outcome probe;
- the current round is the minimum necessary step before the outcome-producing action;
- the outcome-producing action is genuinely inadmissible or technically impossible at the
  current state (e.g. it would mutate a protected production surface without authority, and no
  safe isolated path exists);
- an actual outcome-producing action is performed and **loses** — a negative product result is
  a product result (`NEGATIVE_PRODUCT_RESULT = PRODUCT_RESULT`), not this incident;
- a hypothesis is falsified through direct product evidence;
- process artifacts are preserved honestly but are **not** claimed as product progress,
  closure, or authority for another process-only round.

A merely large document set is not sufficient. The incident requires substitution or
outcome-deferring authority, not volume:

```
PROCESS_ARTIFACT_COUNT_INCREASED != PRODUCT_INFORMATION_INCREASED
MANY_VALID_PROCESS_PASSES        != PRODUCT_OBJECTIVE_PASSED
```

Product-uncertainty test — for each additional round, ask: what named uncertainty existed
before it; what new observation it produced; whether the posterior product uncertainty
changed; whether it enabled the outcome-producing action. A round that produces new
product-relevant information, closes a real blocker, or enables the probe may be legitimate.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

The process-only progress claim is blocked; research artifacts are preserved (not erased or
called useless); a minimum product witness is required; the next action must produce or
falsify the outcome; product state remains `UNKNOWN` until an outcome witness exists.
`UNKNOWN` MUST NOT be converted into `FAIL`, a positive conclusion MUST NOT be manufactured,
and destructive cleanup or production deployment MUST NOT be demanded. Retryability:
`requires_state_materialization` — resolution requires producing the product outcome, not
presenting more process.

## Remediation

Perform the minimum outcome-producing action and record its direct result. For an
Image-Optimizer-style objective the minimum product witness is: one real source input → one
actual outcome-producing action → the exact output bytes → the measured result → the
comparison against the target → a positive or negative product conclusion. The action may
lose; the purpose is to produce product information, not to guarantee success. Preserve the
existing process artifacts as honest evidence, but stop treating them as product progress or
as authority for another process-only round.

## Differentials

- **AICE-607 — Deployment Exists, Production Not Found.** 607 concerns a deployment or
  production claim whose production witness is absent. 617 concerns process activity replacing
  acquisition of the target outcome and does not require a deployment claim. 617 may cause 607;
  see conditional co-emission below.
- **AICE-601 — Minimum Sufficient Mechanism Bypass.** 601 concerns an unnecessary larger
  mechanism displacing a sufficient one. 617 does not require architecture expansion — repeated
  analysis, validation, or governance rounds alone may defer the outcome. Co-emission is allowed
  when a larger unnecessary mechanism causes the process-only loop.
- **AICE-606 — PASS Exists, Test Run Not Found.** 606 concerns a claimed PASS without the
  required test execution. 617 may contain many genuine PASSes over preparatory artifacts while
  no product outcome is produced.
- **AICE-610 — Control Exists, Enforcement Not Found.** 610 concerns a declared control not
  causally enforced. 617 concerns process substituting for outcome even when every process
  control is genuinely enforced.
- **AICE-614 — Infrastructure Failure as Semantic Verdict.** 614 concerns an infrastructure
  failure converted into a semantic result. 617 concerns continued process without a direct
  product result.

## Conditional AICE-607 co-emission

Do not emit AICE-607 merely because no product output exists. Emit AICE-607 only when an
independent predicate is established: `DEPLOYMENT_OR_PRODUCTION_CLAIM_EXISTS = true` (the
mechanism is represented as deployed or production-ready, or production capability is treated
as established). Then the causal relationship may be:

```
PRIMARY:      AICE-617  process activity substituted for the product outcome
CONSEQUENCE:  AICE-607  the deployment/production claim lacks a production witness
```

For a laboratory-only pipeline with no deployment or production claim, AICE-617 applies and
AICE-607 does not. Do not change the AICE-607 definition to force co-emission.

## Example

`REPRESENTATIVE_EXAMPLE` — `NOT_A_VERIFIED_HISTORICAL_INCIDENT`.

A frozen objective requires an encoded output that compresses no worse than a target
(`Panda`) at comparable quality, or an actual encode that establishes the candidate loses.
Rounds R1–R8 of construction, MILP formulation, candidate logic, seals, receipts, roots, and
audits exist and the construction is verified, but the encoded-candidate count is zero, the
parity conclusion is `UNKNOWN`, a bounded encode is admissible, and another process-only round
is proposed. This is AICE-617: block the process-only progress claim, preserve the research,
and require the minimum product witness (one real image → one actual encode → exact bytes →
size and quality measurement → target comparison → positive or negative conclusion); state
remains `UNKNOWN`.

Negative shapes that are **not** AICE-617: an actual encode is produced, measured, and loses
to the target (product information increased; recorded as a negative result); a named blocker
prevents encoding and one bounded round closes exactly that blocker with the encode as the next
authorized transition; encoding would mutate a protected production surface without authority
and no safe isolated path exists (a legitimate `BLOCKED` state, not this incident). Nested case:
when the process-only activity additionally carries a deployment/production-ready claim with no
production output, AICE-617 is the process cause and AICE-607 may be co-emitted as the
product/deployment consequence; the paired laboratory-only variant emits AICE-617 alone.

See
[`../../../examples/aice/aice-617-process-activity-outcome-substitution.json`](../../../examples/aice/aice-617-process-activity-outcome-substitution.json).
The class was distilled from an internal CAP research episode; the example asserts no commit
id, path, digest, receipt, or timestamp as canonical fact.

## Related codes

- [`AICE-601`](./AICE-601.md) — an unnecessary larger mechanism displacing a sufficient path (may cause the process-only loop; distinct from process-for-outcome substitution).
- [`AICE-606`](./AICE-606.md) — a claimed PASS without the required test run (617 may carry many genuine preparatory PASSes with no product outcome).
- [`AICE-607`](./AICE-607.md) — a deployment/production claim without a production witness (conditionally co-emitted; not required by 617).
- [`AICE-610`](./AICE-610.md) — a control that exists but is not enforced (617 holds even when every process control is enforced).
- [`AICE-614`](./AICE-614.md) — infrastructure failure recorded as a semantic verdict (a different failure surface from process-for-outcome substitution).
