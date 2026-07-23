# AICE-602 — Gateway Authority Context Failure

**Unofficial draft (AICE v0.8.0).**

## Canonical identifier

`AICE-602`

## Human-readable alias

`HTTP 602 — Bad Gateway`

"Bad Gateway" is a non-normative pun on the conventional HTTP 502 label. It carries no
relation to the standardized meaning of HTTP 502 beyond the joke, and asserts no IETF,
HTTP, RFC, standards-body, or industry-standard status.

## Intent

Catch the case where a gateway, safety layer, policy engine, model-access layer, approval
service, or other authoritative control makes a security-relevant decision primarily from
the shape or content of a request, while failing to establish, preserve, or consume the
**actor context** required to interpret that request correctly.

The defining defect is **not** an incorrect content classification. The defect is that
content shape was used as a substitute for the actor, authority, purpose, provenance,
target, or operational context the decision actually required.

Canonical machine name: `GATEWAY_AUTHORITY_CONTEXT_FAILURE`.

Canonical law:

```
PAYLOAD_SIMILARITY
≠
ACTOR_EQUIVALENCE
```

Canonical relation:

```
SAME_PAYLOAD
+ DIFFERENT_ACTOR
+ DIFFERENT_AUTHORITY
= DIFFERENT_SECURITY_MEANING
```

Canonical trust rule:

```
ACTOR_AUTHORITY_ASSERTED_IN_PROMPT
≠
ACTOR_AUTHORITY_ESTABLISHED
```

Canonical design principle:

> A security gateway must evaluate the authority and bounded purpose of the actor, not
> merely the vocabulary of the request.

## Canonical machine form

```
GATEWAY_DECISION_REQUIRED
SECURITY_RELEVANT_ACTION_PRESENT
ACTOR_AUTHORITY_CONTEXT_REQUIRED
LEGITIMATE_AUTHORITY_STATUS_EXTERNALLY_ESTABLISHED
ACTOR_CONTEXT_UNAVAILABLE_IGNORED_OR_NOT_CONSUMED
PAYLOAD_OR_OPERATION_SHAPE_USED_AS_AUTHORITY_PROXY
AUTHORITATIVE_DECISION_APPLIED
AUTHORIZED_ACTION_DENIED
  OR UNTRUSTED_ACTION_ADMITTED
OPERATIONAL_EFFECT_PRESENT
WORKFLOW_EFFECT = STATE_UNCHANGED
WORKFLOW_EFFECT = BLOCK_ACCEPTANCE
```

The required actor context may include: authenticated identity; organizational role;
delegated authority; declared and authorized purpose; target identity; incident or
operational state; provenance of the artifact; requested capability; permitted action
class; execution environment; bounded scope; operator authorization; emergency or
incident-response status.

## Actor-context failure modes

AICE-602 has two normative subforms. Either is sufficient.

### A. `CONTEXT_AVAILABLE_NOT_CONSUMED`

The gateway or surrounding system possesses authenticated actor, role, target, purpose,
or incident-state information, but the decision path does not consume it materially.

```
AUTHORITY_CONTEXT_AVAILABLE = true
AUTHORITY_CONTEXT_CONSUMED  = false
```

### B. `CONTEXT_REQUIRED_BUT_NOT_ESTABLISHABLE`

The system relies on the gateway for an authorized operational class (such as incident
response), but provides no trusted mechanism through which that gateway can establish or
receive the required authority context.

```
AUTHORIZED_OPERATION_CLASS_REQUIRED = true
TRUSTED_AUTHORITY_CHANNEL_AVAILABLE = false
CONTENT_ONLY_CLASSIFICATION_APPLIED = true
```

Do not require a responder to establish authority merely by typing "I am an authorized
incident responder." Prompt prose is not authentication. A model's self-declared role is
not an IAM credential.

## Two decision branches

At least one branch must be established. Both are **not** required.

### Authorized-denial branch

Requires evidence that:

1. the actor was independently established as authorized for the bounded operation;
2. the requested operation was within that authority;
3. the payload, artifact, or command had a legitimate defensive, diagnostic, forensic,
   recovery, testing, or maintenance purpose;
4. the gateway denied or materially obstructed the operation;
5. the denial was caused by content or operation shape without adequate actor, authority,
   purpose, provenance, target, or environment context;
6. the denial affected a real operational path.

Representative classes: incident responder analyzing exploit payloads; malware analyst
examining samples; security engineer reproducing a vulnerability in an isolated lab;
maintainer inspecting a malicious package; forensic operator processing C2 artifacts;
administrator executing an authorized recovery command; safety evaluator testing a bounded
prohibited-content detector; medical or industrial responder examining hazardous
instructions inside a controlled domain.

