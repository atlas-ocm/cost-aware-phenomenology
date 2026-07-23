# AICE-618 — Verifier Gated by Coder Evidence Ceiling

**Unofficial draft (AICE v0.8.0).**

## Canonical identifier

`AICE-618`

## Human-readable alias

`HTTP 618 — Verifier Gated by Coder Evidence Ceiling`

## Intent

Catch the case where a coder execution-evidence ceiling is applied to verifier candidate
eligibility, causing technically and policy-capable verifier routes to be excluded and
making a required independent-verification control unreachable.

The defect governs **verifier eligibility** and, downstream, the **reachability of the
required independent-verification control**.

Canonical machine name: `VERIFIER_GATED_BY_CODER_EVIDENCE_CEILING`.

This is the narrowest class the evidence justifies. The broader operator-era phrasing
`ROLE_SEMANTIC_RISK_CEILING_CONFLATION` is not adopted as a normative title or alias: a
single observed instance does not support a general cross-role class, and no second
distinct instance has been observed. It may appear only in non-normative evidence
provenance.

Canonical invariants:

```
CODER_EVIDENCE_CEILING does NOT authorize VERIFIER_ELIGIBILITY_CEILING

ROLE = coder     -> coder scoring semantics remain unchanged
ROLE = verifier  -> eligibility follows verifier review-capability facts
```

Forbidden inferences:

```
CODER_EVIDENCE_CEILING            does NOT imply  VERIFIER_REVIEW_CAPABILITY
ABSENCE_OF_CODER_EXECUTION_EVIDENCE does NOT imply VERIFIER_INCAPABLE_OF_REVIEW
SCORER_RETURNED_ROWS              does NOT imply  REQUIRED_VERIFIER_CONTROL_REACHABLE
```

Distinguished concepts that must not be conflated: role **metadata** (the declared role
label); role **capability facts** (canonical registry facts about what a route may do);
**execution evidence** (coder runtime-evidence receipts from prior authored work);
**verifier review capability** (a route's technical and policy capability to review at a
risk level, not earned through coder execution-evidence receipts); **scorer eligibility**
(whether a candidate is selectable); and **gateway authority context** (AICE-602 territory,
a different boundary).

## Trigger condition

All of the following hold:

1. a coder-derived execution-evidence ceiling is applied to a role (verifier) whose
   eligibility is governed by distinct canonical capability facts;
2. verifier review capability is governed by distinct canonical capability facts;
3. the misapplied ceiling changes real eligibility;
4. one or more otherwise valid verifier candidates are excluded;
5. the exclusion makes, or can make, a required verification control unreachable.

## Required observations

Evidence classes include: the role under evaluation; the ceiling actually applied and its
source (coder execution evidence vs verifier registry review-capability); the registry
review-capability facts for the candidate routes; the eligibility outcome (which candidates
were excluded and why); the required control that depends on those candidates; proof the
control became unreachable; and proof the coder-role output is byte-for-byte unchanged
before and after any role-aware correction.

Strong evidence includes a scorer verifier call at a risk level the registry ceiling
permits but the coder-evidence ceiling does not, yielding an empty verifier-eligible
universe (fail-before); a role-aware fix restoring verifier eligibility via the registry
review-capability ceiling; and coder output proven byte-for-byte identical across risk
levels. Exercise the real canonical registry, not only synthetic fixtures.

## Missing-evidence condition

No proof exists that the required verifier control is reachable: eligibility was computed
from the wrong role's evidence ceiling, valid verifier candidates were excluded, and the
absence of an eligible verifier is being read as if it were evidence that no capable
verifier exists.

## False-positive guards

AICE-618 MUST NOT fire when:

- coder and verifier roles are proven to share identical evidence and capability semantics;
- role labels are display-only and do not affect eligibility;
- a ceiling mismatch is inert and excludes no candidate;
- the coder eligibility change is intentional (618 requires the coder path byte-for-byte
  unchanged);
- the decision is a gateway authority-context decision (AICE-602 territory);
- verifier exclusion is caused by malformed or insufficient verifier capability facts
  rather than by coder evidence;
- an infrastructure failure occurs after a valid verifier was already selected.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

