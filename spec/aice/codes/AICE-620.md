# AICE-620 — Architectural Groundhog Loop

**Unofficial draft (AICE v0.12.0).**

## Canonical identifier

`AICE-620`

## Human-readable alias

`HTTP 620 — Architectural Groundhog Loop`

The canonical title is `Architectural Groundhog Loop`. The descriptive alias
`Canonical Execution Path Reintroduction` is presentation metadata only, as are the informal
renderings _Displaced Execution Authority Returns_ and _Canonical Path Exists, Competing
Authority Returns_. The canonical machine identity — the precise causal mechanism — is
`AICE-620` / `CANONICAL_EXECUTION_PATH_REINTRODUCTION`.

## Intent

Catch the architectural loop in which a deliberate consolidation is silently undone. An
execution path that once held independent control authority is explicitly subordinated,
displaced, or reduced to a thin adapter when another path becomes the canonical execution
spine. The displaced path is never retired. Later — usually under a genuine but *different*
new requirement — it regains independent authority, and the competing topology the earlier
decision was intended to remove is back.

Canonical machine name: `CANONICAL_EXECUTION_PATH_REINTRODUCTION`.

The defect is **authority return without a necessity witness**. It is not the existence of a
second entrypoint, not asynchrony, and not code that merely remains callable.

Canonical boundary:

```
DISPLACED PATH   must not   SILENTLY REACQUIRE AUTHORITY

CANONICAL_IN_PROSE                 != CANONICAL_IN_EXECUTABLE_TOPOLOGY
DEMOTION_IN_PROSE                  != DEMOTION_IN_EXECUTABLE_TOPOLOGY
THIN_ADAPTER                       != COMPETING_CONTROL_PATH
NEW_TRANSPORT_REQUIREMENT          != NEW_LIFECYCLE_AUTHORITY_REQUIREMENT
NEW_REQUIREMENT_EXISTS             != UNIQUE_NECESSITY_FOR_DUPLICATED_AUTHORITY
PATH_STILL_CALLABLE                != PATH_HAS_RETURNED_AS_AUTHORITY
DORMANT_EXECUTABLE_PATH            != REINTRODUCED_EXECUTION_AUTHORITY
RETIRED_AUTHORITY_STILL_EXECUTABLE != RETIRED_ARCHITECTURE
```

## Trigger condition

All of the following hold:

1. a canonical execution spine was established
   (`CANONICAL_EXECUTION_SPINE_ESTABLISHED`);
2. a competing path was demoted or displaced from it
   (`COMPETING_PATH_PREVIOUSLY_DEMOTED_OR_DISPLACED`);
3. the spine was later reaffirmed (`CANONICAL_SPINE_LATER_REAFFIRMED`);
4. the displaced path remained executable, not merely present in source
   (`DISPLACED_PATH_REMAINED_EXECUTABLE`);
5. it regained independent authority over at least one of lifecycle, identity, state, routing,
   retry, admission, mutation, cancellation, lease, or terminal classification
   (`DISPLACED_PATH_REGAINED_INDEPENDENT_AUTHORITY`);
6. no new premise uniquely requires the duplicated authority
   (`NO_NEW_PREMISE_UNIQUELY_REQUIRES_DUPLICATED_AUTHORITY`);
7. the reintroduced authority was actually exercised
   (`AUTHORITY_REINTRODUCTION_ACTUALLY_OCCURRED`);
8. a material workflow effect exists (`MATERIAL_WORKFLOW_EFFECT_ESTABLISHED`).

Required formula:

```
CANONICAL_SPINE_ESTABLISHED
AND COMPETING_AUTHORITY_DISPLACED
AND CANONICAL_SPINE_REAFFIRMED
AND DISPLACED_PATH_REMAINS_EXECUTABLE
AND DISPLACED_PATH_REGAINS_INDEPENDENT_AUTHORITY
AND NO_NEW_PREMISE_UNIQUELY_REQUIRES_DUPLICATED_AUTHORITY
AND MATERIAL_WORKFLOW_EFFECT_EXISTS
  -> CANONICAL_EXECUTION_PATH_REINTRODUCTION
```

Two forms are admitted. **Form A**: a subordinate path acquires authority it never had.
**Form B**: a former authority is displaced and later returns. Form B additionally requires
that the returning path did **not** originate subordinate; asserting Form B for a path that
was always a subordinate adapter is a misclassification, not a stronger reading.

## Required observations

Evidence must come from executable bytes, not from architecture prose. Evidence classes
include: the commit or module in which the ladder, decision function, or lifecycle ownership
moved, cited from the receiving module's own bytes rather than from a commit message; the
re-export, binding, or registration that names the spine as owner; proof the displaced path
was never deleted, disabled, or expiry-sealed, and is still advertised and dispatchable; the
specific returned authority, identified by the line that intercepts a spine decision or
supplies the spine a bound it should have received; the stated premise of the commit that
returned the authority, compared against the premise that would be required to justify it; and
persisted runtime records showing the returned path executed after the return.