The fact that content is dangerous does not by itself make the denial erroneous. The
question is whether the gateway correctly consumed the authority and bounded operational
context its claimed use case required.

### Untrusted-admission branch

Requires evidence that:

1. the actor lacked authority for the protected operation;
2. the action was security-relevant;
3. the gateway admitted or enabled it;
4. admission occurred because request shape, superficial classification, trusted
   vocabulary, synthetic evaluation labels, or another content proxy was used instead of
   the missing authority context;
5. an authoritative or external effect became reachable or occurred.

Do not infer this branch merely because another system elsewhere admitted an offensive
actor. The admitting gateway and its decision path must be identified. Do not merge
separate providers, products, deployments, or control planes into one event because the
comparison is memorable.

### Full authority inversion

A **full authority inversion** is a stronger AICE-602 form in which both branches are
independently established:

```
AUTHORIZED_ACTION_DENIED   = true
UNTRUSTED_ACTION_ADMITTED  = true
```

The decisions must originate from:

- the same gateway and policy boundary; or
- separate decision paths whose relevant authority semantics are independently proven
  equivalent.

```
FULL_AUTHORITY_INVERSION =
  AUTHORIZED_ACTION_DENIED
  AND UNTRUSTED_ACTION_ADMITTED
  AND COMPARABLE_GATEWAY_SEMANTICS_ESTABLISHED
```

Full inversion is **sufficient** for AICE-602 but is **not required**. Two unrelated
providers, products, deployments, or control planes must not be combined into a
full-inversion claim merely because one admitted an offensive path and another denied a
defensive path. Absent `SAME_GATEWAY = true` or
`POLICY_EQUIVALENCE_FOR_RELEVANT_DECISION = established`, such a pairing is only a
`SEPARATE_CONTROL_PLANE_CONTRAST` — a powerful industry asymmetry, but not one inverted
gateway. Full inversion, like every AICE predicate, must be earned by observation.

Compact branch matrix:

| Authorized path | Unauthorized path | Result |
|---|---|---|
| Denied | Not examined | AICE-602: authorized denial |
| Not examined | Admitted | AICE-602: untrusted admission |
| Denied | Admitted (same/equivalent gateway) | AICE-602: full authority inversion |
| Allowed | Denied | Normal control directionality (no incident) |

Where an implementation wishes to record the stronger form without changing the schema, it
may carry a derived, non-schema-constraining marker such as
`authority_context_failure_mode = FULL_AUTHORITY_INVERSION` inside `code_details`.

## Why AICE-602 is foundational

AICE-604 and later codes generally assume an actor has already reached a path where
objects, execution, deployment, controls, verification, or evidence can be evaluated.
AICE-602 concerns an **earlier** trust boundary:

```
actor
  -> identity and authority
  -> gateway decision
  -> permitted observation or action
  -> downstream evidence
```

When authority context is lost at this gateway, every downstream control operates on a
misclassified principal. The lower number expresses the position of the failure in the
causal stack, **not** the attractiveness of "602 Bad Gateway" and **not** a universal
severity ranking. Do not claim that all low-number incidents are more severe than all
later incidents. The numbering expresses conceptual placement only.

## Trigger condition

AICE-602 requires evidence supporting all applicable elements:

1. a gateway or policy decision controlled a security-relevant path;
2. a concrete actor and action can be identified;
3. the actor's authorization status is independently established;
4. the action's bounded purpose, target, and environment are established;
5. correct interpretation required actor, authority, purpose, provenance, target, or
   incident-state context;
6. that context was unavailable through the gateway interface, lost before decision,
   ignored, not consumed, collapsed into a generic actor class, or replaced by content
   shape;
7. the gateway used payload vocabulary, command shape, artifact type, synthetic task
   label, or another content proxy as a substitute for authority;
8. the gateway issued an authoritative admit or deny decision;
9. the decision was incorrect relative to the independently established authority and
   bounded purpose;
10. the decision affected a real operational path, protected state, recovery capability,
    evidence-production path, or acceptance claim;
11. the workflow lacks evidence to accept the gateway as correctly governing the claimed
    operational class.

For authorized denial: `AUTHORIZED_ACTION_DENIED = true`. For untrusted admission:
`UNTRUSTED_ACTION_ADMITTED = true`. At least one branch must be established; both are not
required.

### Canonical representative scenario

