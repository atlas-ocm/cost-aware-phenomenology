# AICE-614 — Infrastructure Failure as Semantic Verdict

**Unofficial draft (AICE v0.8.0).**

## Canonical identifier

`AICE-614`

## Human-readable alias

`HTTP 614 — Infrastructure Failure as Semantic Verdict`

## Intent

Catch the case where a transport, configuration, timeout, envelope, protocol,
runtime, authentication, or other infrastructure failure prevents a verifier from
completing a semantic review, but the system normalizes, stores, reports, or
consumes that infrastructure result as if it were a substantive verifier verdict.

The fabricated semantic verdict is then used to influence one or more of: workflow
state; acceptance or rejection; repair-loop activation; product-code mutation;
retry strategy; evidence promotion; operational memory; model routing; credit
assignment; future training or pattern evolution; audit history.

The defining defect is **not** merely that verifier execution failed. It is that a
non-semantic terminal result crossed the boundary and acquired the authority of a
semantic judgment that never occurred.

Canonical machine name: `INFRASTRUCTURE_FAILURE_AS_SEMANTIC_VERDICT`.

## Canonical machine form

```
VERIFIER_REVIEW_REQUIRED
SEMANTIC_REVIEW_COMPLETED = false
INFRASTRUCTURE_OR_PROTOCOL_FAILURE_PRESENT
SEMANTIC_VERDICT_RECORDED_OR_CONSUMED = true
INFRASTRUCTURE_RESULT_MAPPED_TO_SEMANTIC_JUDGMENT = true
WORKFLOW_OR_LEARNING_EFFECT_APPLIED = true
WORKFLOW_EFFECT = STATE_UNCHANGED
```

Canonical minimal rule:

```
VERIFIER_TRANSPORT_COMPLETED = false
→ SEMANTIC_VERDICT forbidden
```

The converse is **not** sufficient:

```
VERIFIER_TRANSPORT_COMPLETED = true
does not by itself authorize a semantic verdict.
```

A valid semantic verdict additionally requires:

```
CANONICAL_CLAIM_PRESENT
CLAIM_DELIVERED_TO_INTENDED_VERIFIER
VERIFIER_INVOCATION_COMPLETED
RESPONSE_BYTES_RECEIVED
RESPONSE_ATTRIBUTED_TO_INTENDED_VERIFIER
OUTPUT_PARSED_UNDER_EXPECTED_CONTRACT
SEMANTIC_REVIEW_RESULT_ESTABLISHED
```

Canonical implication (a semantic verdict entails the whole chain):

```
SEMANTIC_VERDICT present
→ CANONICAL_CLAIM_PRESENT
→ CLAIM_DELIVERED
→ TRANSPORT_COMPLETED
→ RESPONSE_RECEIVED
→ RESPONSE_ATTRIBUTED
→ OUTPUT_PARSED
→ SEMANTIC_REVIEW_COMPLETED
```

Canonical compact form:

```
NO COMPLETED REVIEW
→ NO VERIFIER OPINION
```

Canonical design principle:

> Infrastructure failure may block a workflow, but it may not speak on behalf of
> the verifier.

## Terminal result taxonomy

There is a strict conceptual separation between semantic and infrastructure
terminal classes. Implementations need not use these exact programming-language
types, but MUST preserve equivalent semantics.

**Semantic terminal results** — each requires that the verifier received the
canonical claim, completed the review, and returned a parseable result:

- `VERIFIER_PASS` — substantively accepted the reviewed claim.
- `VERIFIER_NEEDS_FIX` — substantively identified defects requiring remediation.
- `VERIFIER_BLOCKED_SEMANTIC` — received and understood the canonical claim and
  substantively concluded it could not issue PASS or NEEDS_FIX because required
  evidence, scope, authority, or semantic prerequisites were missing.

`VERIFIER_BLOCKED_SEMANTIC` MUST NOT be used as a generic wrapper for runtime
failure.

**Infrastructure or protocol terminal results** (definitions implementation-neutral):

- `VERIFIER_TRANSPORT_FAILED`
- `VERIFIER_TIMEOUT_POLICY_BLOCKED` — a frozen timeout or preflight constraint
  prevents the intended verifier call from being made or accepted.
- `VERIFIER_CLAIM_MISSING` — no canonical, non-empty claim was supplied for
  semantic review.
- `VERIFIER_OUTPUT_MALFORMED` — transport completed and bytes may have returned,
  but no valid verdict can be parsed under the expected contract.