Provenance must be honest. Use `PRIMARY_PERSISTED` for committed bytes and persisted runtime
artifacts, `HISTORICAL_CORROBORATION` for commit-message text (which may date or label but
never establish), `TEST_EXECUTION` for suite-produced artifacts (which demonstrate mechanism,
never production usage), and `NOT_FOUND_IN_BOUNDED_EVIDENCE_UNIVERSE` where the search was
bounded.

```
CLAIM_IN_COMMIT_MESSAGE                != PERSISTED_INDEPENDENTLY_READABLE_EVIDENCE
NOT_FOUND_IN_BOUNDED_EVIDENCE_UNIVERSE != CONTRARY_EVIDENCE_CANNOT_EXIST
```

## Missing-evidence condition

No unique-necessity witness exists for placing the returned authority outside the canonical
spine. A new requirement may be real and documented; what is absent is any design note, ADR,
review record, or governance surface establishing that satisfying it *required* a second
control authority rather than an adapter converging on the first. Absent that witness, the
return is an unexplained topology change, and the burden does not shift onto the reader to
disprove a necessity nobody recorded.

## False-positive guards

AICE-620 MUST NOT fire when:

- the displaced path was genuinely retired — deleted, decommissioned, or asserted-dead by a
  standing test — because predicate 4 then fails;
- the returning component owns only transport concerns: a job or queue identity, queue
  position, cancellation request, worker lease, or detached execution, while semantic
  lifecycle, routing, retry policy, and terminal classification stay with the spine
  (predicate 5 fails);
- an entrypoint translates input and immediately converges on the spine, producing one
  workflow identity and one terminal (predicates 5 and 8 fail) — multiple front doors are not
  the incident;
- the path regains authority in code but is never exercised (predicate 7 fails) — that is a
  risk surface to be recorded, not an incident;
- a new requirement genuinely made the single-spine design unworkable and the record shows the
  second authority was the minimum way to satisfy it (predicate 6 fails) — the correct terminal
  is a blocked, unresolved-premise state, not a classification.

Several front doors are legitimate **when they converge**: one job identity, one lifecycle, one
state model, one routing decision, one retry ledger, one terminal result. Entry multiplicity is
not the incident. Non-convergence is.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

Acceptance of the competing topology is blocked. The reintroduced path is not deleted as a
remediation step and no runtime is decommissioned by fiat — an incident is not an authority to
break a running system. Retryability: `requires_new_evidence` — resolution requires either a
unique-necessity witness for the duplicated authority, or convergence.

## Remediation

Choose one and make it observable in executable bytes rather than in prose. Either **converge**
— return the disputed decision to the spine, so the adapter receives its bound and its
transition rather than supplying them — or **record the necessity**, declaring the second
authority canonical for its named scope, binding it into the governance contract, and
reconciling the two identity namespaces so lineage joins in at least one direction. What is not
a remediation: restating in documentation that the spine is authoritative, since prose
reaffirmation is exactly what predicate 3 already recorded and predicate 5 already survived.

## Differentials

- **AICE-610 — Control Exists, Enforcement Not Found.** The nearest neighbour. See the
  resolution below; it is normative.
- **AICE-601 — Minimum Sufficient Mechanism Bypass.** 601 concerns an unnecessary larger
  mechanism displacing a sufficient one, judged at the moment of introduction. 620 concerns the
  authority loop over time — established, displaced, survived, returned. A single oversized
  introduction with no prior displacement is 601, not 620. Co-emission is allowed.
- **AICE-603 — Governance-Induced Service Unavailability.** Governance friction may explain why
  an alternate route was attractive, but that is a claim about motive. 603 concerns the
  withholding event; 620 concerns the later architecture of the route.
- **AICE-605 — Release Exists, Implementation Not Found.** Nothing in 620 is missing an
  implementation or a release; both paths are implemented and both run.
- **AICE-612 — Actor Path Substitution.** 612 transfers a conclusion about one actor's path to
  another. 620 makes no transfer: both paths are observed directly.

## AICE-610 resolution (normative)

AICE-610 and AICE-620 are **orthogonal**, not nested. Neither implies the other, and the
overlap is resolved by asking which independent predicate is established.

```
AICE-610 requires   A DECLARED CONTROL, SUCCESSFULLY CONSTRUCTED, PERSISTED, PARSED,
                    OR VALIDATED, WHOSE RESULT IS NOT CONSUMED
AICE-620 requires   A DISPLACEMENT, A SURVIVAL, AND A RETURN OF AUTHORITY
```