```
AUTHORIZED_RESPONDER
  -> REAL_ATTACK_ARTIFACTS
  -> CONTENT-ONLY SAFETY CLASSIFICATION
  -> RESPONDER TREATED AS ATTACKER
  -> FORENSIC PATH DENIED
  -> RECOVERY PATH SWITCHED
  -> STATE_UNCHANGED
  -> BLOCK_ACCEPTANCE
```

An organization is responding to an active compromise; an authenticated incident responder
must analyze real exploit commands, malicious payloads, and C2 artifacts; the hosted
analysis gateway classifies the payload as offensive cyber content; the gateway cannot
establish or consume the responder's authority and bounded forensic purpose; the analysis
request is blocked; the organization moves to a separately controlled local analysis path;
acceptance of the hosted path as suitable for incident response is blocked. The incident
does not require proof that the same gateway admitted the original attacker — authorized
defensive denial alone can satisfy AICE-602.

## Required observations

Evidence classes include: authenticated actor identity; role or authority source;
delegated authorization; incident declaration; bounded purpose; target allowlist;
environment identity; gateway request envelope; gateway policy input; fields actually
consumed by the decision; omitted or discarded context; gateway response; denial or
admission reason; audit record; external effect; alternate recovery route; proof that the
operation was analysis rather than execution; proof that authority was not merely
self-asserted in prompt text.

Strong evidence may include: IAM or operator authorization records; gateway schemas showing
that no actor-context field exists; traces showing actor fields existed upstream but were
absent at the policy decision; policy logs showing classification based only on content
category; a refusal explicitly treating forensic payloads as malicious generation; a
controlled comparison using the same artifact under authenticated-responder and
unauthenticated-actor contexts; evidence that a local bounded responder route successfully
analyzed the same artifact class; a real admission caused by reliance on a synthetic task
label or payload vocabulary; independent readback of the denied or admitted operational
effect.

The presence of the words "security," "forensics," "authorized," or "responder" inside a
prompt is not authority evidence.

## Missing-evidence condition

An authoritative gateway decision governed a real actor, but the actor, authority, purpose,
provenance, target, or incident-state context required to interpret the request correctly
was unavailable, ignored, collapsed, or replaced by content shape — so the decision cannot
be accepted as correctly governing the claimed operational class, and no evidence
establishes that it did.

## False-positive guards

AICE-602 MUST NOT fire when:

- actor authority is merely self-declared;
- no authenticated or externally established authority exists;
- the requested action falls outside the actor's authorization;
- the target is outside the authorized scope;
- the operation requests live execution when only inspection is permitted;
- the gateway correctly separates payload interpretation from payload execution;
- an absolute invariant prohibits the action regardless of actor;
- the provider does not claim to support the required defensive workflow;
- a trusted responder lane exists but the operator did not use it;
- the failure is transport, timeout, authentication outage, malformed output, or runtime
  unavailability (that is AICE-614 territory, not AICE-602);
- workflow blocking is caused by missing authority evidence and the result is honestly
  classified as `AUTHORITY_NOT_ESTABLISHED`;
- the gateway consumes authenticated actor context and makes a policy decision consistent
  with that context;
- two unrelated control planes are compared without proof of equivalence;
- an offensive evaluation runs with reduced safeguards under one system while a defensive
  request is denied by a different system;
- an attacker bypasses the control rather than receiving an authority-blind admission;
- an auditor transfers path evidence across actors without a real gateway decision;
- the only evidence is a LinkedIn post, screenshot, model summary, or memorable analogy;
- the only evidence is that an open-weight model completed a task a hosted model refused;
- no operational or authoritative effect occurred;
- the incident concerns only content-policy preference rather than authority context.

Important rules:

```
SAME_PAYLOAD          ≠ SAME_ACTOR
SAME_PAYLOAD          ≠ SAME_AUTHORITY
SELF_DECLARED_INTENT  ≠ AUTHENTICATED_PURPOSE
DIFFERENT_PROVIDER_DECISIONS ≠ ONE_INVERTED_GATEWAY
```

AICE-602 is not a general complaint that a model refused a request. It requires a mismatch
between externally established authority and bounded purpose on one side, and the
authoritative gateway decision on the other.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

A detected AICE-602 incident MUST block acceptance of claims such as: gateway correctly
enforces role-aware policy; hosted path supports incident response; actor-sensitive
governance is operational; control distinguishes authorized analysis from hostile
execution; trusted-access routing works; defensive liveness is established.

In the untrusted-admission branch, the external protected state may already have changed.
`WORKFLOW_EFFECT = STATE_UNCHANGED` means the AICE acceptance workflow MUST NOT advance; it
does **not** claim the external system necessarily remained unchanged. Retryability:
`requires_new_evidence`.

