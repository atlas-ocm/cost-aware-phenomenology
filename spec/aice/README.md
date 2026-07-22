# AICE 6xx — Normative Specification

**Unofficial draft specification, version 0.3.0. Status: Draft / Research-only.**

AICE (AI Chaos Engineering) is a proposed incident taxonomy for *evidence-boundary
failures* in AI-assisted workflows. This document is the normative reference for the
AICE-604 through AICE-611 code set and the machine-readable incident envelope
([`incident.schema.json`](./incident.schema.json)).

This is **not** an HTTP status-code extension, **not** an IETF standard, and **not**
evidence of external adoption. The `HTTP 6xx` labels are memorable human-readable
aliases only. The canonical identifiers are `AICE-604` … `AICE-611`.

AICE 6xx is the evidence-gated incident taxonomy within the broader **AI Chaos Control
Protocols** series — deterministic control protocols for probabilistic software. That
series name is a non-normative parent-series label; it is not an expansion of the
acronym `AICE` and does not change the machine namespace, which remains `AICE`.

The key words **MUST**, **MUST NOT**, **SHOULD**, and **MAY** in this document are to
be interpreted in their ordinary RFC-style normative sense, with the explicit caveat
that this is an unofficial draft and imposes no obligation outside a system that
chooses to adopt it.

---

## 1. Purpose

AICE classifies discrepancies between two states of a claimed unit of work:

- **narrative_state** — what an agent, verifier, orchestrator, report, or model
  *claims* occurred.
- **physical_state** — what is *supported by* observable events, independently
  readable artifacts, process receipts, state inspection, or verified postconditions.

An AICE incident is emitted when the narrative asserts completion but the required
observable event, evidence chain, or physical postcondition is absent or contradictory.

Canonical principle:

> No text is an event.
> No declared hash proves that bytes exist.
> No PASS closes a defect without a verified postcondition.

## 2. Core rule

Model-generated prose **MUST NOT** directly mutate workflow state.

Workflow state **MAY** advance only when the required observable event and
postcondition have been verified. Where verification is absent, the workflow **MUST**
treat the claim as unproven rather than complete.

## 3. Incident contract

An AICE incident is a structured envelope. The following fields form the common
contract; [`incident.schema.json`](./incident.schema.json) is authoritative for the
machine-readable shape.

| Field | Requirement | Meaning |
|---|---|---|
| `code` | MUST | Canonical identifier, one of `AICE-604`…`AICE-611`. Unknown codes MUST be rejected. |
| `title` | MUST | Human-readable code title (see the registry). |
| `spec_version` | MUST | AICE spec version (`0.3.0`). |
| `timestamp` | MAY | ISO 8601 emission time. Omit rather than fabricate. |
| `claim` | MUST | The narrative claim under scrutiny. |
| `narrative_state` | MUST | `COMPLETE` \| `PARTIAL` \| `ABSENT`. |
| `physical_state` | MUST | `OBSERVED` \| `UNOBSERVED` \| `CONTRADICTED` \| `NOT_APPLICABLE`. |
| `observed_evidence` | MUST | Array of evidence actually observed (MAY be empty). |
| `missing_evidence` | MUST | Array of required-but-absent or contradictory evidence. |
| `workflow_effect` | MUST | Array of effects; MUST contain `STATE_UNCHANGED`. |
| `required_action` | MUST | Remediation that would resolve the incident. |
| `retryability` | MUST | How the action could be resolved (never by repetition alone). |
| `producer` | MAY | Producing actor identity, when known. |
| `verifier` | MAY | Verifying actor identity, when relevant. |
| `independence` | MAY | Independence assessment of the verifier (AICE-608). |
| `artifact` | MAY | Declared artifact whose materialization is in question (AICE-604). |
| `code_details` | MAY | Code-specific extra structure. |
| `notes` | MAY | Free-text notes. |

### 3.1 State enums

```
narrative_state:  COMPLETE | PARTIAL | ABSENT
physical_state:   OBSERVED | UNOBSERVED | CONTRADICTED | NOT_APPLICABLE
```

### 3.2 Workflow effects

The default workflow behavior for an **unresolved** AICE incident **MUST** be:

```
STATE_UNCHANGED
```

Every incident envelope **MUST** carry `STATE_UNCHANGED` in `workflow_effect`. A
higher-level workflow **MAY** additionally apply one or more of:

```
BLOCK_ACCEPTANCE | BLOCK_PROMOTION | BLOCK_RELEASE | BLOCK_DEPLOYMENT | REQUEST_EVIDENCE
```

These blocking effects are additive and do not replace `STATE_UNCHANGED`.

## 4. Resolution semantics

When an AICE incident is emitted:

- workflow state **MUST** remain unchanged;
- promotion, release, deployment, or acceptance **MUST** remain blocked where the
  corresponding blocking effect applies;
- remediation **MUST** request the missing evidence or materialize the missing state;
- additional model agreement alone **MUST NOT** resolve the incident.

The core workflow:

```
CLAIM
  -> REQUIRED EVIDENCE
  -> POSTCONDITION CHECK
  -> ACCEPT  (postcondition observed)
     or
  -> AICE INCIDENT  (postcondition absent/contradictory; STATE_UNCHANGED)
```

## 5. False-positive discipline

AICE is a boundary taxonomy, not a suspicion generator. Each code carries explicit
false-positive guards (see [`codes/`](./codes/)). In particular:

- an explicitly documented no-op — a metadata-only release, a declared no-op
  deployment — is **not** an incident;
- a trustworthy external receipt (e.g. a CI record) **MAY** satisfy an evidence
  requirement even when the local process was not directly observed;
- a small diff is **not**, by itself, grounds for an incident.

## 6. Registry and codes

- [`registry.json`](./registry.json) — compact machine-readable registry of the code
  set, titles, trigger summaries, default effects, and retryability.
- [`codes/`](./codes/) — one normative Markdown document per code:
  - [`AICE-604`](./codes/AICE-604.md) — Hash Exists, Reality Not Found
  - [`AICE-605`](./codes/AICE-605.md) — Release Exists, Implementation Not Found
  - [`AICE-606`](./codes/AICE-606.md) — PASS Exists, Test Run Not Found
  - [`AICE-607`](./codes/AICE-607.md) — Deployment Exists, Production Not Found
  - [`AICE-608`](./codes/AICE-608.md) — Verification Exists, Independence Not Found
  - [`AICE-609`](./codes/AICE-609.md) — Consensus Exists, Evidence Not Found
  - [`AICE-610`](./codes/AICE-610.md) — Control Exists, Enforcement Not Found
  - [`AICE-611`](./codes/AICE-611.md) — Operational Reachability Substitution

For v0.3 the code set is exactly `AICE-604` … `AICE-611`.

## 7. Relationship to CAP

CAP (Cost-Aware Phenomenology) constrains recommendations and transitions through
telemetry, cost, risk, and operator admissibility. AICE is an **applied incident
taxonomy** for evidence-boundary failures in AI-assisted workflows. AICE is not a new
core phenomenological claim; it is a practical extension consistent with CAP's
machine-checkable, telemetry-gated approach. It complements — and does not replace —
access control, sandboxing, transactions, and ordinary observability.