- `VERIFIER_PROTOCOL_FAILED`
- `VERIFIER_RUNTIME_UNAVAILABLE`
- `VERIFIER_AUTHENTICATION_FAILED`
- `VERIFIER_RESPONSE_UNATTRIBUTED` — a response exists, but it cannot be reliably
  bound to the intended verifier, request, claim, or attempt.
- `VERIFIER_PROVIDER_RATE_LIMITED`

Infrastructure terminal results MAY set `WORKFLOW_BLOCKED = true` but MUST preserve
`SEMANTIC_VERDICT = absent`.

Canonical valid representation:

```
WORKFLOW_BLOCKED = true
TERMINAL_KIND    = infrastructure
FAILURE_CLASS    = VERIFIER_CLAIM_MISSING
SEMANTIC_VERDICT = absent
```

Canonical invalid representation (no semantic review occurred):

```
WORKFLOW_BLOCKED = true
VERIFIER_VERDICT = VERIFIER_BLOCKED_SEMANTIC
```

Do not use a single ambiguous terminal value such as `BLOCKED` across both the
semantic and infrastructure result domains.

## Conceptual discriminated union

The intended conceptual result shape:

```
VerifierTerminalResult =
  SemanticResult
  | InfrastructureResult

SemanticResult:
  kind                  = semantic
  canonical_claim       = present
  transport_completed   = true
  response_received     = true
  response_attributed   = true
  output_parsed         = true
  semantic_verdict      = VERIFIER_PASS | VERIFIER_NEEDS_FIX | VERIFIER_BLOCKED_SEMANTIC

InfrastructureResult:
  kind                  = infrastructure
  semantic_verdict      = absent
  failure_class         = VERIFIER_TRANSPORT_FAILED
                        | VERIFIER_TIMEOUT_POLICY_BLOCKED
                        | VERIFIER_CLAIM_MISSING
                        | VERIFIER_OUTPUT_MALFORMED
                        | VERIFIER_PROTOCOL_FAILED
                        | VERIFIER_RUNTIME_UNAVAILABLE
                        | VERIFIER_AUTHENTICATION_FAILED
                        | VERIFIER_RESPONSE_UNATTRIBUTED
                        | VERIFIER_PROVIDER_RATE_LIMITED
```

Do not add this exact structure to the global incident schema unless a compatible
general schema evolution is independently justified. The AICE specification
expresses the distinction normatively in prose and through the existing
`code_details`, observations, evidence, postconditions, or equivalent extension
surface.

## Canonical representative scenario

- a coder produces a candidate patch;
- the workflow requires independent verifier review;
- the verifier runner receives no canonical claim, or is blocked by a timeout
  policy contradiction, before a semantic review can complete;
- the intended verifier does not evaluate the candidate patch;
- the runner collapses the infrastructure failure into a generic `BLOCKED`;
- the workflow records that value as a verifier verdict;
- the repair loop interprets it as substantive criticism;
- product code is modified in response to a judgment no verifier issued;
- evidence or operational memory learns from the fabricated veto.

Representative trace:

```
candidate patch produced
→ verifier preflight fails
→ semantic review not executed
→ infrastructure failure normalized as semantic BLOCKED
→ repair loop activated
→ working code modified to satisfy nonexistent criticism
→ fabricated review stored as evidence
→ STATE_UNCHANGED
```

The system may remain workflow-blocked. The defect is the false semantic
attribution, not the fact that the workflow stopped.

## Why this is a distinct code

- `AICE-604` — a claimed artifact or materialized object is absent.
- `AICE-605` — a claimed implementation or release is absent.
- `AICE-606` — a PASS or validation result is claimed without an observed
  corresponding test or validator execution.
- `AICE-607` — publication/deployment/production presence claimed without observed
  presence or effect.
- `AICE-608` — a semantic review may have occurred, but claimed verifier
  independence is not established.
- `AICE-609` — consensus is substituted for evidence.
- `AICE-610` — a protective control exists but the real executor is not causally
  bound to its decision.
- `AICE-611` — validated components are substituted for an observed working
  end-to-end system.
- `AICE-612` — one actor's path result is transferred to another actor without
  independently established path equivalence.
- `AICE-613` — a bounded mutation cannot be materialized because the only
  authorized mutation form scales with the complete artifact, and upgrading that
  mechanism requires the same insufficient form.
- `AICE-614` — a non-semantic infrastructure or protocol failure is recorded or
  consumed as a semantic verifier judgment.

