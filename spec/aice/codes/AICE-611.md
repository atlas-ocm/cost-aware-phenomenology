# AICE-611 — Operational Reachability Substitution

**Unofficial draft (AICE v0.6.0).**

## Canonical identifier

`AICE-611`

## Human-readable alias

`HTTP 611 — Operational Reachability Substitution`

## Intent

Catch the case where a system, workflow, agent capability, or protected operation is
accepted as working because its components, validators, guards, tests, receipts, schemas,
or seals exist and pass independently, while the authorized end-to-end path from real
operator input to the required externally observable postcondition is unreachable,
bypassed by the tested harness, or has never been executed and observed.

The defect is the substitution of component validity for operational reachability.

Canonical machine name: `OPERATIONAL_REACHABILITY_SUBSTITUTION`.

Canonical machine form:

```
LOCAL_COMPONENT_EVIDENCE_PRESENT
END_TO_END_PATH_REQUIRED
END_TO_END_PATH_REACHABILITY_NOT_ESTABLISHED
REQUIRED_POSTCONDITION_UNOBSERVED
WORKFLOW_EFFECT = STATE_UNCHANGED
```

Canonical compact form:

```
VALIDATED_COMPONENTS
≠
WORKING_SYSTEM
```

## Field maxim (non-normative)

> Validated components are not a working system.

Secondary maxim (non-normative):

> A collection of PASSes is not an end-to-end execution path.

Memorable rationale only — they change no normative behavior. Component validity is a
real but weaker claim than authorized system behavior from the real entrypoint.

## Core acceptance predicate

A capability MUST NOT be accepted as operational unless an authorized path has been
observed from the real declared entrypoint to the required postcondition:

```
REAL_OPERATOR_INPUT
  -> DECLARED_ENTRYPOINT
  -> AUTHORIZED_ROUTER_OR_FSM
  -> REQUIRED_CONTROLS_AND_COMPONENTS
  -> REAL_EXECUTOR_OR_TOOL
  -> REQUIRED_EXTERNAL_POSTCONDITION
  -> INDEPENDENT_READBACK
```

Static reachability, imported modules, registered handlers, passing unit tests,
component-local receipts, mocks, synthetic harnesses, direct internal function calls,
architectural diagrams, and model narratives are **not** substitutes for observed
traversal of the required path. The path MUST begin at the entrypoint an actual operator
or authorized caller is expected to use, and MUST end at the real postcondition used to
define success.

## Two subcases

Operational reachability can remain unestablished in two ways; both satisfy the shared
predicate `END_TO_END_PATH_REACHABILITY_NOT_ESTABLISHED`.

1. `STRUCTURALLY_UNREACHABLE` — the authorized path cannot actually be traversed
   (disconnected routing, an unused handler, an unreachable state transition, a missing
   caller, an unregistered command, an alternate execution route, incompatible
   contracts, or another integration defect).
2. `NEVER_EXECUTED_END_TO_END` — the path may appear structurally plausible, but no real
   operator-style execution has traversed the complete authorized chain and produced the
   required observed postcondition.

A verified structural break is stronger evidence, but the absence of any real end-to-end
execution is sufficient to block an operational PASS when such a PASS is claimed. Absence
of end-to-end execution does **not**, by itself, prove structural impossibility.

## Why this is a distinct code

- `AICE-604` — a claimed artifact or materialized object is absent.
- `AICE-605` — a claimed implementation or release is absent.
- `AICE-606` — a PASS is claimed without an observed test or validator execution.
- `AICE-607` — a deployment is claimed without independently observed production presence
  or effect.
- `AICE-608` — verification is claimed without sufficient verifier independence.
- `AICE-609` — consensus is substituted for evidence.
- `AICE-610` — a specific protective control exists and may validate, but the executor is
  not causally bound to its decision.
- `AICE-611` — real implementations, controls, validators, tests, receipts, and PASS
  results may all exist, but the complete authorized operator-to-postcondition path is
  unreachable or has never been observed.

Compact distinction:

```
604 = the object does not exist
605 = the implementation does not exist
606 = the claimed test execution does not exist
610 = the control exists, but execution does not depend on it
611 = the components exist, but the working end-to-end system is not established
```

