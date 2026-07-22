# AICE-610 — Control Exists, Enforcement Not Found

**Unofficial draft (AICE v0.6.0).**

## Canonical identifier

`AICE-610`

## Human-readable alias

`HTTP 610 — Control Exists, Enforcement Not Found`

## Intent

Catch the case where a control, guardrail, policy object, safety capsule, approval
result, or other protective mechanism physically exists and may validate successfully,
but the actual execution path is not causally bound to that control. Runtime behavior
proceeds through another path, a bypass, or an unguarded consumer, so the control governs
nothing it is claimed to govern.

Canonical machine form:

```
CONTROL_PRESENT
CONTROL_VALIDATED
EXECUTION_PATH_NOT_BOUND_TO_CONTROL
WORKFLOW_EFFECT = STATE_UNCHANGED
```

## Field maxim (non-normative)

> A guardrail outside the execution path is stage scenery.

Memorable rationale only — it changes no normative behavior. A control that exists and
even validates is not enforcement; enforcement is the property that the real executor
cannot proceed without consuming the control.

## Why this is a distinct code

AICE-610 is not a missing-artifact or missing-implementation code:

- `AICE-604` — the claimed artifact or bytes are absent.
- `AICE-605` — the claimed implementation is absent.
- `AICE-606` — a PASS is claimed without an observed test or validator execution.
- `AICE-610` — the control and its implementation exist, but actual runtime execution
  does not depend on them.

Compact distinction:

```
604 = the object does not exist
605 = the implementation does not exist
610 = the implementation exists, but runtime does not depend on it
```

AICE-610 is **not** triggered merely because a control is weak, incomplete, or
misconfigured. Its defining defect is the missing causal binding between the protective
control and the real execution path.

## Trigger condition

All of the following hold:

1. a protective control physically exists;
2. the control is expected or claimed to govern a specific runtime action;
3. the control can be constructed, persisted, parsed, or validated successfully;
4. the governed action can occur without consuming the control result;
5. a bypass, alternate route, disconnected consumer, shadow-only path, or equivalent
   missing binding is observed;
6. the required enforcement postcondition is therefore absent.

The incident MUST NOT be emitted solely because a control file exists without proof that
it was intended to govern the observed action.

## Required observations

Evidence classes that establish the incident:

- bytes or object identity of the control;
- a successful control validation or construction receipt;
- the expected consumer or enforcement boundary;
- the actual call path, runtime trace, invocation graph, or equivalent observation;
- proof that the governed action bypassed or ignored the control;
- preferably a counterfactual probe showing that changing, invalidating, or removing the
  control does not alter the supposedly governed execution path.

A counterfactual mutation is not required when it would be unsafe in production; an
independently observed call graph or runtime trace MAY be sufficient. Narrative
architectural diagrams alone are **not** evidence of enforcement.

## Missing-evidence condition

The control exists and may validate, but no observation shows the real executor consuming
the control result before performing the protected action; a bypass or unguarded consumer
is present, so the enforcement postcondition is unproven.

## False-positive guards

AICE-610 MUST NOT fire when:

- the mechanism is explicitly documented as telemetry-only or shadow mode;
- the control is outside the declared scope of the action;
- the feature is intentionally disabled by an observed configuration;
- the object is a design artifact or test fixture never claimed to govern production
  runtime;
- an explicitly authorized emergency bypass was used and its separate policy, provenance,
  and postcondition were observed;
- the control was consumed but produced an incorrect decision — that is a control-quality
  defect, not missing enforcement binding;
- enforcement occurred at a different layer and that binding is independently demonstrated.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

The protected operation MUST NOT be promoted, accepted, released, or marked complete
while enforcement binding is unproven. Additional validation of the control object alone
MUST NOT resolve the incident.

## Remediation

Remediation is **not** "add another validator" or "persist the control more carefully".
The required remediation is causal binding:

```
protected input
  -> mandatory control evaluation
  -> control result consumed by the real executor
  -> fail-closed behavior when the control is missing or invalid
  -> protected action
  -> independently observed postcondition
```

Acceptance requires evidence that:

1. the real executor consumes the intended control;
2. missing or invalid control blocks the protected action;
3. the previous bypass is removed or separately governed;
4. a negative test demonstrates fail-closed behavior;
5. a positive test demonstrates successful execution through the controlled path;
6. runtime evidence proves the tested path is the actual path used.

Retryability: `requires_new_evidence` — the incident becomes retryable only after
remediation is applied and the actual execution path has been re-observed.

## Example

Representative, sanitized example — **not** a verified historical record:

- a strongly validated safety/coder "capsule" is created and passes its own validation;
- the capsule physically exists;
- the real executor reaches the protected action through another route and does not
  consume the capsule;
- runtime therefore does not depend on the capsule, which exists largely as architectural
  scenery.

The remediated shape of this pattern is a control the executor is required to consume —
for example a mandatory capsule whose absence or invalidity fails closed before the
protected action, with an observed "capsule consumed" postcondition on the real path.

See
[`../../../examples/aice/aice-610-control-without-enforcement.json`](../../../examples/aice/aice-610-control-without-enforcement.json).
The example is labeled representative; no third-party commit, path, or digest is asserted.

## Related codes

- [`AICE-605`](./AICE-605.md) — release without an observed implementation delta.
- [`AICE-606`](./AICE-606.md) — PASS without a verified run.
- [`AICE-608`](./AICE-608.md) — verification lacking independence.