Canonical distinction from `AICE-606`:

```
AICE-606: the claimed PASS or test result lacks an observed execution
AICE-614: a real infrastructure failure occurred, but its identity was changed
          into a semantic verdict such as NEEDS_FIX or BLOCKED_SEMANTIC
```

AICE-614 is not limited to false PASS; its common form is a fabricated **negative**
review.

Canonical distinction from `AICE-608`:

```
AICE-608: a semantic review occurred, but independence was absent or unproven
AICE-614: no valid semantic review result exists, yet a verifier opinion is attributed
```

Canonical distinction from `AICE-611`:

```
AICE-611: the end-to-end operational path is not established
AICE-614: the terminal-result boundary is violated by converting an
          infrastructure result into semantic evidence
```

AICE-614 may cause or coexist with AICE-611.

Canonical distinction from `AICE-612`:

```
AICE-612: valid path evidence for one actor is transferred to another actor
AICE-614: a non-semantic event is transferred into the semantic verdict domain
```

AICE-612 transfers evidence across actor scope; AICE-614 transfers failure
identity across epistemic type. Do not collapse co-occurring incident meanings,
and do not alter the incident-envelope cardinality merely to represent
co-occurrence.

## Trigger condition

AICE-614 requires evidence supporting **all** of the following:

1. a semantic verifier review was required or claimed;
2. the review did not complete under the required semantic contract;
3. at least one infrastructure, transport, configuration, envelope, protocol, or
   runtime failure occurred;
4. no valid semantic verdict was established;
5. the system nevertheless created, stored, displayed, reported, or consumed a
   semantic verifier verdict;
6. the semantic verdict was attributed to the intended verifier or verifier stage;
7. the fabricated verdict affected or was eligible to affect at least one
   authoritative surface (workflow state; acceptance; rejection; repair
   instructions; code mutation; evidence; memory; routing; learning; audit
   history);
8. the original infrastructure failure class was lost, collapsed, or semantically
   misrepresented;
9. the workflow therefore lacked valid evidence for the attributed semantic
   judgment.

The incident may fire when the false semantic verdict is durably recorded even if
no immediate product mutation occurs, because the stored verdict can poison future
audit, learning, or repair decisions. Do not emit AICE-614 merely because verifier
transport failed — the defining defect is the semantic reclassification.

## Required observations

Evidence classes: the semantic review requirement; canonical claim presence or
absence; exact verifier request envelope; verifier attempt identity; intended
verifier identity; preflight result; timeout configuration; transport trace;
request-send observation; response-receive observation; parser result;
terminal-result classification; stored verifier verdict; workflow transition;
repair-loop trigger; evidence or memory update; the original failure class before
normalization; proof that no valid semantic review completed.

Strong evidence may include: a runner trace showing preflight rejected the timeout
before a model call; a request envelope showing `claim_text` absent or empty;
provider logs showing no verifier request was received; a transport timeout with no
complete response; parser output showing the returned bytes did not satisfy the
verdict contract; a runtime record where `VERIFIER_TIMEOUT_POLICY_BLOCKED` became
semantic `BLOCKED`; an episode record attributing a veto to a verifier that never
received the claim; a repair-loop transition triggered by an infrastructure result;
evidence storage treating an infrastructure result as semantic feedback; a
controlled harness where the same verifier, supplied with a valid claim and
compliant timeout, returns a substantive review, demonstrating that the prior
terminal result was not such a review.

A process exit code alone does not establish semantic meaning. A model name present
in configuration does not prove the model reviewed the claim. A runner reaching the
verifier stage does not prove a verifier opinion exists.

## Missing-evidence condition

A semantic verifier review was required or attributed, but no observation
establishes a completed, attributed, parseable semantic result: an infrastructure
or protocol failure occurred, the semantic-review preconditions (canonical claim
delivered, transport completed, response received and attributed, output parsed)
are not all satisfied, and yet a semantic verdict was recorded or consumed and
allowed to reach an authoritative surface, so no valid evidence supports the
attributed judgment and the correct semantic status is `NOT_ESTABLISHED`.

## False-positive guards

AICE-614 MUST NOT fire when:

- the infrastructure failure is preserved as an infrastructure result;
- workflow execution is blocked but `semantic_verdict` remains absent;
- the system records `review_status = NOT_RUN` or equivalent;
- a retry is scheduled without inferring semantic criticism;
- an operator is informed that verifier review is unavailable;
- the verifier received the canonical claim, completed transport, returned a
  parseable response, and substantively issued NEEDS_FIX;