`AICE-610` may be a causal contributor to `AICE-611`, but the codes are not equivalent. A
disconnected policy control in an otherwise operational workflow is `AICE-610`; a workflow
whose locally valid components cannot be reached from its real entrypoint is `AICE-611`.
When both are independently established, record them as distinct findings rather than
collapsing their meanings; do not alter the incident-envelope cardinality to express
co-occurrence.

## Trigger condition

All of the following hold:

1. a system, capability, workflow, or operation is claimed to be working, complete,
   ready, accepted, integrated, or operational;
2. a real declared entrypoint exists or is implied by the claim;
3. a required externally observable postcondition can be stated;
4. evidence exists for one or more local components (schemas, validators, guards,
   handlers, routers, tools, tests, fixtures, receipts, seals, component-local PASS
   results);
5. the evidence used for acceptance does not establish traversal of the full authorized
   path from the real entrypoint to the required postcondition;
6. at least one of the following is observed: the path is structurally unreachable; the
   real entrypoint invokes another path; a required transition has no authorized caller;
   a component is tested only through a direct internal invocation; mocks or synthetic
   harnesses bypass actual orchestration; the path has never been executed end to end;
   the expected postcondition has never been independently read back;
7. the required operational postcondition therefore remains unobserved.

The incident MUST NOT be emitted merely because end-to-end testing would be desirable; it
applies when operational acceptance depends on a path whose reachability has not been
established.

## Required observations

Evidence classes:

- the claimed capability and its acceptance boundary;
- the declared real entrypoint and a real operator-style input;
- the expected authorized route and the required externally observable postcondition;
- component-local PASS receipts;
- an actual runtime trace, call graph, FSM trace, tool-invocation log, or event log;
- evidence that the real entrypoint cannot reach the required route, that test harnesses
  invoke internal components directly, that the real path has never executed, or that the
  required postcondition has not been independently observed.

Strong evidence includes invoking the declared entrypoint and observing that no authorized
transition reaches the executor; tracing a real request through the FSM; proving a handler
has no reachable caller; proving a tested function is not used by the production
entrypoint; observing the workflow terminate before the required action; or demonstrating
that no episode, receipt, or readback exists for a complete real execution. A static code
graph may support the diagnosis but does not alone prove that a path executed. A model
statement that "the full pipeline is wired" is not evidence, and a list of passing
component tests is not evidence of end-to-end reachability.

## Missing-evidence condition

Local component evidence is present and an operational claim is made, but no observation
shows the authorized path being traversed from the real entrypoint to the required
postcondition, and the required postcondition has not been independently read back; the
path is either structurally unreachable or has never been executed end to end.

## False-positive guards

AICE-611 MUST NOT fire when:

- the artifact is explicitly a library, component, prototype, or partial subsystem and no
  operational end-to-end claim is made;
- the tested internal API is itself the declared production entrypoint;
- a real authorized end-to-end execution has been observed and the required postcondition
  independently read back;
- the path is intentionally disabled by an observed configuration and nobody claims the
  capability is currently operational;
- the capability is explicitly marked incomplete, experimental, or blocked and has not
  been promoted;
- only a non-required optional branch is unreachable;
- the postcondition occurred through a different but explicitly authorized and
  independently observed implementation;
- a safe shadow-mode or dry-run path is correctly described as shadow mode or dry run
  rather than operational execution;
- the end-to-end execution failed visibly and the workflow remained blocked instead of
  being promoted;
- the operator entrypoint is unavailable solely because the environment is intentionally
  offline and no readiness claim is made for that environment.

Do not emit AICE-611 merely because unit tests exist, merely because no UI exists when an
API/CLI/queue is the declared operational interface, or merely because the path has not
been manually exercised if equivalent real-path automated evidence establishes the same
entrypoint, routing, executor, environment, and postcondition.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

The system, feature, workflow, integration, or episode MUST NOT be promoted to `PASS`,
`COMPLETE`, `READY`, `OPERATIONAL`, `INTEGRATED`, `RELEASED`, or `VERIFIED_END_TO_END`
while operational reachability remains unestablished. Additional component-local evidence
alone MUST NOT resolve the incident.

## Remediation