## Remediation

Remediation is **not**: disable all safety controls for responders; trust the phrase "I am
an incident responder"; add a magic word such as `FOR_FORENSICS`; whitelist an entire user
without bounded scope; expose unrestricted code execution; pass raw credentials through
prompt text; treat every enterprise account as trusted; weaken content protections
globally; deploy an "uncensored" model without isolation; route around policy without
recording the authority boundary; classify refusal as proof the payload was hostile;
combine two different gateways into a fictional inversion; declare open weights inherently
safe; or declare hosted models inherently unusable.

Required remediation establishes a bounded trusted path:

```
authenticated actor
  -> explicit delegated authority
  -> bounded purpose
  -> target and environment scope
  -> capability-specific permission
  -> isolated analysis lane
  -> payload interpretation separated from payload execution
  -> gateway consumes authority context
  -> authoritative decision
  -> action or denial
  -> independent postcondition readback
```

Acceptable mechanisms may include: a trusted responder access program; authenticated
incident-response roles; signed authorization envelopes; short-lived scoped credentials;
target allowlists; isolated malware-analysis environments; read-only artifact inspection;
static parsing before execution; bounded tool permissions; content detonation sandboxes;
self-hosted open-weight defensive models inside the operator's perimeter; operator-
authorized break-glass routes; hardware- or service-backed responder identity; complete
decision and execution receipts.

Self-hosting alone is not sufficient. An open-weight model without authority boundaries,
isolation, audit, and bounded tools can create a different failure class.

Acceptance requires a real control run showing:

1. authenticated responder identity reached the gateway;
2. bounded defensive purpose and target scope reached the gateway;
3. the gateway consumed those fields;
4. the same artifact class could be inspected without granting unrestricted execution;
5. an unauthorized actor remained denied;
6. invalid or expired authorization failed closed;
7. policy and execution decisions remained causally bound;
8. the authorized action produced an independently observed postcondition;
9. no prompt-only role assertion was accepted as authority.

## Distinction from adjacent codes

### AICE-610 — Control Exists, Enforcement Not Found

- AICE-610: the control exists; the real executor is not causally bound to it; the
  protected action can bypass the decision — *the guard can be bypassed*.
- AICE-602: the gateway decision is actually enforced, but is defective because the
  required actor/authority context was unavailable, ignored, collapsed, or replaced by
  content shape — *the guard is standing at the gate but checks the weapon and forgets to
  check who is holding it*.

The two may coexist. Do not use AICE-602 as a replacement for a proven enforcement bypass.

### AICE-612 — Actor Path Substitution

- AICE-612: an audit tests one actor's path and asserts a conclusion about another actor's
  path without proving equivalence — *the auditor reasoned about the wrong actor*.
- AICE-602: a real gateway makes an authoritative decision that fails to consume the actor
  distinction required to interpret the request — *the gateway governed the real actor
  without understanding its authority context*.

AICE-612 transfers evidence across actor scope; AICE-602 collapses authority context inside
the decision path itself.

### AICE-614 — Infrastructure Failure as Semantic Verdict

- AICE-614: no valid semantic or policy verdict exists; an infrastructure failure
  impersonates one — *the gateway never issued a valid opinion, but one was fabricated*.
- AICE-602: a real gateway or policy decision exists but is semantically authority-blind —
  *the gateway issued a real decision using the wrong security ontology*.

A timeout, unavailable provider, malformed response, or transport failure alone MUST NOT
satisfy AICE-602.

### Not a content-safety disagreement

AICE-602 is not emitted merely because a user dislikes a safety policy, a model refuses
dangerous content, a provider is stricter than the operator prefers, an actor claims benign
intent without authentication, a prohibited action remains prohibited for all actors, a
responder requests real execution when only static analysis was authorized, or the provider
does not claim to support the relevant operational class.

## Non-normative explanatory model: Bad Gateway

A conventional bad gateway fails to connect one system to another. An AICE-602 gateway may
be technically healthy, reachable, and consistently enforced while interpreting security
direction incorrectly, because it evaluates the request vocabulary without the authority
context required to understand the actor.

```text
AUTHORIZED_RESPONDER
→ "This request violates policy."

UNAUTHENTICATED_ACTOR
→ decision not established by this example

GATEWAY_HEALTH
→ healthy

AUTHORITY-AWARE GOVERNANCE
→ not established
```

The unauthenticated actor is shown as `decision not established`, not as admitted; the
admission branch is not proven by this example. This section is non-normative.