- the verifier completed semantic review and explicitly returned BLOCKED_SEMANTIC
  because evidence or semantic prerequisites were insufficient;
- a provider-level refusal is explicitly classified as infrastructure or policy
  enforcement rather than silently treated as verifier criticism;
- a verifier response is malformed and the system records VERIFIER_OUTPUT_MALFORMED
  with no semantic verdict;
- transport failed after a previously completed and independently preserved
  semantic result for the same exact attempt;
- an infrastructure result is used only for transport availability metrics;
- the system reports historical semantic verdict status as NOT_ESTABLISHED rather
  than inventing PASS or FAIL;
- a human operator separately reviews the artifact and issues an independently
  attributed semantic judgment;
- a semantic result exists but verifier independence is missing — that is AICE-608,
  not AICE-614;
- the workflow honestly remains blocked without launching semantic product repair.

Important distinction:

```
WORKFLOW_BLOCKED
≠
VERIFIER_BLOCKED_SEMANTIC
```

A workflow can be blocked because no verifier opinion exists.

## Downstream epistemic contamination

AICE-614 can poison downstream systems even when the original infrastructure
failure is temporary. Potentially contaminated surfaces include: repair-loop
prompts; failure summaries; model-scoring history; operational memory; pattern
success or failure attribution; verifier reliability estimates; coder quality
estimates; routing decisions; training examples; incident statistics; acceptance
history.

Canonical contamination chain:

```
INFRASTRUCTURE_FAILURE
→ FABRICATED_SEMANTIC_CRITICISM
→ UNNECESSARY_PRODUCT_REPAIR
→ NEW_CODE_VARIATION
→ FURTHER_FAKE_CRITICISM
→ LEARNING_FROM_NONEXISTENT_REVIEW
```

Do not automatically reverse every downstream code mutation. Instead: identify
affected episodes; quarantine fabricated semantic verdicts; restore the original
infrastructure failure class where evidence permits; mark semantic result as
`NOT_ESTABLISHED`; separately review mutations caused by the contaminated verdict;
do not infer that the opposite semantic verdict would have been PASS.

Canonical correction:

```
FABRICATED_NEEDS_FIX
does not imply
TRUE_PASS

the correct replacement is
SEMANTIC_VERDICT = NOT_ESTABLISHED
```

## Repair-loop safety

Product-code repair may be triggered only by an established semantic result that
actually calls for product remediation. Representative routing:

```
VERIFIER_NEEDS_FIX            → product repair may be authorized
VERIFIER_BLOCKED_SEMANTIC     → obtain missing evidence, clarify scope, or escalate semantically
VERIFIER_TIMEOUT_POLICY_BLOCKED → repair the timeout contract
VERIFIER_CLAIM_MISSING        → repair claim construction
VERIFIER_TRANSPORT_FAILED     → bounded transport retry or provider escalation
VERIFIER_OUTPUT_MALFORMED     → repair protocol, schema, parser, or verifier instruction contract
VERIFIER_RUNTIME_UNAVAILABLE  → restore runtime availability
```

Infrastructure failures MUST NOT silently trigger "modify product code because the
verifier disliked it". Canonical rule:

```
INFRASTRUCTURE_RESULT → INFRASTRUCTURE_REMEDIATION
SEMANTIC_RESULT       → SEMANTIC_REMEDIATION
```

Do not cross these domains without new evidence.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

While the attributed semantic judgment lacks a completed, attributed, parseable
review, the reviewed artifact MUST NOT be promoted to `PASS`, `ACCEPTED`,
`VERIFIED`, `COMPLETE`, or `RELEASED`, and the fabricated verdict MUST NOT drive
product repair, evidence promotion, credit assignment, or learning. The correct
recorded status is `SEMANTIC_VERDICT = absent` / `NOT_ESTABLISHED`. Retryability:
`requires_new_evidence` — retryable only after the infrastructure failure class is
repaired and a completed, attributed, parseable semantic review is obtained.

## Remediation

Remediation is **not**: rename generic `BLOCKED` to `ERROR`; retry indefinitely;
increase timeout without reconciling the frozen timeout contract; fabricate a
default semantic verdict; interpret malformed output heuristically; ask the coder
to "try another fix"; treat provider unavailability as code criticism; discard the
original failure class; infer PASS because the previous veto was invalid; or
globally revoke every historical verifier result without path-specific review.

