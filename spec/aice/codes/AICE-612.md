# AICE-612 — Actor Path Substitution

**Unofficial draft (AICE v0.7.0).**

## Canonical identifier

`AICE-612`

## Human-readable alias

`HTTP 612 — Actor Path Substitution`

## Intent

Catch the case where an audit, verifier, test, or diagnostic process observes the
reachability, blocking, authorization result, or behavior of one actor class and then
applies that result to a different actor class without independently testing the second
actor's authorized entrypoint, authority boundary, route, or postcondition.

The defect is the substitution of one actor-scoped path for another.

Canonical motivating correction:

```
PROPOSER_PATH_BLOCKED
≠
OPERATOR_PATH_MISSING
```

Canonical machine name: `ACTOR_PATH_SUBSTITUTION`.

Canonical machine form:

```
TESTED_ACTOR_PATH_PRESENT
TESTED_ACTOR_RESULT_OBSERVED
CLAIMED_ACTOR_DISTINCT
CLAIMED_ACTOR_PATH_NOT_TESTED
CROSS_ACTOR_INFERENCE_APPLIED
AUDIT_CONCLUSION_NOT_ESTABLISHED
WORKFLOW_EFFECT = STATE_UNCHANGED
```

Canonical compact form:

```
PATH_RESULT(actor_A) ≠ PATH_RESULT(actor_B)
unless path equivalence has been independently established.
```

## Field maxim (non-normative)

> A blocked proposer is not a missing operator.

Secondary maxim (non-normative):

> Reachability evidence does not transfer across authority boundaries.

Architectural metaphor (non-normative):

> Testing the model entrance does not prove that the operator entrance is missing.

Memorable rationale only — they change no normative behavior.

## Actor-scoped reachability model

Reachability MUST NOT be represented or inferred as a single unqualified boolean
(`PATH_REACHABLE = true | false`). The meaningful predicate is actor- and
authority-scoped:

```
REACHABILITY(actor, authority, entrypoint, route, environment, required_postcondition)
```

A path result applies only to the actor, authority boundary, entrypoint, route,
environment, and postcondition actually observed. This is the normative conceptual model;
an implementation need not literally use this tuple as a schema or runtime structure.

Relevant actor classes may include model proposer, autonomous agent, human operator,
authorized reviewer, administrator, scheduler, system service, verifier, executor,
emergency operator, or external API caller. "Operator" does not always mean a human; the
defining property is a distinct authority-bearing principal or actor class.

## Canonical example

```
model proposer
  -> may propose an operation
  -> must not invoke the protected executor directly
  -> direct executor path correctly returns DENY

human operator
  -> may inspect or approve the proposal
  -> uses a different authorized entrypoint
  -> may invoke the protected executor after authorization
```

If the audit performs only `proposer -> protected executor -> DENY` and concludes
"operator execution path does not exist", that conclusion is not established. The proposer
denial may be a correct safety property. AICE-612 MUST NOT recommend "fixing" the incident
by granting the proposer operator authority.

## Why this is a distinct code

- `AICE-604` — a claimed artifact or materialized object is absent.
- `AICE-605` — a claimed implementation or release is absent.
- `AICE-606` — a PASS is claimed without an observed test or validator execution.
- `AICE-607` — deployment/production effect claimed without observed production.
- `AICE-608` — verification claimed without sufficient independence.
- `AICE-609` — consensus substituted for evidence.
- `AICE-610` — a protective control exists but the executor is not causally bound to it.
- `AICE-611` — the claimed end-to-end operational path was examined, but its reachability
  or execution from the real entrypoint to the required postcondition was not established.
- `AICE-612` — one actor's path was examined, but the result was transferred to another
  actor's path without evidence of equivalence.

Canonical distinction:

```
AICE-611: operator path examined  -> operator-path reachability not established
AICE-612: proposer path examined  -> operator-path conclusion asserted
```

`AICE-612` may generate a false `AICE-611` diagnosis; do not collapse the two codes.
`AICE-610` concerns runtime causal enforcement (execution can bypass the control);
`AICE-612` concerns invalid cross-actor inference (the control may be working correctly by
blocking the proposer, but the auditor misreads that denial as absence of the operator
route). Both defects may coexist, but one does not imply the other. Do not alter the
incident-envelope cardinality to represent co-occurrence.

## Trigger condition

All of the following hold:

1. a conclusion is claimed about the reachability, availability, authorization, blocking,
   success, failure, or existence of a path for a specific actor class;
2. the observed test, trace, or probe exercised a different actor class;
3. the tested and claimed actors differ in at least one material dimension (authority,
   identity/principal, entrypoint, route, credentials, approval state, policy context,
   environment, or required postcondition);
4. the claimed actor's actual authorized path was not independently exercised;
5. no evidence establishes that the two actor paths are equivalent for the conclusion
   being made;
6. the observed result from the tested actor was transferred to the untested actor;
7. that transferred result was used to support an audit verdict, operational conclusion,
   acceptance or rejection decision, blocker, or incident classification.

The incident MUST NOT be emitted merely because two actor classes exist; the defining
defect is an unsupported cross-actor inference.