## Non-normative explanatory model: the weapon and the firefighter

A guard inspects an axe. The guard sees a dangerous object but does not establish whether
the person holding it is an arsonist entering a building or an authenticated firefighter
responding to an active fire. The guard arrests the firefighter because the axe resembles a
weapon. The object classification may be correct. The authority classification is absent.

> The guard checked the weapon and forgot to check who was holding it.

> A firefighter carrying an axe is not an arsonist.

This metaphor does not imply that all authorized responders should be allowed to perform
all actions. The firefighter remains bounded by role, target, incident, and capability.
Non-normative.

## Non-normative explanatory model: cybernetic autoimmunity

A security system may correctly recognize dangerous syntax while attacking the authorized
mechanism intended to inspect or neutralize that danger.

```text
THREAT_SYNTAX_RECOGNIZED       = true
RESPONDER_AUTHORITY_RECOGNIZED = false
DEFENSIVE_ACTION_DENIED        = true
```

The system has classified vocabulary, not risk.

> An immune system that evaluates syntax instead of authority may attack the responder
> while leaving the threat operational.

This does not state that the gateway protected, assisted, or admitted the attacker unless
that branch is separately proven. "Cybernetic Autoimmunity" is not a new code or canonical
machine name. Non-normative.

## Non-normative note: the L0 crowbar

When a hosted analysis path could not process the attack artifacts, the operator used an
open-weight model on infrastructure under its own control. The lesson is not "remove all
safeguards." The lesson is "critical responders need an authority-bearing, bounded analysis
path that remains operational during the incident."

> The hosted gateway blocked the forensic kit, so the operator reached for the L0 crowbar.

The crowbar must still live inside isolation, scoped authority, tool boundaries, evidence
capture, and independent readback. Do not equate "local" with "safe." Non-normative.

## Field maxims (non-normative)

> The guard checked the weapon and forgot to check who was holding it.

> A firefighter carrying an axe is not an arsonist.

> The same payload does not imply the same authority.

> A gateway that cannot distinguish an attacker from an incident responder has not
> classified risk. It has classified vocabulary.

> Prompt text is not an identity credential.

> The model said "I am authorized" is not IAM.

> Content classification is not authority verification.

> A healthy gateway can still be directionally wrong.

> The gateway is healthy. It just blocks the fire brigade.

> Do not build a fence that protects the threat from the responder.

> An immune system that evaluates syntax instead of authority may attack the responder
> while leaving the threat operational.

These maxims are memorable rationale only. They MUST NOT leak into registry machine fields,
schema constraints, normative trigger names, or historical evidence claims.

## Example

`VERIFIED_PUBLIC_HISTORICAL_SCOPE` (narrow) for the authorized-denial predicate; all other
detail is `REPRESENTATIVE`.

Two official Hugging Face sources — the July 2026 security-incident disclosure and Jeff
Boudier's July 2026 self-hosting guide — currently support a single narrow statement:

> A hosted forensic-analysis path was blocked because its safety layer could not
> distinguish an authorized incident responder processing real attack artifacts from an
> attacker. The operator switched to a locally controlled GLM 5.2 path.

The sources establish subform `CONTEXT_REQUIRED_BUT_NOT_ESTABLISHABLE`: the commercial-API
guardrails had no trusted way to establish the responder's authority and classified on
content. They do **not** name which commercial provider refused, do not establish that a
signed actor-context field was supplied and ignored, do not establish that the same gateway
admitted the original attacker, and therefore establish neither a full authority inversion
nor a single inverted gateway. The offensive-evaluation contrast reported elsewhere is a
`SEPARATE_CONTROL_PLANE_CONTRAST`; its primary source was not independently retrievable in
this build, so it is not encoded as fact.

See
[`../../../examples/aice/aice-602-gateway-authority-context-failure.json`](../../../examples/aice/aice-602-gateway-authority-context-failure.json).
The example asserts no provider identity, request id, timestamp, model call, payload,
credential, hash, commit, gateway log, IAM record, exact refusal text, or same-payload
comparison as fact.

## Related codes

- [`AICE-610`](./AICE-610.md) — a control the executor can bypass (runtime enforcement),
  versus an enforced-but-authority-blind gateway decision here.
- [`AICE-612`](./AICE-612.md) — invalid cross-actor inference by an auditor, versus an
  authority-context collapse inside a real gateway decision here.
- [`AICE-614`](./AICE-614.md) — a fabricated verdict where no valid review exists, versus a
  real gateway decision made with the wrong security ontology here.