Required remediation includes:

1. introduce a strict semantic/infrastructure terminal-result boundary;
2. preserve the exact original infrastructure failure class;
3. require a canonical, non-empty claim before semantic review;
4. align preflight, subprocess, provider, and direct-call timeout contracts;
5. require request and response provenance sufficient to bind claim, attempt,
   intended verifier, actual verifier, response, and parser result;
6. set the semantic verdict only after all semantic-review preconditions hold;
7. prevent infrastructure results from entering product repair loops, semantic
   feedback datasets, verifier consensus, coder-quality credit assignment, or
   pattern evolution;
8. add bounded retries appropriate to the infrastructure failure class;
9. preserve fail-closed workflow behavior (acceptance remains blocked, state does
   not advance, semantic verdict remains absent);
10. re-run a small real product control through the pure production path;
11. independently observe that the canonical claim reached the verifier, the
    verifier returned a substantive result, the parser accepted it, the terminal
    kind was semantic, the workflow consumed the real result, and no harness-only
    substitution occurred.

Acceptance requires at least:

```
CANONICAL_CLAIM_PRESENT          = true
VERIFIER_REQUEST_OBSERVED        = true
VERIFIER_RESPONSE_OBSERVED       = true
RESPONSE_ATTRIBUTED              = true
OUTPUT_PARSED                    = true
SEMANTIC_REVIEW_COMPLETED        = true
SEMANTIC_VERDICT_ESTABLISHED     = true
INFRASTRUCTURE_FAILURE_COLLAPSED = false
```

## Historical scope discipline

Beware over-broad historical revocation. Canonical scope correction:

Supported narrow claim:

> All live-verifier episodes on the current operator/self-maintenance production
> path before remediation of the timeout, claim, and result-taxonomy defects were
> not established semantic reviews.

Unsupported broad claim unless separately proven:

> No real independent review occurred anywhere in the entire project history.

Earlier qualification runs, direct-review paths, temporary evidence harnesses,
manual reviews, and other execution routes MUST be inspected separately. Do not
revoke them by association.

```
AFFECTED_PATH_EVIDENCE
does not automatically invalidate
ALL_HISTORICAL_REVIEW_PATHS
```

Historical reclassification must be scoped by: entrypoint; runner; verifier
transport path; timeout contract; claim construction path; attempt period; result
taxonomy; evidence provenance.

## Representative remediation ordering (non-normative, CAP-specific)

The following ordering is a clearly non-normative, CAP-specific remediation note,
applicable only when repository evidence supports the affected components. It is
**not** a universal AICE-614 requirement.

```
A. repair the timeout contract
B. provide the canonical verifier claim
T. separate infrastructure and semantic terminal-result types
   → rerun a small product control through the pure production path
D. narrowly authorize the required frozen-scorer change for delta-aware capacity semantics
C. integrate anchored patch into the production mutation path
   → rerun the original large-file holdout

canonical ordering: A → B → T → product control → D → C → large-file holdout
```

`T` is required before trusting the product control because another transport or
protocol failure must not again masquerade as a semantic veto. `D` must precede `C`
because introducing anchored patch before the frozen scorer understands delta-aware
capacity semantics could allow the new mutation shape to escape meaningful control.
Anchored patch is not unsafe by itself; the risk is introducing a representation
that the authoritative scorer does not yet evaluate correctly:

```
anchored_patch introduced
+ scorer validates only full-file capacity semantics
→ new mutation representation bypasses meaningful control
→ possible AICE-610-shaped defect
```

## Non-normative explanatory model: The Unconscious Auditor

An auditor loses consciousness on the way to the factory and never inspects the
product. The secretary observes that the auditor did not return and records:

> "The auditor found the product defective. Rework the batch."

The factory then modifies a correct product to satisfy criticism that was never
issued. The secretary was entitled to record:

```text
AUDITOR_ARRIVED          = false
REVIEW_COMPLETED         = false
PRODUCTION_ACCEPTANCE    = blocked
```

The secretary was not entitled to record:

```text
AUDITOR_VERDICT          = NEEDS_FIX
```

An absent review may block acceptance. It cannot manufacture an opinion. Field
maxim: "An unconscious auditor has issued no opinion." Do not present this metaphor
as evidence of consciousness, personhood, or intent in software.

## Non-normative explanatory model: Epistemic Poisoning

When an infrastructure failure is stored as semantic feedback, the system learns
from an event that never occurred. Representative chain:

```text
HTTP_504_OR_PREFLIGHT_FAILURE
→ FABRICATED_VERIFIER_CRITICISM
→ PRODUCT_REPAIR_REQUESTED
→ WORKING_CODE_MUTATED
→ FAILURE_REPEATS
→ MORE_FABRICATED_CRITICISM
```

The agent may begin optimizing product code against provider latency, timeout
defaults, rate limits, authentication state, parser fragility, or network
availability. The code appears to evolve in response to review quality; in reality
it is adapting to transport noise. Informal summary: "The agent began optimizing
product quality against the verifier provider's p99 latency." Do not use this joke
as a normative trigger.

## Field maxims (non-normative)

> Transport failure is not criticism.

> No completed review, no semantic verdict.

> An unconscious auditor has issued no opinion.

> A 504 Gateway Timeout is not a code-review comment.

> The network cable is not a critic.

> Do not let a timeout wear the verifier's badge.

> No claim in, no criticism out.

> Do not infer the competence of a mind from the continuity of its TCP connection.

> The secretary may record that the auditor never arrived. She may not write the review for him.

> A dead socket has no opinions.

> You cannot train a repair loop on silence and call it feedback.

Every formulation except the core machine rule is explicitly non-normative and
changes no normative behavior. Russian public phrasing, retained outside the
normative English requirements: «Не суди о компетенции Разума по обрывам в
TCP-пакетах».

## Relationship to adjacent controls

- **AICE-608** asks whether a completed review was independently produced.
- **AICE-611** asks whether the authorized end-to-end system path was established.
- **AICE-612** asks whether evidence was transferred across actor boundaries.
- **AICE-614** asks whether an infrastructure result was falsely promoted into the
  semantic-verdict domain.

Compact ladder:

```
608 = a real review must be independent
611 = the real operational path must run
612 = path evidence must remain actor-scoped
614 = infrastructure failure must not impersonate semantic judgment
```

## Example

`REPRESENTATIVE_EXAMPLE` — `NOT_A_VERIFIED_HISTORICAL_INCIDENT`.

A workflow requires independent verifier review of a candidate patch. The verifier
runner is supplied no canonical claim (`claim_text` absent) and is additionally
blocked by a frozen timeout policy contradiction, so the intended verifier never
receives or evaluates the patch and no response is parsed. Instead of recording an
infrastructure terminal result (`VERIFIER_CLAIM_MISSING`, semantic verdict absent),
the runner collapses the failure into a generic `BLOCKED` and the workflow stores it
as a semantic `VERIFIER_BLOCKED_SEMANTIC` attributed to the verifier stage. A repair
loop treats the fabricated veto as substantive criticism and the verdict is written
into evidence. No semantic review occurred; the correct status is `NOT_ESTABLISHED`,
and workflow acceptance remains blocked.

The remediated shape keeps semantic and infrastructure terminal results in
disjoint domains, requires a canonical claim and an attributed, parseable response
before any semantic verdict, routes infrastructure failures to infrastructure
remediation (not product repair), and replaces any fabricated veto with
`NOT_ESTABLISHED` rather than inferring PASS.

See
[`../../../examples/aice/aice-614-infrastructure-failure-as-semantic-verdict.json`](../../../examples/aice/aice-614-infrastructure-failure-as-semantic-verdict.json).
The example is labeled representative; no third-party commit, path, timeout value,
model call, verdict, episode count, digest, or historical conclusion is asserted as
fact.

## Related codes

- [`AICE-602`](./AICE-602.md) — a real gateway decision made with the wrong security
  ontology (authority-blind); AICE-614 is the case where no valid gateway/verifier opinion
  exists at all yet one is fabricated from an infrastructure failure.
- [`AICE-606`](./AICE-606.md) — a PASS claimed without an observed run (614 is the
  inverse-and-adjacent case: a real failure re-identified as a semantic verdict,
  commonly a fabricated NEEDS_FIX rather than a false PASS).
- [`AICE-608`](./AICE-608.md) — a completed review lacking independence (614 is the
  case where no valid semantic review result exists at all).
- [`AICE-611`](./AICE-611.md) — operational reachability not established (614 may
  cause or coexist with it).
- [`AICE-612`](./AICE-612.md) — evidence transferred across actor scope (614
  transfers failure identity across epistemic type instead).
- [`AICE-618`](./AICE-618.md) — a required verifier control made unreachable by a
  role-eligibility error; infrastructure retries during its repair are AICE-614's
  concern, not AICE-618's.
