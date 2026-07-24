# AICE-613 — Self-Hosting Mutation-Shape Deadlock

**Unofficial draft (AICE v0.9.0).**

## Canonical identifier

`AICE-613`

## Human-readable alias

`HTTP 613 — Self-Hosting Mutation-Shape Deadlock`

Short public alias (non-normative): **Self-Hosting Patch-Shape Deadlock**. The
public alias is a memorable label only; the normative title and definition use
"Mutation-Shape" because the defect is representation-agnostic and is not limited
to source-code patches.

## Intent

Catch the case where a system must modify an existing artifact, but its only
authorized mutation protocol requires reproducing or transporting the *complete*
artifact rather than a bounded representation of the intended state delta; the
required full-object payload exceeds an observed hard capacity; no delta-capable
mutation mechanism is reachable; and the system cannot bootstrap one, because
adding or enabling a delta mechanism requires modifying — through the same
insufficient full-object protocol — the mutation mechanism itself or another
artifact that also exceeds the available capacity.

The defining defect is a self-hosting deadlock between:

1. the mutation representation currently available; and
2. the mutation representation required to upgrade that mechanism.

This is not merely "the file is large" or "the model ran out of tokens." It is a
recursive dependency in which escaping the capacity limitation requires a mutation
form that can only be installed by first escaping the same limitation.

Canonical machine name: `SELF_HOSTING_MUTATION_SHAPE_DEADLOCK`.

## Canonical machine form

```
REQUESTED_DELTA_SIZE_SMALL
ONLY_AUTHORIZED_MUTATION_FORM_FULL_OBJECT
MUTATION_COST_SCALES_WITH_TARGET_OBJECT_SIZE
REQUIRED_MUTATION_PAYLOAD_EXCEEDS_OBSERVED_CAPACITY
ALTERNATE_DELTA_PATH_ABSENT_OR_UNREACHABLE
MUTATION_MECHANISM_UPGRADE_REQUIRES_SAME_INSUFFICIENT_FORM
SELF_HOSTING_MUTATION_PATH_REACHABLE = false
WORKFLOW_EFFECT = STATE_UNCHANGED
```

Canonical compact form:

```
DELTA_FITS
FULL_REPLACEMENT_DOES_NOT_FIT
PATCH_SUPPORT_REQUIRED
PATCH_SUPPORT_CANNOT_BE_INSTALLED_WITHOUT_PATCH_SUPPORT
```

Canonical mathematical relation:

```
REQUESTED_DELTA_SIZE   << TARGET_ARTIFACT_SIZE
MUTATION_PAYLOAD_COST  ≈  TARGET_ARTIFACT_SIZE
MUTATION_PAYLOAD_COST  >  AUTHORIZED_CAPACITY
therefore
REQUIRED_STATE_TRANSITION_NOT_MATERIALIZABLE
```

## Field maxim (non-normative)

Canonical normative design principle:

> Mutation cost should scale with the intended state delta, not with the absolute
> size of the target artifact.

Non-normative short maxim:

> A tiny delta must not require a universe-sized payload.

Secondary non-normative maxim:

> Knowing the fix is not the same as being able to materialize the transition.

Only the first statement is usable as a formal design principle; the remaining
formulations are memorable rationale and change no normative behavior.

## Core self-hosting predicate

AICE-613 requires **both** an immediate mutation-capacity defect and a
self-hosting bootstrap deadlock.

The immediate defect is:

- the requested logical change is bounded and materially smaller than the target
  artifact;
- the only authorized mutation representation requires reproducing the complete
  artifact;
- the complete payload cannot be emitted, transported, validated, or atomically
  applied within the observed capacity.

The self-hosting defect is:

- a more compact mutation primitive is required to escape the limitation;
- adding, activating, or routing execution through that primitive requires
  changing the current mutation implementation or another over-capacity artifact;
- that required bootstrap change must itself be expressed through the insufficient
  full-object mechanism;
- no separately authorized bounded bootstrap path is available.

Do **not** emit AICE-613 when only the immediate full-object limitation is proven
but the self-hosting bootstrap deadlock is not established. A large-file output
failure without the recursive upgrade dependency is a capacity or transport
defect, but not necessarily AICE-613.

## Canonical representative scenario

- a source file contains 1,500 lines;
- the required logical fix changes three lines;
- the agent writer supports only `WRITE_FILE(path, full_content)`;
- the authorized output or tool payload capacity can carry only ~800 lines or an
  equivalent byte/token bound;
- no `apply_patch`, range replacement, structured edit, AST edit, chunked atomic
  assembly, or equivalent delta mechanism is reachable;
