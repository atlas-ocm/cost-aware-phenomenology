# AICE-603 — Governance-Induced Service Unavailability

**Unofficial draft (AICE v0.9.0).**

## Canonical identifier

`AICE-603`

## Human-readable alias

`HTTP 603 — Service Unavailable`

"Service Unavailable" is a non-normative pun on the conventional HTTP 503 label. It carries
no relation to the standardized meaning of HTTP 503 beyond the joke, and asserts no IETF,
HTTP, RFC, standards-body, or industry-standard status. The pun names the failure shape:
the service exists and a valid path to it exists, but an unnecessary locked gate makes it
*unavailable*.

## Intent

Catch the case where an underlying capability and at least one admissible execution path
exist, but an **unnecessary governance dependency** is made mandatory; that dependency is
unavailable, unreachable, or unsatisfiable, and the otherwise available capability is
consequently withheld from the authorized workflow.

The defining defect is **not** that a real capability is down. The defect is that a working
capability with a valid alternative path was withheld because a governance dependency that
the objective did not uniquely require was mandatory and could not be satisfied.

Canonical machine name: `GOVERNANCE_INDUCED_SERVICE_UNAVAILABILITY`.

Canonical law:

```
DEPENDENCY_UNAVAILABLE
≠
CAPABILITY_UNAVAILABLE
```

Canonical distinctions:

```
TOOL_MENTIONED             ≠ TOOL_REQUIRED
ONE_ROUTE_UNAVAILABLE      ≠ ALL_ADMISSIBLE_ROUTES_UNAVAILABLE
GOVERNANCE_PATH_UNAVAILABLE ≠ UNDERLYING_SERVICE_ABSENT
```

## Canonical machine form

```
UNDERLYING_CAPABILITY_EXISTS
ADMISSIBLE_EXECUTION_PATH_EXISTS
MANDATORY_GOVERNANCE_DEPENDENCY_EXISTS
DEPENDENCY_UNIQUELY_REQUIRED_BY_OBJECTIVE = false
MANDATORY_DEPENDENCY_STATUS ∈ { UNAVAILABLE, UNREACHABLE, UNSATISFIABLE }
CAPABILITY_WITHHELD_FROM_AUTHORIZED_WORKFLOW
WORKFLOW_EFFECT = STATE_UNCHANGED
WORKFLOW_EFFECT = BLOCK_ACCEPTANCE
```

## Trigger condition

AICE-603 requires evidence supporting all applicable elements:

1. `UNDERLYING_CAPABILITY_EXISTS` — the service or capability the workflow needs actually
   exists;
2. `ADMISSIBLE_EXECUTION_PATH_EXISTS` — at least one authority-preserving path to that
   capability exists (independent, exact-bytes, read-only where required, attributable,
   transport-complete);
3. `MANDATORY_GOVERNANCE_DEPENDENCY_EXISTS` — a specific governance dependency (a tool, a
   route, a control-plane call) is declared mandatory;
4. `DEPENDENCY_UNIQUELY_REQUIRED_BY_OBJECTIVE = false` — that dependency is not uniquely
   required by any active safety, authority, or independence invariant the objective needs;
5. `MANDATORY_DEPENDENCY_STATUS` is `UNAVAILABLE`, `UNREACHABLE`, or `UNSATISFIABLE`;
6. `CAPABILITY_WITHHELD_FROM_AUTHORIZED_WORKFLOW` — because the unnecessary mandatory
   dependency cannot be satisfied and admissible alternatives are forbidden, the capability
   is withheld.

Required formula:

```
SERVICE_IMPLEMENTATION_EXISTS
AND VALID_EXECUTION_PATH_EXISTS
AND UNNECESSARY_GOVERNANCE_DEPENDENCY_IS_MANDATORY
AND THAT_DEPENDENCY_IS_UNAVAILABLE
→ GOVERNANCE_INDUCED_SERVICE_UNAVAILABILITY
```

## Required observations

