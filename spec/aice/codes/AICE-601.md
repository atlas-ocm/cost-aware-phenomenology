# AICE-601 — Minimum Sufficient Mechanism Bypass

**Unofficial draft (AICE v0.9.0).**

## Canonical identifier

`AICE-601`

## Human-readable alias

`HTTP 601 — Not Implemented`

"Not Implemented" is a non-normative pun on the conventional HTTP 501 label. It carries no
relation to the standardized meaning of HTTP 501 beyond the joke, and asserts no IETF,
HTTP, RFC, standards-body, or industry-standard status. The pun names the failure shape:
the *smaller sufficient mechanism* is the one left "not implemented" while a larger one is
built around it.

## Intent

Catch the case where a bounded objective already has a currently evidenced admissible
mechanism that satisfies every active safety, authority, evidence, rollback, and
verification invariant, yet a **larger** mechanism is introduced, landed, or made
prerequisite **without a unique necessity witness**, increasing control surface or
execution cost and delaying, blocking, or displacing the sufficient path.

The defining defect is **not** that architecture exists, nor that a larger design is ever
discussed. The defect is that a larger mechanism was made *operationally prerequisite*
when a smaller admissible one existed, and no reproduced failure, missing invariant,
compatibility constraint, or measured requirement justified the expansion.

Canonical machine name: `MINIMUM_SUFFICIENT_MECHANISM_BYPASS`.

Canonical law:

```
MORE_ARCHITECTURE
≠
MORE_SAFETY
```

Canonical distinctions:

```
GENERIC_EXTENSIBILITY          ≠ CURRENT_REQUIREMENT
MODEL_MEDIATED_EXECUTION       ≠ SAFER_EXECUTION
MORE_APPROVAL_STEPS            ≠ STRONGER_EVIDENCE
REUSABLE_ARCHITECTURE_CLAIM    ≠ PROVEN_REUSE_DEMAND
GOVERNANCE_COMPLEXITY          ≠ RISK_REDUCTION
```

Canonical definition of *minimum sufficient*:

> `MINIMUM_SUFFICIENT` = the smallest currently evidenced admissible mechanism that
> satisfies the frozen objective and every active invariant.

It does **not** mean fewest lines, fewest files, fewest tests, no verifier, no rollback,
or no governance. A sufficient mechanism keeps every invariant; it merely stops adding
control surface that no witness demands.

## Canonical machine form

```
OBJECTIVE_MECHANICALLY_BOUNDED
MINIMUM_SUFFICIENT_PATH_IDENTIFIED
MINIMUM_PATH_SATISFIES_ALL_ACTIVE_INVARIANTS
LARGER_MECHANISM_INTRODUCED_OR_MADE_PREREQUISITE
UNIQUE_NECESSITY_WITNESS_FOR_EXPANSION = absent
EXPANSION_INCREASES_SURFACE_OR_COST
SUFFICIENT_PATH_DELAYED_BLOCKED_DISPLACED_OR_DENIED
WORKFLOW_EFFECT = STATE_UNCHANGED
WORKFLOW_EFFECT = BLOCK_ACCEPTANCE
```

## Trigger condition

AICE-601 requires evidence supporting all applicable elements:

1. `OBJECTIVE_MECHANICALLY_BOUNDED` — the objective is a concrete, bounded transition or
   task family, not an open-ended capability;
2. `MINIMUM_SUFFICIENT_PATH_IDENTIFIED` — a currently evidenced admissible mechanism for
   that objective exists;
3. `MINIMUM_PATH_SATISFIES_ALL_ACTIVE_INVARIANTS` — that smaller path preserves every
   active safety, authority, evidence, rollback, and verification invariant;
4. `LARGER_MECHANISM_INTRODUCED_OR_MADE_PREREQUISITE` — a larger mechanism is introduced,
   landed, or made a prerequisite for the objective;
5. `UNIQUE_NECESSITY_WITNESS_FOR_EXPANSION = absent` — no reproduced failure mode, missing
   verifier independence, missing rollback/atomicity, missing evidence binding, mandatory
   compatibility/migration constraint, measured operational-scale requirement, or
   confirmed multi-use-case demand justifies the expansion;
6. `EXPANSION_INCREASES_ONE_OR_MORE` of: authority surface; mutable state space; execution
   paths; failure modes; implementation cost; verification burden; time-to-action;
7. `SUFFICIENT_PATH_DELAYED_BLOCKED_DISPLACED_OR_DENIED` — the smaller path is delayed,
   blocked, displaced, or treated as inadmissible.

Required formula:

```
MINIMUM_SUFFICIENT_PATH_ESTABLISHED
AND ARCHITECTURE_EXPANSION_MADE_PREREQUISITE
AND UNIQUE_NECESSITY_WITNESS_ABSENT
AND EXPANSION_INCREASES_SURFACE_OR_COST
AND ORIGINAL_TASK_DELAYED_BLOCKED_OR_DISPLACED
→ MINIMUM_SUFFICIENT_MECHANISM_BYPASS
```

If minimum sufficiency is not itself established, the correct status is
`UNKNOWN_MINIMUM_SUFFICIENT_PATH`: a bounded diagnostic or an isolated feasibility spike
may be permitted, but permanent architecture admission remains denied until sufficiency is
known.

## Required observations