### Canonical invalid inferences

```
proposer denied direct execution           -> operator execution is impossible
anonymous caller receives 403              -> authenticated administrator route is missing
read-only verifier cannot mutate state     -> no authorized executor can mutate state
test worker cannot access production secret-> deployment automation cannot access it
external API caller blocked from a route   -> the internal maintenance route does not exist
human operator can perform an action       -> the model proposer may perform the same action
```

The final example shows AICE-612 can produce both false-negative and false-positive
authority conclusions; the code is not limited to model-versus-human cases.

## Required observations

Evidence classes:

- the exact actor/principal used by the probe, and the actor about whom the conclusion was
  made; their credentials, authority, role, approval state, or capability set;
- the tested entrypoint and route, and the claimed actor's declared entrypoint and route;
- expected authorization result for each actor and the actual result observed for the
  tested actor;
- evidence that the claimed actor path was not exercised;
- absence of a demonstrated actor-path equivalence;
- the audit verdict or workflow decision that transferred the result.

Strong evidence may include an execution trace showing the proposer denied at a protected
executor boundary; a separate route definition showing the operator enters through an
approval/authorization endpoint; policy rules assigning different capabilities to proposer
and operator; distinct principal identifiers; an audit script invoking only the
proposer-facing surface; a report generalizing the proposer result to an operator claim; a
path matrix with only one actor row exercised; an operator-path probe that was never run;
or a successful operator-path execution proving the prior negative conclusion false.

A model statement that two actor paths are equivalent is not evidence. Shared function
names are not sufficient evidence of path equivalence, and a common downstream executor
does not make upstream authorization paths equivalent.

## Missing-evidence condition

A conclusion about a claimed actor's path rests on a result observed for a different actor;
the claimed actor's authorized path was never exercised and no actor-path equivalence was
established, so the claimed actor path status is unestablished rather than proven present
or absent.

## False-positive guards

AICE-612 MUST NOT fire when:

- the tested and claimed actor are the same principal and authority context;
- the conclusion is explicitly limited to the tested actor (e.g. "the proposer cannot
  invoke this route");
- proposer and operator genuinely use the same entrypoint, credentials, authorization
  context, route, and required postcondition, and this equivalence is independently
  established;
- the operator path was separately tested;
- the claimed capability is explicitly autonomous and contains no operator route;
- the blocked proposer path is the only declared production entrypoint;
- the system correctly reports the second actor's path as `NOT_ESTABLISHED` rather than
  absent;
- the tested actor is a faithful delegated representative of the claimed actor and the
  delegation equivalence is materially proven;
- the difference between actors is irrelevant to the exact conclusion and this irrelevance
  is independently demonstrated;
- an authorized path is intentionally disabled and the conclusion is scoped to that
  observed configuration;
- both actors provably converge before any authority-sensitive decision and the remaining
  route is independently proven identical.

Do not emit AICE-612 merely because different labels such as "user" and "operator" appear
in documentation; cosmetic naming differences are not distinct authority boundaries.

## Workflow semantics

```
STATE_UNCHANGED
```

The unsupported cross-actor conclusion MUST NOT be used to declare the claimed actor path
missing, declare the system unreachable, emit `AICE-611`, grant broader authority, remove
an existing guard, reject or accept an operational capability, close an audit, or promote a
final PASS or FAIL. The correct state is:

```
CLAIMED_ACTOR_PATH_STATUS = NOT_ESTABLISHED
```

until the correct actor path is independently observed.

## Remediation

Remediation is **not**: unblock the proposer; grant the model operator credentials; remove
the authorization boundary; merge all actor roles; rename the operator path; rerun the same
proposer probe; ask another model whether the routes are equivalent; or infer operator
reachability from static component presence.

Required remediation is an actor-path matrix with separately observed results:

```
ACTOR     ENTRYPOINT         AUTHORITY               EXPECTED RESULT
proposer  proposal endpoint  propose-only            proposal accepted or rejected
proposer  executor endpoint  no execute authority    denied
operator  approval endpoint  authorize               approval recorded
operator  executor route     execute-after-approval  permitted after valid authorization
```

Acceptance requires evidence that every actor in the disputed conclusion is identified with
its authority boundary and claimed entrypoint; expected allow/deny behavior is declared
before the probe; the proposer denial is independently observed; the operator authorization
path is independently exercised; the operator execution path is independently exercised when
execution is part of the claim; the required external postcondition is independently read
back; actor identity, authority, route, execution result, and postcondition are bound in a
durable trace/episode/receipt; and the final audit conclusion is scoped only to the actor
paths actually observed.

Canonical remediation proof:

```
PROPOSER_DIRECT_EXECUTION = DENIED
OPERATOR_AUTHORIZATION    = OBSERVED
OPERATOR_EXECUTION        = OBSERVED
POSTCONDITION_READBACK    = OBSERVED
```

The proposer denial and operator success are not contradictory; together they may
demonstrate correct authority separation. Retryability: `requires_new_evidence` — retryable
only after the claimed actor's actual path has been tested, or actor-path equivalence has
been independently established.

## Relation to safety

A blocked proposer path may be a required safety postcondition. The fact
`MODEL_PROPOSER_CANNOT_EXECUTE_DIRECTLY = true` is not evidence of missing functionality; it
may instead prove `AUTHORITY_SEPARATION_WORKS = true`. AICE-612 exists partly to prevent an
auditor from "remediating" a correctly protected system by weakening its authority boundary.

> Do not repair an audit substitution by granting the tested actor the authority of the
> untested actor.

## Non-normative explanatory model: Algorithmic Solipsism

A lock proves boundary enforcement, not system unavailability.

An automated auditor may incorrectly transform an actor-scoped observation:

> I cannot reach this operation.

into a system-wide conclusion:

> This operation cannot be reached.

This is an actor-context error, not evidence of global unavailability. A denial observed
for one principal establishes a fact only about that principal, authority context,
entrypoint, route, environment, and requested postcondition.

For example:

```text
REACHABLE(model_proposer, direct_executor) = false
REACHABLE(authorized_operator, approved_route) = NOT_ESTABLISHED
```

The first result does not determine the second. A correctly denied proposer may demonstrate
that authority separation is working as designed; it does not demonstrate that no authorized
operator path exists. In informal terms, the auditor mistakes the limits of its own
authority context for the limits of the system:

```text
DENIED_FOR_ME
  -> incorrectly generalized as
NONEXISTENT_FOR_ALL
```

"Algorithmic Solipsism" names this mechanism memorably only; it introduces no new normative
defect and anthropomorphizes nothing in the normative contract.

## Non-normative remediation hazard: Compliance-Driven Degradation

AICE-612 can become dangerous when an invalid cross-actor conclusion is passed to an
automated remediation system. A representative failure chain is:

```text
CORRECT_PROPOSER_DENIAL
  -> MISCLASSIFIED_AS_OPERATIONAL_UNREACHABILITY
  -> REACHABILITY_REPAIR_REQUESTED
  -> AUTHORITY_BOUNDARY_WEAKENED_OR_REMOVED
  -> PROPOSER_GAINS_EXECUTION
  -> END_TO_END_PROBE_PASSES
  -> FORMAL_COMPLIANCE_IMPROVES
  -> ACTUAL_SYSTEM_SAFETY_DEGRADES
```

This is *compliance-driven degradation*: the system is modified to satisfy an incorrect
audit conclusion, and the resulting green path is achieved by destroying a valid authority
boundary. Do not remediate AICE-612 by:

- granting the tested actor the claimed actor's authority;
- removing approval requirements;
- exposing a protected executor directly;
- merging proposer and operator roles;
- weakening a control until the original probe passes.

The correct remediation is to test the claimed actor through its own authorized path. A
successful proposer denial and a successful operator execution are not contradictory:

```text
PROPOSER_DIRECT_EXECUTION = DENIED
OPERATOR_AUTHORIZATION    = OBSERVED
OPERATOR_EXECUTION        = OBSERVED
POSTCONDITION_READBACK    = OBSERVED
```

Together, these results may demonstrate correct authority separation. Compliance-Driven
Degradation is documented here as a remediation hazard within AICE-612, **not** as a new
incident code; it is not yet a separately observed incident class.

### Field maxims (non-normative)

> A blocked proposer is not a missing operator.

> Reachability evidence does not transfer across authority boundaries.

> A lock proves boundary enforcement, not system unavailability.

### Relationship to adjacent controls

- **AICE-610** asks whether execution can bypass the barrier.
- **AICE-611** asks whether an authorized actor can traverse the real path.
- **AICE-612** asks whether the audit tested the same actor about whom it made the
  conclusion.

## Example

`REPRESENTATIVE_EXAMPLE` — `NOT_A_VERIFIED_HISTORICAL_INCIDENT`.

An audit exercises only the model/proposer-facing surface, observes that direct execution is
correctly denied (`BLOCKED_LIVE_AUTHORITY_REQUIRED`), and concludes that the operator
execution path does not exist. The proposer and the authorized operator are distinct
principals with distinct authority boundaries and distinct entrypoints; the operator's
authorized route was never exercised and no actor-path equivalence was established. The
proposer denial is expected and may demonstrate correct authority separation; the operator
path is therefore `NOT_ESTABLISHED`, not proven missing — and not proven reachable either.

The remediated shape is an actor-separated architecture that keeps the proposer surface
blocked from live execution while exposing a distinct operator-authorized route, and that
scopes every audit conclusion to the actor path actually observed.

See
[`../../../examples/aice/aice-612-actor-path-substitution.json`](../../../examples/aice/aice-612-actor-path-substitution.json).
The example is labeled representative; no third-party commit, path, digest, actor role, or
historical conclusion is asserted as fact.

## Related codes

- [`AICE-602`](./AICE-602.md) — a real gateway collapses the actor's authority context
  inside its own decision; AICE-612 instead transfers one actor's path evidence to a
  different actor without a real gateway decision.
- [`AICE-608`](./AICE-608.md) — verification lacking independence.
- [`AICE-610`](./AICE-610.md) — a control the executor is not bound to (runtime enforcement).
- [`AICE-611`](./AICE-611.md) — operational reachability of the claimed path not established.