Evidence classes include: proof the capability exists (a working service, a passing route,
a deterministic mechanism); proof an admissible alternative path exists and preserves the
required invariants; the exact clause that made the specific dependency mandatory and
forbade the alternative (for example *"only via X"*, *"never call Y directly"*, *"if the
tool is unavailable, hold"*); proof the dependency was unavailable/unreachable/unsatisfiable
at the relevant time; and the observed withholding of the capability from the authorized
workflow. Restoration evidence — the dependency later removed, bypassed by ruling, or a
tool-agnostic rule admitted — strengthens the case.

## Missing-evidence condition

A capability and an admissible authority-preserving path to it existed, but an unnecessary
governance dependency was mandatory and unavailable, so the capability was withheld from the
authorized workflow — and no evidence establishes that the dependency was uniquely required
by a real safety or independence invariant, or that no admissible alternative path existed.

## False-positive guards

AICE-603 MUST NOT fire when any of the following holds (each is a valid **negative
control**):

- the underlying provider or capability is **genuinely unavailable** — an ordinary external
  outage is not this incident;
- **no admissible alternative path** exists: if every authority-preserving route is
  legitimately unavailable, the service is legitimately unavailable and this code does not
  apply;
- the dependency is **uniquely required** by a verified safety invariant or preserves a
  verifier independence that no alternative can provide, or is an unavoidable compatibility
  boundary;
- only a **transient transport failure** occurred and no false "service unavailable"
  conclusion was granted authority — correctly holding and reporting an infrastructure
  terminal is the right behavior, not an incident.

```
ORDINARY_PROVIDER_OUTAGE          ≠ AICE-603
NO_ADMISSIBLE_ALTERNATIVE         ≠ AICE-603  (service legitimately unavailable)
UNIQUELY_REQUIRED_DEPENDENCY      ≠ AICE-603
TRANSIENT_TRANSPORT_FAILURE_HELD  ≠ AICE-603
```

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

A detected AICE-603 incident MUST block acceptance of the claim that the capability is
unavailable. The bounded remediation is to remove or bypass the unnecessary dependency and
restore the admissible path; workflow state does not advance on the false-unavailability
claim. Retryability: `requires_new_evidence`.

## Remediation

Remediation is **not**: inventing a new route, simulating the missing tool, or weakening the
invariant the dependency legitimately protects. Required remediation establishes that the
dependency is not uniquely required, then restores an admissible authority-preserving path
to the existing capability (any authorized route that preserves independence, exact-byte
identity, read-only behavior where required, attributable output, and complete transport).
Acceptance requires evidence that the capability was reachable through an admissible path
that satisfied every active invariant without the unnecessary dependency.

## Example

`VERIFIED_INTERNAL_HISTORICAL_SCOPE` (narrow) for the withholding predicate; all other
detail is `REPRESENTATIVE`.

Primary evidence is Cleanup Episode A — the `chore(ai): remove stale cap-probe governance`
commits (`cap-processor 5a5b750`, `v5.com.ua 3069ad2`, `Concept-Arena ddad2d0`). Their exact
preimages made a specific stale MCP verification dependency mandatory and, on its
unavailability, mandated withholding while forbidding the admissible alternative — for
example *"Run advisory verification via `run_advisory_verifier` only; never call the
verifier directly"*, *"MCP/tooling unavailable → `MCP_UNAVAILABLE_HOLD`"*, and *"If MCP is
unavailable: hold and report the gap. Do not bypass the workflow or self-route manually."*
Their exact postimages restore tool-agnostic admissible routing while preserving
independence and evidence requirements: *"`TOOL_UNAVAILABLE != WORK_SEMANTICALLY_INVALID`"*,
*"independent verification may use any authorized available route that preserves
independence, exact-byte identity, read-only behavior, attributable output, and complete
transport."*

See
[`../../../examples/aice/aice-603-governance-induced-service-unavailability.json`](../../../examples/aice/aice-603-governance-induced-service-unavailability.json).
The example encodes the negative controls (ordinary outage, no admissible alternative,
uniquely-required dependency, transient transport failure) as non-triggering.

## Related codes

- [`AICE-602`](./AICE-602.md) — a gateway that makes the wrong authority/context decision,
  versus an existing capability withheld by an unnecessary broken governance dependency
  here.
- [`AICE-613`](./AICE-613.md) — installing the required mutation capability depends on that
  same missing capability (a self-hosting deadlock), versus an admissible alternative that
  exists but is forbidden here.
- [`AICE-614`](./AICE-614.md) — an infrastructure failure fabricated into a semantic
  verdict, versus an infrastructure-unavailable dependency correctly classified but wrongly
  made mandatory over an available alternative here.