Evidence classes include: the frozen bounded objective; the active invariant set; the
exact smaller mechanism and proof it satisfies those invariants (a passing run, an
exact-preimage/postimage pair, a deterministic apply, a rollback path, an independent
verification route); the larger mechanism and the exact point at which it was made
prerequisite (an instruction-file clause, a mandatory call, a "do not use the direct path"
rule, a route policy); the search for a unique-necessity witness and its absence; the
concrete surface/cost the expansion added; and the observed displacement of the sufficient
path (a "deprecated bypass" label, a forbidden alternative, a required cleanup that later
restored the smaller path).

Strong evidence includes exact preimage → postimage pairs of governance/instruction files
in which a mandatory larger apparatus was later replaced by a smaller invariant-preserving
rule, with the invariants demonstrably retained across the change.

## Missing-evidence condition

A smaller admissible mechanism satisfied every active invariant for a bounded objective,
but a larger mechanism was made prerequisite without a unique necessity witness, adding
surface or cost and displacing the sufficient path — and no evidence establishes that the
expansion was required to preserve any invariant the smaller path did not already hold.

## False-positive guards

AICE-601 MUST NOT fire when any of the following holds (each is a valid **negative
control**):

- the added component has a verified unique necessity witness: a reproduced failure mode
  the smaller path does not close; missing verifier independence; missing exact rollback or
  atomicity; missing evidence binding; a mandatory compatibility or migration constraint; a
  measured operational-scale requirement; several confirmed use cases needing a shared
  mechanism; or a demonstrated net reduction in total architecture complexity;
- the architecture was **merely proposed and refused** — never made operationally
  mandatory. A rejected over-build is not an incident; it is the control working;
- the incident rests on **complexity alone**. A large system is not, by that fact, an
  AICE-601 incident; displacement of an established sufficient path must be observed;
- a smaller **deterministic** mechanism was later adopted to **replace** a larger
  model-mediated one. That is the correct direction (the system moving toward minimum
  sufficiency) and is the opposite of this incident;
- a reserved-but-unimplemented operation is cited as the "sufficient path": an operation
  that does not yet exist could not have been displaced and is not an admissible
  alternative;
- minimum sufficiency was genuinely unknown and the response was a bounded spike rather
  than a permanent mandatory subsystem (`UNKNOWN_MINIMUM_SUFFICIENT_PATH`).

```
PROPOSED_BUT_REFUSED_ARCHITECTURE     ≠ INCIDENT
COMPLEXITY_ALONE                      ≠ AICE-601
DETERMINISTIC_REPLACING_MODEL_RAIL    ≠ DISPLACEMENT_OF_A_SUFFICIENT_PATH
UNIMPLEMENTED_OPERATION               ≠ ADMISSIBLE_ALTERNATIVE
```

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

A detected AICE-601 incident MUST block acceptance of claims such as: the larger mechanism
is required; the expansion made the objective safer; generic extensibility justified the
build now. The bounded remediation is to select the minimum sufficient path; workflow state
does not advance to accept the expansion. Retryability: `requires_new_evidence`.

## Remediation

Remediation is **not**: deleting governance, verifiers, rollback, or evidence binding to
"go smaller"; shipping the objective with fewer invariants than the risk requires; or
banning all future architecture. Required remediation is to **select the minimum sufficient
path** — the smallest currently evidenced admissible mechanism that satisfies the frozen
objective and every active invariant — and to admit the larger mechanism only once a unique
necessity witness for it is produced (a reproduced failure, a missing invariant, a measured
scale requirement, or a confirmed multi-use demand).

Acceptance requires evidence that the smaller path performed the bounded objective while
preserving every active invariant, and that no admitted larger component lacks a necessity
witness.

## Example

`VERIFIED_INTERNAL_HISTORICAL_SCOPE` (narrow) for the displacement predicate; all other
detail is `REPRESENTATIVE`.

Primary evidence is Cleanup Episode A — the `chore(ai): remove stale cap-probe governance`
commits (`cap-processor 5a5b750`, `v5.com.ua 3069ad2`, `Concept-Arena ddad2d0`). Their exact
preimages made a larger MCP/FSM/verifier-broker apparatus mandatory (for example, *"Call
`start_task` before any non-trivial work"*, *"Run advisory verification via
`run_advisory_verifier` only; never call the verifier directly"*, direct routes labelled
*"deprecated bypass"*). Their exact postimages replaced that apparatus with a smaller
tool-agnostic rule that preserves every invariant it actually protected (no self-review,
verifier independence, scoped evidence, explicit human authorization, transport honesty).
The invariant-preserving postimage is the witness that the larger apparatus lacked a unique
necessity witness and had displaced the sufficient path.

See
[`../../../examples/aice/aice-601-minimum-sufficient-mechanism-bypass.json`](../../../examples/aice/aice-601-minimum-sufficient-mechanism-bypass.json).
The example asserts no claim beyond the narrow displacement scope, and encodes the negative
controls (proposed-but-refused, complexity-alone, deterministic-replacing-model-rail) as
non-triggering.

## Related codes

- [`AICE-602`](./AICE-602.md) — a gateway that enforces a decision but is authority-blind,
  versus an unnecessary larger mechanism that displaces a sufficient path here.
- [`AICE-610`](./AICE-610.md) — a control that exists but is not causally enforced, versus a
  control that *is* enforced yet was never necessary here.
- [`AICE-613`](./AICE-613.md) — a self-hosting mutation-shape deadlock where the mutation
  mechanism cannot bootstrap itself, versus an expansion that had a working smaller
  alternative it displaced here.
