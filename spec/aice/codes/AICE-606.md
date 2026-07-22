# AICE-606 — PASS Exists, Test Run Not Found

**Unofficial draft (AICE v0.1.0).**

## Canonical identifier

`AICE-606`

## Human-readable alias

`HTTP 606 — PASS Exists, Test Run Not Found`

## Intent

Catch the case where a PASS, success verdict, benchmark result, or validation claim
exists without evidence that the test actually ran.

## Trigger condition

A success verdict or validation claim exists without a verified execution receipt or
equivalent evidence of an actual run.

## Required observations

Evidence that the test ran, which may include:

- command or invocation identity;
- start/end timestamps;
- exit status;
- test identity and input set;
- captured output or a structured result;
- environment identity where material;
- an artifact or report tied to the run.

## Missing-evidence condition

A PASS/success/benchmark/validation claim is present, but none of the above execution
evidence is available, and no trustworthy external receipt substitutes for it.

## False-positive guards

- a trustworthy external CI receipt may satisfy the requirement even if the local
  process was not directly observed;
- a verifier's prose alone does **not** satisfy the requirement.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

The PASS MUST NOT be accepted as closing a defect or validating behavior until an
execution receipt is observed.

## Remediation

Produce the execution receipt (command, exit status, captured output, or a trustworthy
CI record) and attach it to the claim. Retryability: `requires_new_evidence`.

## Example

```
CLAIM: "all tests pass"
observed_evidence: []            # no command, no exit status, no output
missing_evidence: exit_status, captured_output, command_identity
workflow_effect: STATE_UNCHANGED, BLOCK_ACCEPTANCE
```

## Related codes

- [`AICE-608`](./AICE-608.md) — verification lacking independence.
- [`AICE-609`](./AICE-609.md) — consensus offered in place of evidence.