The control condition above is AICE-610's own canonical disjunction (AICE-610, Trigger
condition, point 3), quoted in full. Reaching **any one** successful lifecycle stage —
construction, persistence, parse, or validation — makes an artifact 610-eligible; a
validation step is one sufficient stage, not a gate. A persisted policy object that parses
successfully and is bypassed by a returning authority path satisfies AICE-610 and co-emits
with AICE-620; requiring it to also *validate* before co-emitting would silently narrow
AICE-610's canonical condition.

- **610 without 620.** A repository that never displaced anything can still declare a control
  and fail to bind it. No displacement, no return, no 620.
- **620 without 610.** Where the spine's authority was asserted by an architectural decision, a
  module docstring, and a re-export binding, there is no control artifact that reaches any
  successful lifecycle stage — constructed, persisted, parsed, or validated — and produces an
  enforcement result to be bypassed. A declaration is not a control: what disqualifies it is
  not a missing validation step but that no stage of it yields a consumable enforcement
  result at all. In that shape 610 does
  **not** co-emit, and this is the common case: the reaffirmation instrument in the source
  episode was a re-export and an observe-only lifecycle handle, neither of which enforces.
- **Both.** Where a parity, admission, or approval control genuinely exists in any
  successfully processed form — constructed, persisted, parsed, or validated — and is
  routed around by the returning path, both fire: 610 for the unenforced control, 620 for the
  authority return. They describe different objects — 610 the control, 620 the topology — so
  co-emission is neither redundant nor a merge condition.

Emit AICE-610 alongside AICE-620 only when `ENFORCEMENT_CONTROL_DECLARED = true` and its result
is demonstrably unconsumed on the returning path. Do not infer a control from a declaration:

```
ARCHITECTURAL_DECLARATION != ENFORCEMENT_CONTROL
RE_EXPORT_BINDING         != ENFORCEMENT_CONTROL
OBSERVE_ONLY_HANDLE       != ENFORCEMENT_CONTROL
```

## Example

`REPRESENTATIVE_EXAMPLE` — derived from an observed multi-repository episode outside this
repository.

A loop controller is born authoritative, owning a bounded retry budget, escalation gates, and
terminal classification. A later commit removes that entire cross-attempt ladder from it in one
change and installs it in a new transition module, whose own bytes state that the controller
"becomes a thin driver that executes one bounded attempt and OBEYS the returned transition". A
workflow module re-exports the transition and driver functions under a comment naming itself
the declared owner, and the standing client contract names that plane the control plane while
mentioning the controller nowhere. The controller is never deleted and remains an advertised,
dispatchable tool. Months later, under a genuine requirement to move the loop out of a long
synchronous request, a detached job table arrives — legitimately transport. Then a second
commit, whose stated premise is reassignment rather than asynchrony, adds two lines: one
intercepts the spine's own retry and escalate transition kinds and routes them to a second
decision function with its own policy version, and one substitutes a constant owned by the
controller for the caller-supplied loop bound, feeding the substituted value back into the
spine's budget rule. A persisted runtime record then shows the spine escalating and the loop
retrying anyway. Two retry authorities coexist, the effective bound is one neither surface
advertises, and two persisted identity namespaces share no join. All eight predicates hold.

Negative shapes that are **not** AICE-620: the same repository's scorer migration, where a
shadow became authoritative, the legacy selector was retired, the legacy runtime was deleted,
and a standing test was added asserting the decommissioning holds (predicate 4 fails — the
project demonstrably knows how to retire competing authority); the detached job table taken
alone, owning identity, queue position, cancellation, and lease while every semantic decision
stays with the spine (predicate 5 fails); an entrypoint that translates input and calls the
spine, yielding one workflow state and one terminal (predicates 5 and 8 fail).

See
[`../../../examples/aice/aice-620-canonical-execution-path-reintroduction.json`](../../../examples/aice/aice-620-canonical-execution-path-reintroduction.json).
The example asserts no commit id, path, digest, receipt, or timestamp as canonical fact.

## Related codes

- [`AICE-601`](./AICE-601.md) — an unnecessary larger mechanism displacing a sufficient path (judged at introduction; 620 judges the authority loop over time).
- [`AICE-603`](./AICE-603.md) — a capability withheld by an unnecessary governance dependency (620 concerns the route's later architecture, not the withholding event).
- [`AICE-610`](./AICE-610.md) — a control that exists but is not enforced (orthogonal; see the normative resolution above).
- [`AICE-611`](./AICE-611.md) — component-local evidence standing in for an end-to-end path (620's paths are both exercised end to end).
- [`AICE-612`](./AICE-612.md) — a conclusion about one actor's path transferred to another (620 observes both paths directly).