Remediation is **not**: adding more unit tests; adding another component validator;
producing another receipt; inspecting another schema; proving each function works
independently; calling the internal function directly; constructing a synthetic green
harness that bypasses the real entrypoint; or asking another model whether the
architecture looks connected.

Required remediation is an observed operational path:

```
real operator-style input
  -> declared public entrypoint
  -> actual production router or FSM
  -> required policy and control boundaries
  -> selected executor or tool
  -> required state mutation or external effect
  -> independent postcondition readback
  -> episode or incident receipt
```

Acceptance requires evidence that:

1. the real entrypoint received the request;
2. the request traversed the intended authorized routing and FSM transitions;
3. the actual runtime implementation was invoked rather than a fixture, surrogate, mock,
   or direct test-only entrypoint;
4. required guards and controls participated in the same execution;
5. the externally observable postcondition occurred;
6. the postcondition was independently read back;
7. the execution produced a durable episode, receipt, trace, or equivalent evidence
   binding input, path, result, and postcondition;
8. disabling or disconnecting a mandatory transition causes the end-to-end acceptance test
   to fail rather than remain green.

A successful remediation must prove both `PATH_REACHABLE = true` and `PATH_EXECUTED = true`.
Static wiring evidence is not a substitute for execution. Retryability:
`requires_new_evidence` — retryable only after the reachability defect is remediated and
the authorized end-to-end path has been executed again from the real entrypoint.

## Relation to synthetic and component tests

Synthetic tests, fixtures, mocks, schema validation, component tests, and direct internal
invocations remain useful and may prove local properties. They MUST NOT be substituted for
the first real execution of the required operator-to-postcondition chain. The correct
evidence order for an operational claim is:

```
real defect or real required path
  -> observed execution
  -> captured integration failure or success
  -> synthetic regression fixture
  -> repeatable prevention proof
```

The defect is not that synthetic tests are invalid; it is their use as a replacement for
operational reachability:

```
COMPONENT_TEST_PASS      proves  COMPONENT_BEHAVIOR_UNDER_TEST_HARNESS
END_TO_END_PATH_PASS     proves  AUTHORIZED_SYSTEM_BEHAVIOR_FROM_REAL_ENTRYPOINT
```

These are different claims.

## Example

`REPRESENTATIVE_EXAMPLE` — `NOT_A_VERIFIED_HISTORICAL_INCIDENT`.

A self-maintenance workflow is reported operational: its schema validators, guards,
scorer, coder path, verifier path, component tests, and receipts all exist and pass when
invoked directly. But the real operator entrypoint cannot reach the full chain — an
authorized transition is not wired to the executor, and no real operator-style request has
ever traversed entrypoint → FSM → scorer → coder → verifier → episode to produce and read
back the required postcondition. Component validity was substituted for a working system.

The remediated shape of this pattern is a system that treats reachability from the real
entrypoint as a first-class, blocking property — refusing to promote a capability to
operational until an authorized request has been observed traversing the complete chain
and the postcondition has been independently read back.

See
[`../../../examples/aice/aice-611-operational-reachability-substitution.json`](../../../examples/aice/aice-611-operational-reachability-substitution.json).
The example is labeled representative; no third-party commit, path, digest, or historical
conclusion is asserted.

## Related codes

- [`AICE-606`](./AICE-606.md) — PASS without a verified run.
- [`AICE-607`](./AICE-607.md) — deployment without an observed production state.
- [`AICE-610`](./AICE-610.md) — a control the executor is not bound to (a possible cause).
- [`AICE-612`](./AICE-612.md) — actor path substitution: an operator-path conclusion (including a `NOT_ESTABLISHED` verdict here) MUST NOT be inferred from a different actor's path result.
- [`AICE-613`](./AICE-613.md) — self-hosting mutation-shape deadlock: when the end-to-end path is unreachable specifically because the system cannot materialize the bounded mutation required to fix or upgrade its own limiting mechanism, AICE-613 is the first broken edge; report it precisely rather than collapsing it into a generic AICE-611 unobserved-postcondition finding.
- [`AICE-614`](./AICE-614.md) — infrastructure failure as semantic verdict: an AICE-614 result may cause or coexist with an AICE-611 finding, but converting an infrastructure failure into a semantic verifier verdict is a distinct defect from an unestablished end-to-end path.