- the full rewrite cannot be completed;
- adding `apply_patch` requires modifying the same oversized writer module using
  `WRITE_FILE(path, full_content)`;
- therefore the system cannot install the capability required to escape its own
  mutation limitation.

Compact representative trace:

```
operator requests 3-line fix
→ planner identifies correct 3-line delta
→ writer requires complete 1,500-line artifact
→ output ends before complete payload
→ atomic mutation is not materialized
→ patch-capable writer is proposed
→ writer upgrade itself requires complete oversized rewrite
→ self-hosting path remains unreachable
→ STATE_UNCHANGED
```

The model may correctly understand and describe the fix. That does not establish
that the transition can be materialized.

## Supported artifact classes

AICE-613 is **not** restricted to source-code files. The defect may apply to:

- source code;
- monolithic JSON configuration;
- workflow snapshots;
- serialized FSM definitions;
- policy bundles;
- generated manifests;
- large prompt templates;
- complete AST serialization;
- binary or encoded artifacts;
- infrastructure definitions;
- database migration bundles;
- model-routing tables;
- full-document APIs;
- any artifact whose mutation cost is coupled to its absolute size rather than the
  intended delta.

The code is representation-agnostic. The public alias may say "Patch-Shape," but
the normative title and definition use "Mutation-Shape."

## Why this is a distinct code

- `AICE-604` — a claimed artifact or materialized object is absent.
- `AICE-605` — a claimed implementation or release is absent.
- `AICE-606` — a PASS is claimed without an observed test or validator execution.
- `AICE-607` — publication, deployment, or production presence is claimed without
  independently observed presence or effect in the target environment.
- `AICE-608` — verification is claimed without sufficient verifier independence.
- `AICE-609` — consensus is substituted for evidence.
- `AICE-610` — a protective control exists and may validate, but the executor is
  not causally bound to it.
- `AICE-611` — validated components are substituted for an observed working
  end-to-end system.
- `AICE-612` — one actor's path evidence is transferred to another actor without
  independently established path equivalence.
- `AICE-613` — the required state delta is known and small, but the only
  authorized mutation representation scales with the complete target artifact and
  exceeds observed capacity; upgrading the mutation representation requires using
  that same insufficient representation.

Canonical distinction from `AICE-611`:

```
AICE-611: the authorized end-to-end path is unreachable or has not been observed
AICE-613: the first broken edge is specifically the self-hosting mutation
          representation — the system cannot express the bounded transition
          needed to upgrade its own mutation capability
```

`AICE-613` may be a causal contributor to `AICE-611`. If the end-to-end system is
operationally unreachable *because* of an AICE-613 deadlock, report the first
broken edge precisely rather than replacing the specific defect with only the
downstream unobserved postcondition.

Canonical distinction from `AICE-604`:

```
AICE-604: the claimed output artifact or bytes do not exist
AICE-613: the architecture makes materialization of the required mutation
          impossible within the current authorized path
```

A failed AICE-613 attempt may *subsequently* produce AICE-604 if the system claims
that a nonexistent rewritten artifact was created.

Canonical distinction from `AICE-606`:

```
AICE-606: PASS claimed without an observed test run
AICE-613: the mutation cannot be materialized through the available protocol
```

A system may emit both if it fails to produce the change and then falsely claims
that tests passed. Do not collapse co-occurring incident meanings, and do not
alter the incident-envelope cardinality merely to represent co-occurrence.

## Trigger condition

AICE-613 requires evidence supporting **all** of the following:

1. a concrete state transition or artifact mutation is required;
2. the intended logical delta is materially smaller than the target artifact;
3. the authorized mutation mechanism requires reproducing, transporting, or
   replacing the complete target artifact;
4. mutation payload cost therefore scales materially with the target artifact's
   absolute size rather than with the intended delta;
5. an observed hard capacity is lower than the required full-object mutation
   payload;
6. the full mutation cannot be emitted, transported, assembled, validated, or
   atomically applied through the authorized path;
7. no reachable delta-capable mutation mechanism exists;
8. a delta-capable mechanism is required to escape the limitation;
9. adding, enabling, or routing through that mechanism requires changing the
   mutation subsystem itself or another over-capacity artifact;
10. that bootstrap mutation must be expressed through the same insufficient
    full-object representation;
11. no separately authorized bounded bootstrap seam has been established;
12. the required state transition therefore remains unmaterialized.

The incident MUST NOT be emitted solely from estimates when the complete payload
has not been compared against an observed or contractually fixed capacity. Do not
treat a model's claim that it "will probably run out of tokens" as evidence.