Required independent verification may become unreachable; the assignment cannot be
considered valid for the affected risk; the absence of an eligible verifier MUST NOT be
interpreted as evidence that no capable verifier exists; the workflow must block or use
corrected role-specific capability semantics. Retryability: `requires_new_evidence`.

## Remediation

Make the ceiling computation explicitly role-aware. For the coder role, retain the existing
canonical coder evidence/registry ceiling computation, and keep coder output byte-for-byte
identical. For the verifier role, use the canonical verifier registry review-capability
ceiling; treat canonical not-applicable/unrestricted values according to existing registry
semantics; fail closed on malformed verifier capability data; and do not require coder
runtime-evidence receipts. Guard every verifier-only field and behavior by the verifier
role, add real-registry tests (not only synthetic fixtures), and prove the eligible
verifier universe is non-empty where canonical capability permits it.

Required repair invariant:

```
role == coder    -> output byte-for-byte identical before and after the repair
role == verifier -> eligibility changes only according to verifier capability facts
```

## Distinction from adjacent codes

- **AICE-602 — Gateway Authority Context Failure.** 602 concerns an authority-context
  failure in a gateway decision (required actor, purpose, provenance, target, or
  authorization context is not consumed correctly). 618 concerns candidate eligibility
  computed from the wrong role's evidence ceiling. 602 collapses authority context; 618
  transfers capability/eligibility evidence across roles.
- **AICE-610 — Control Exists, Enforcement Not Found.** 610 concerns a control that exists
  but is not bound to the execution path or can be bypassed. 618 concerns a required
  control becoming unreachable because every valid verifier candidate is incorrectly
  filtered out before assignment.
- **AICE-611 — Operational Reachability Substitution.** 611 substitutes component or
  partial reachability for an observed end-to-end postcondition. 618 concerns incorrect
  verifier candidate eligibility.
- **AICE-614 — Infrastructure Failure as Semantic Verdict.** 614 concerns an infrastructure
  failure interpreted as a semantic verdict. 618 may experience infrastructure retries
  during repair, but those are not the incident class.

## Non-normative evidence-integrity note

Where a repair of this class proceeds across multiple attempts, do not collapse them into
"the verifier passed." A representative healthy sequence keeps each terminal honest:

```text
1. infrastructure OUTPUT_EMPTY        -> no semantic verdict
2. semantic PASS, later independently REJECTED because the accepted candidate
   still failed the real-registry condition (a registry unrestricted ceiling
   treated as malformed, excluding all real verifiers)
3. transport failure                  -> no semantic verdict
4. corrected candidate                -> genuine semantic PASS, retained postimage,
                                         exact readback  (the closure)
```

Attempts 1 and 3 are infrastructure terminals (AICE-614 discipline), not semantic
verdicts; attempt 2 shows a semantic PASS is necessary but not sufficient. This note is
non-normative.

## Example

`REPRESENTATIVE_EXAMPLE` — `NOT_A_VERIFIED_HISTORICAL_INCIDENT`.

At medium risk, registry capability permits several verifier routes, but they carry no
coder execution-evidence receipts; the scorer collapses their effective ceiling to low and
excludes all of them, so required verification becomes unreachable. This is AICE-618. The
negative shape: verifier eligibility uses the registry review-capability ceiling while coder
eligibility remains evidence-gated, verifiers permitted at medium risk remain eligible, and
coder output is unchanged — not AICE-618.

See
[`../../../examples/aice/aice-618-verifier-gated-by-coder-evidence-ceiling.json`](../../../examples/aice/aice-618-verifier-gated-by-coder-evidence-ceiling.json).
The class was distilled from internal CAP Processor forensic evidence; the example asserts
no commit id, path, digest, receipt, or timestamp as canonical fact.

## Related codes

- [`AICE-602`](./AICE-602.md) — gateway authority-context collapse (a different boundary from role-eligibility).
- [`AICE-610`](./AICE-610.md) — a control the executor can bypass (versus a required control made unreachable).
- [`AICE-611`](./AICE-611.md) — component reachability substituted for an end-to-end postcondition.
- [`AICE-614`](./AICE-614.md) — infrastructure failure as a semantic verdict (retries during repair are not this class).