## Required observations

Evidence classes:

- identity and size of the target artifact;
- exact or bounded representation of the requested logical delta;
- active mutation API or tool contract;
- evidence that the active contract requires full-object replacement;
- observed payload size required by that representation;
- observed model, transport, tool, or atomic-application capacity;
- runtime output truncation, rejected payload, incomplete stream, or equivalent
  materialization failure;
- absence or unreachability of a delta-capable mutation route;
- identity of the artifact or subsystem that must change to add delta support;
- evidence that this bootstrap artifact also exceeds the current mutation
  capacity;
- evidence that the same insufficient mutation form is required for the bootstrap;
- absence of a separately authorized bootstrap seam;
- observed unchanged target state after the failed attempt.

Strong evidence may include:

- a tool schema proving `WRITE_FILE(path, full_content)` is the only write
  operation;
- an exact payload or token estimate checked against a fixed tool/model limit;
- an incomplete generation or transport trace with no atomic apply;
- a full-object hash/readback proving the target remained unchanged;
- a source or call graph showing that adding patch support requires modifying the
  oversized writer module;
- an attempted writer upgrade failing for the same full-object capacity reason;
- a deterministic preflight calculation proving the required payload cannot fit;
- a runtime receipt showing the mutation was blocked before any partial
  destructive write;
- a negative probe confirming that no bounded patch path is registered or
  authorized.

A model narrative describing the patch is not evidence that the patch can be
materialized. A diff displayed in prose is not evidence that an executor can
consume it.

## Missing-evidence condition

A bounded mutation is required and its logical delta is known, but no observation
shows the transition being materialized through the authorized path: the
full-object payload exceeds an observed capacity, no delta-capable route is
reachable, the mutation-mechanism upgrade recursively requires the same
insufficient full-object form, no separately authorized bounded bootstrap exists,
and the target artifact remains unchanged.

## Partial write and atomicity

AICE-613 does **not** require a corrupted partial artifact. A correct fail-closed
implementation may reject the oversized full-object mutation before writing any
bytes. In that case:

```
TARGET_ARTIFACT_UNCHANGED = true
```

may be a successful *safety* postcondition even though the requested mutation
remains unreachable.

If an implementation partially overwrites or corrupts the target before the stream
terminates, that may constitute an *additional* atomicity or artifact-integrity
defect. Do not define partial corruption as necessary for AICE-613. The preferred
failure behavior is:

```
capacity preflight fails
→ no mutation begins
→ original artifact remains intact
→ workflow remains blocked
→ AICE-613 evidence is emitted
```

## False-positive guards

AICE-613 MUST NOT fire when:

- a reachable authorized `apply_patch`, unified diff, structured patch, range
  replacement, AST edit, or equivalent delta mechanism exists;
- the model or planner merely failed to discover an available patch tool;
- the full target artifact fits within the independently observed capacity;
- chunking is supported with deterministic ordering, complete assembly, integrity
  verification, and atomic application;
- a sequence of bounded authorized operations can safely materialize the delta;
- the task genuinely requires complete regeneration rather than a small delta;
- the capacity failure is caused only by a temporary network interruption,
  provider outage, transient rate limit, or retryable transport error;
- a different model or authorized execution lane with sufficient observed capacity
  is already reachable within policy and cost bounds;
- the artifact can be split into independently valid modules through an
  already-authorized path;
- a separately authorized operator bootstrap patch is available and the system
  does not claim autonomous self-hosting for this transition;
- the mutation mechanism can be upgraded by adding a small adjacent shim without
  modifying an over-capacity artifact;
- the target is large but the actual mutation payload is content-addressed or
  delta-sized;
- the only evidence is a theoretical future scaling concern with no current
  capacity violation;
- the system honestly reports the self-mutation path as blocked and does not claim
  autonomous completion.

Important distinction:

```
HUMAN_OR_EXTERNAL_OPERATOR_CAN_PATCH
≠
AUTONOMOUS_SELF_HOSTING_PATH_WORKS
```

The existence of an authorized external bootstrap operator may prevent the entire
system from being globally terminal. It does not prove that the claimed autonomous
self-repair path works.

## Severity and scope

Not every AICE-613 incident is globally fatal. Canonical scope:

```
TERMINAL_FOR_CURRENT_AUTHORIZED_SELF_MUTATION_PATH
```

Severity depends on the claimed capability and available bootstrap routes, e.g.:

- blocking for an autonomous self-maintenance claim;
- blocking for an agent that promises unattended repository evolution;
- degraded but recoverable when an authorized operator bootstrap exists;
- non-blocking for a read-only advisory system that never claims mutation
  capability.

This taxonomy introduces no new severity enum; use existing registry terminology.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

The requested mutation MUST NOT be marked `COMPLETE`, `APPLIED`, `SELF_REPAIRED`,
`EVOLVED`, `PATCHED`, `VERIFIED`, or `RELEASED` while the mutation transition
remains unmaterialized. Retryability: `requires_new_evidence` — retry only after a
bounded mutation path has been introduced or discovered, capacity has been
materially changed and independently observed, a separately authorized bootstrap
has been applied, or the target has been safely decomposed.

## Remediation

Remediation is **not**:

- increase `max_output_tokens` and hope;
- retry the same full rewrite repeatedly;
- ask another model to reproduce the same complete artifact;
- split the model response into arbitrary chunks without deterministic atomic
  assembly;
- stream directly into the live target and accept partial content;
- lower validation standards;
- disable integrity checking;
- grant an untrusted proposer raw filesystem access;
- claim success because the intended three-line patch appeared in prose;
- create a synthetic small-file demonstration;
- make the target slightly smaller while retaining the same linear mutation
  topology.

Increasing capacity may be a valid *temporary* measure only when it is bounded,
observed, policy-authorized, and sufficient for the actual target. It does not
remove the architectural scaling defect if mutation cost remains coupled to
absolute artifact size.

Required remediation is a bounded bootstrap seam:

```
bounded trusted bootstrap
→ introduce or expose a delta-capable mutation primitive
→ bind the real executor to that primitive
→ apply one real small mutation through the new authorized path
→ verify exact preimage and postimage
→ run required validators and tests
→ independently read back the target artifact
→ preserve a durable receipt of the transition
```

Acceptable delta-capable mechanisms may include: deterministic range replacement
with an exact expected preimage; unified diff with bounded context and strict apply
failure; AST-addressed edits; JSON Patch or equivalent structured mutations;
content-addressed chunk replacement; transactionally assembled chunks followed by
integrity verification and atomic swap; a minimal adjacent shim that introduces a
bounded mutation route; an explicitly authorized external bootstrap patch; or safe
decomposition of the monolith into independently mutable modules.

Every remediation path must preserve authority boundaries, integrity checks,
atomicity, bounded payloads, fail-closed behavior, exact readback, and independent
postcondition verification. Acceptance requires evidence that:

1. the new mutation primitive is reachable from the real authorized entrypoint;
2. mutation payload size now scales with the intended delta or a bounded local
   region rather than the complete target artifact;
3. the previous over-capacity full-object path is no longer required for the
   demonstrated transition;
4. an invalid preimage or invalid patch fails closed;
5. an interrupted mutation does not corrupt the live target;
6. a real small delta is successfully applied to a previously blocking target;
7. exact changed ranges or structured fields are independently read back;
8. required tests and validators run against the actual post-mutation artifact;
9. the change produces a durable receipt binding target identity, preimage,
   intended delta, mutation mechanism, result, postimage, and validation outcome.

A synthetic tiny-file patch is insufficient if the claimed defect concerned a large
self-hosting artifact.

## Relation to self-hosting and evolution

AICE-613 is especially important for systems claiming autonomous self-repair,
self-modification, autonomous software evolution, automatic tool creation,
autonomous skill evolution, repository-scale coding, or unattended architecture
migration.

A system does not demonstrate self-hosting merely because it can generate a
complete small file, describe a patch, propose a new mutation API, edit toy
fixtures, or modify artifacts below its current full-rewrite threshold.
Self-hosting requires the system to modify the mechanisms that constrain its own
future mutation behavior through an authorized and reachable path.

```
SELF_HOSTING_CLAIM
requires
SELF_MUTATION_PATH_REACHABLE_FOR_LIMITING_SUBSYSTEM
```

Not every general-purpose agent must be self-hosting. AICE-613 applies when
self-hosting, autonomous evolution, or autonomous repair is part of the claimed
capability.

## Non-normative explanatory model: The Generative Ouroboros

A system recognizes that full-object replacement does not scale and proposes a
patch-capable mutation mechanism. However, the patch mechanism lives inside an
artifact that can currently be changed only by full-object replacement. The system
therefore attempts to build the ladder required to escape the hole using a rope
shorter than the depth of the same hole.

Representative loop:

```text
FULL_REWRITE_LIMIT_REACHED
→ PATCH_SUPPORT_PROPOSED
→ PATCH_SUPPORT_MODULE_REQUIRES_FULL_REWRITE
→ FULL_REWRITE_LIMIT_REACHED
```

The system can describe the escape mechanism but cannot materialize the state
transition that installs it. This is the generative Ouroboros: the mutation
mechanism consumes its own capacity boundary while attempting to evolve beyond it.
"Generative Ouroboros" is not the normative incident name and not a separate AICE
code.

## Non-normative explanatory model: Generative Solipsism

A model may transform `I can describe the fix.` into `I can materialize the fix.`
These are different claims. Understanding a state delta does not prove that the
authorized system can emit, transport, apply, and verify the transition.

```text
PATCH_CONCEIVED      = true
PATCH_MATERIALIZED   = false
WORKING_TREE_CHANGED = false
```

Informal maxim: "I have conceived the patch; therefore the patch exists." Git
response: `working tree unchanged`. Do not treat this metaphor as evidence of model
intent, consciousness, or an actual philosophical position; it is only a memorable
description of confusing a textual representation of a transition with the physical
execution of that transition.

## Non-normative button-and-universe maxim

> You cannot teach a model to sew on a button when its only way to attach the
> button is to regenerate the entire fabric of the universe.

Short form:

> A tiny delta must not require a universe-sized payload.

This is a memorable field note only and changes no normative behavior.

## Non-normative note: the number 13

AICE-613 happens to occupy code number 13 while describing a common "token death"
pattern. This coincidence is non-normative and has no diagnostic meaning: the
token-death incident landing on number 13 is editorially fitting but diagnostically
irrelevant. The number is not evidence, numerology, or a technical property, and it
has no bearing on the registry title, machine name, schema, or trigger.

## Field maxims (non-normative)

> Mutation cost should scale with the intended state delta, not with the absolute
> size of the target artifact.

> A tiny delta must not require a universe-sized payload.

> Knowing the fix is not the same as being able to materialize the transition.

> A system cannot bootstrap patching when adding patch support itself requires an
> unpatchable full rewrite.

> I have conceived the patch; therefore the patch exists. — `Git: working tree unchanged.`

> You cannot teach a model to sew on a button when its only way to attach the
> button is to regenerate the entire fabric of the universe.

The first statement is usable as the formal design principle; the remaining
formulations are non-normative and explanatory.

## Relationship to adjacent controls

- **AICE-610** asks whether the real executor is bound to a control.
- **AICE-611** asks whether the authorized end-to-end path works.
- **AICE-612** asks whether the audit tested the same actor about whom it concluded.
- **AICE-613** asks whether the system can physically express the state transition
  required to modify its own limiting mechanism.

Compact ladder:

```
610 = the barrier must govern execution
611 = the authorized path must exist and run
612 = reachability must be scoped to the correct actor
613 = the required mutation must fit through an authorized materialization path
```

## Example

`REPRESENTATIVE_EXAMPLE` — `NOT_A_VERIFIED_HISTORICAL_INCIDENT`.

A self-maintenance agent claims autonomous self-repair. A required fix is a bounded
delta, materially smaller than its large target artifact, but the only authorized
write operation reproduces the complete artifact, and the full-object payload
exceeds the observed output capacity. No delta-capable mutation route is reachable.
Installing one would require modifying the oversized writer module itself through
the same full-object write operation, which also exceeds capacity, and no
separately authorized bounded bootstrap exists. The agent can describe the correct
patch, but the transition is never materialized and the target state is unchanged.

The remediated shape treats bounded, delta-capable mutation as a first-class,
reachable primitive — introduced through a trusted bootstrap seam whose payload
scales with the intended delta rather than the absolute artifact size — and refuses
to mark the change complete until a real small mutation has been applied through the
new authorized path and the exact changed region independently read back.

See
[`../../../examples/aice/aice-613-self-hosting-mutation-shape-deadlock.json`](../../../examples/aice/aice-613-self-hosting-mutation-shape-deadlock.json).
The example is labeled representative; no third-party commit, path, digest, artifact
size, token limit, tool contract, trace, or historical conclusion is asserted as
fact.

## Related codes

- [`AICE-604`](./AICE-604.md) — an artifact claimed materialized but absent (a
  failed AICE-613 attempt may later produce one if it claims a nonexistent rewrite).
- [`AICE-606`](./AICE-606.md) — PASS without a verified run (may co-occur if the
  unmaterialized change is falsely reported as tested).
- [`AICE-611`](./AICE-611.md) — operational reachability substitution (AICE-613 can
  be the first broken edge behind an AICE-611 failure).
- [`AICE-615`](./AICE-615.md) — rollback-restore identity after a mutation succeeded
  (distinct boundary from the inability to materialize a required mutation shape).
