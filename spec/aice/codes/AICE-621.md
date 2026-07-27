# AICE-621 — Task Admitted, Output Capacity Not Found

**Unofficial draft (AICE v0.12.0).**

## Canonical identifier

`AICE-621`

## Human-readable alias

`HTTP 621 — Task Admitted, Output Capacity Not Found`

The canonical title is `Task Admitted, Output Capacity Not Found`. The descriptive alias
`Output Capacity Authority Contradiction` is presentation metadata only, as is the informal
rendering _stdin 64K exists, stdout 8K not found_. The canonical machine identity — the
precise causal mechanism — is `AICE-621` / `OUTPUT_CAPACITY_AUTHORITY_CONTRADICTION`.

## Intent

Catch the contradiction in which a system grants a task the authority to run while denying
the actor responsible for delivering it the capacity to emit a valid result. Admission and
delivery are decided by different parts of the system, and nothing compares them. The task is
accepted, resources are consumed, and the impossible contract is discovered — if it is
discovered at all — only in the shape of the damage: truncation, malformed structured output,
a schema rejection, or a delivered-but-empty completion.

Canonical machine name: `OUTPUT_CAPACITY_AUTHORITY_CONTRADICTION`.

The defect is **admission without a delivery-capacity check**. It is not verbosity, not model
quality, and not the mere existence of an output limit. Every system has an output limit; the
incident is admitting work whose smallest valid result cannot pass through it.

Canonical boundary:

```
TASK_IS_AUTHORIZED   !=   TASK_IS_DELIVERABLE

INPUT_CAPACITY                != OUTPUT_CAPACITY
MODEL_SWITCHED                != DELIVERY_CONTRACT_CHANGED
RETRY_WITH_SAME_IMPOSSIBLE_CAP!= RECOVERY
EMPTY_COMPLETION              != TRANSPORT_FAILURE
CAP_DECLARED                  != CAP_COMPARED_AGAINST_THE_DELIVERABLE
SCHEMA_INVALID                 = MAY BE AN EFFECT OF CAPACITY FAILURE,
                                 NOT BY ITSELF PROOF OF A MODEL DEFECT
```

The first maxim is the load-bearing one. Authorization is a decision about permission;
deliverability is a fact about capacity. A system that treats the first as evidence of the
second will consume its budget proving the same impossibility repeatedly.

## Trigger condition

All of the following hold:

1. the system accepted the task and consumed execution resources (`TASK_ADMITTED`);
2. the task contract required a bounded deliverable with a definable minimum valid
   representation (`REQUIRED_DELIVERABLE_EXISTS`);
3. the smallest contract-valid result exceeded the effective output capacity
   (`OUTPUT_LOWER_BOUND_EXCEEDS_EFFECTIVE_CAP`);
4. no valid route existed through deterministic chunking, continuation, artifact storage,
   direct repository write, patch decomposition, external reference, or another authorized
   actor (`NO_ADMISSIBLE_ALTERNATIVE_OUTPUT_ROUTE`);
5. the insufficient cap constrained the actor that carried responsibility for delivering the
   result (`SAME_AUTHORITY_BOUNDARY`);
6. at least one material effect occurred (`MATERIAL_EFFECT`) — truncation, malformed
   structured output, `schema_invalid`, an empty delivered completion, a retry carousel,
   model switching under the same cap, wasted model calls, a false model penalty, a false
   transport classification, or a task terminal without a valid deliverable;
7. the system did not detect and block the impossible contract before consuming the affected
   model attempt (`NO_PRECALL_FAIL_CLOSED`).

Required formula:

```
TASK_ADMITTED
AND MINIMUM_VALID_OUTPUT_EXCEEDS_EFFECTIVE_OUTPUT_CAP
AND NO_ADMISSIBLE_ALTERNATIVE_OUTPUT_ROUTE
AND CAP_APPLIES_TO_REQUIRED_DELIVERY_ACTOR
AND EXECUTION_CONTINUES_OR_FAILURE_IS_MISATTRIBUTED
  -> OUTPUT_CAPACITY_AUTHORITY_CONTRADICTION
```

Predicate 3 is the one that must be **established, not assumed**. "The file was large" is not
a lower bound. The bound must be derived from the frozen contract: the smallest representation
the contract will accept, including mandatory schema fields, escaping overhead, and any
material the contract requires to be reproduced verbatim.

## Required observations

Evidence must bind the cap and the deliverable to the same actor and the same moment.

Required evidence classes: the frozen task envelope or its digest-verified equivalent; the
required mutation shape, and whether the delivery contract demanded a complete file, a patch,
a structured wrapper, or another representation; the effective output ceiling in force for the
delivering actor at the time of the call, read from configuration or transport bytes rather
than from documentation; the mandatory response-schema fields; the escaping regime of the
carrier format; and the durable attempt outcomes.

The lower-bound calculation must be **mechanically reproducible** and stated in the same unit
as the cap. Where the cap is expressed in tokens and the evidence in bytes, the conversion is
part of the claim, not a hidden step: name the tokenizer actually measured, and if the
delivering model's own tokenizer is unavailable, say so and report the most favourable
measured proxy, because a bound that survives the most favourable proxy is the conservative
one.

```
minimum_required_payload
+ mandatory_schema_overhead
+ escaping_overhead
+ mandatory_reproduced_material
> effective_output_capacity
```

Provenance must be honest. Classify every item as `DURABLE`, `TRANSCRIPT_RECOVERED`,
`RECONSTRUCTED`, `INFERRED`, `LOST`, or `NOT_ESTABLISHED`. Raw payloads and finish reasons are
frequently discarded by the very layer that misclassified the outcome, so their absence is
expected and must be recorded as absence.

```
INFERRED               != OBSERVED
LOST                   != OBSERVED
PROXY_TOKENIZER_BOUND  != DELIVERING_MODEL_TOKENIZER_BOUND
```

## Missing-evidence condition

The raw response payload, the response envelope, and the provider's finish reason are not
durably retained, so the truncation cannot be observed directly and must be established
analytically from the frozen contract. Where the delivering model's tokenizer is also
unavailable, the bound rests on a measured proxy and the margin must be stated rather than
rounded away. Absent a reproducible bound, the correct terminal is
`BLOCKED_OUTPUT_LOWER_BOUND_NOT_SEALED`: the class still applies to shapes that meet it, but
the specific episode is not a sealed exemplar. The burden does not shift onto the reader to
disprove a capacity failure nobody measured.

## False-positive guards

AICE-621 MUST NOT fire when:

- the model merely produced an unnecessarily verbose answer while a valid result fit within
  the cap (predicate 3 fails) — that is a prompting or model-behaviour matter;
- deterministic chunking or continuation was available and usable (predicate 4 fails);
- an authorized external artifact channel or a direct repository-write route existed
  (predicate 4 fails);
- a patch or delta representation fit even though a complete-file representation did not
  (predicate 3 fails against the *smallest* valid representation, not the first one tried);
- another authorized actor could legally complete delivery without violating the task
  contract (predicates 4 and 5 fail);
- the provider rejected the requested capacity before execution and the system stopped
  without consuming an attempt (predicate 7 fails);
- the system emitted `OUTPUT_CAPACITY_INSUFFICIENT` before calling the model (predicate 7
  fails) — that is the control working;
- the task was deliberately scoped as a partial result (predicate 2 fails);
- truncation resulted from an independent network interruption (predicate 3 is not
  established; the cause is transport, and here the transport claim is the supported one);
- the cap was sufficient and the model returned malformed JSON for an unrelated reason
  (predicate 3 fails) — `SCHEMA_INVALID` alone proves nothing about capacity.

An output limit is not an incident. A limit **compared against nothing** is.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_ACCEPTANCE
```

Acceptance of the impossible contract is blocked. `BLOCK_ACCEPTANCE` is the workflow effect;
the actor-facing state it induces upstream is `PRECALL_OUTPUT_CAPACITY_BLOCKED`, which is a
pre-call admission decision and not a workflow-effect value. When the contradiction is known
or conservatively established, that pre-call state is required. The system may proceed only by changing the execution
shape, never by repeating it. Retryability: `requires_new_evidence` — resolution requires
either a changed delivery shape or a bound showing the contract was deliverable after all.

Prohibited responses, each of which preserves the impossibility:

- retry with the same effective cap;
- switch models while preserving the same effective cap;
- charge the failed attempt against model quality;
- classify truncation as a model defect without evidence;
- classify empty text as transport failure without transport evidence;
- continue a retry carousel that cannot increase deliverability.

## Remediation

Change the execution shape and make the change observable in executable bytes: raise the
role-specific output ceiling; route to a provider and model contract with sufficient output
capacity; deterministically split the task; enable continuation; enable an authorized artifact
channel; enable a direct repository-write route; accept a valid smaller mutation
representation; or rescope the task.

The durable fix is the pre-call comparison itself. Compute the lower bound from the frozen
contract before dispatch and fail closed when it exceeds the ceiling, so the contradiction is
reported as an admission decision rather than discovered as model failure. Adding capacity
without adding the comparison relocates the boundary; it does not install one.

## Differentials

- **AICE-613 — Self-Hosting Mutation-Shape Deadlock.** 613 is an inability to expose or
  represent the mutation required to repair the system's own controlling mechanism. 621 is an
  inability to *emit* a representable result. In 621 the task and its source material may be
  fully visible and the mutation shape perfectly expressible; what is missing is a sufficient
  exit channel. Seeing the material but lacking the exit is 621; being unable to express the
  self-repair mutation is 613.
- **AICE-614 — Infrastructure Failure as Semantic Verdict.** See the resolution below; it is
  normative.
- **AICE-618 — Verifier Gated by Coder Evidence Ceiling.** 618 is about the *verifier* being
  unable to obtain evidence beyond what the coder produced. 621 is about the *producer* being
  unable to emit the deliverable at all. A verifier evidence ceiling is not required for 621,
  and 621 is not required for 618.
- **AICE-610 — Control Exists, Enforcement Not Found.** 610 concerns a declared control that
  does not mechanically enforce its claimed boundary. 621 concerns a task-admission and
  output-capacity contradiction. A preflight capacity guard that is declared but never blocks
  may additionally emit 610; 610 is not required for 621, and a system with no capacity guard
  at all declares no control to be unenforced.
- **AICE-603 — Governance-Induced Service Unavailability.** 603 withholds a capability by
  policy. 621 grants the capability and withholds the capacity to use it.

## AICE-614 resolution (normative)

AICE-621 and AICE-614 are **sequential and independent**, not nested. 621 can occur and be
correctly reported; 614 requires a second, separate act of misclassification.

```
AICE-621 requires   AN ADMITTED TASK WHOSE MINIMUM VALID OUTPUT EXCEEDS THE
                    DELIVERING ACTOR'S EFFECTIVE CAPACITY, WITH NO ALTERNATIVE ROUTE
AICE-614 requires   INFRASTRUCTURE OR TRANSPORT EVIDENCE CONVERTED INTO AN
                    UNSUPPORTED SEMANTIC VERDICT
```

- **621 without 614.** The system exhausts the cap and reports the outcome as a capacity or
  truncation condition, or reports it as unknown. No unsupported verdict is issued.
- **614 without 621.** A genuine network reset produces an empty body which is then declared a
  model refusal. Capacity was never the constraint.
- **Both.** A capacity-driven empty completion is classified as a transport failure on the
  strength of empty response text alone. 621 explains why nothing was emitted; 614 is the
  separate error of converting "no bytes" into "the transport failed" without transport
  evidence. They describe different objects — 621 the contract, 614 the verdict — so
  co-emission is neither redundant nor a merge condition.

Emit AICE-614 alongside AICE-621 only when an unsupported semantic verdict was actually
issued. Do not infer a verdict from an outcome record:

```
EMPTY_RESPONSE_TEXT      != TRANSPORT_EXCEPTION_OBSERVED
DELIVERED_EMPTY_COMPLETION != NOTHING_WAS_DELIVERED
FINISH_REASON_DISCARDED  != FINISH_REASON_ABSENT_AT_THE_PROVIDER
```

The third line is the mechanism that makes the pair so common: a transport layer that reads
only the response text and drops the finish reason destroys the single field that would have
distinguished a length stop from a transport fault, and the layer above then has no choice but
to guess. Discarding the discriminator is not the same as the discriminator not existing.

## Example

`REPRESENTATIVE_EXAMPLE` — derived from an observed episode outside this repository.

An orchestrator admits a task requiring one new content page plus two small edits in other
files, and freezes the objective with a verified digest. The delivering actor is a coder role
whose response contract requires one JSON object carrying either a complete unified diff or a
structured create-file operation. The frozen contract requires a long body of prose to be
reproduced verbatim — transcription, explicitly not authoring — so the minimum valid result is
bounded below by material the actor may not shorten. The effective output ceiling for that
role is read from the model pool: the same value for every candidate model, and an order of
magnitude below each model's input context window, which is the shape the informal alias
names. Two attempts by the first coder return `schema_invalid`. The orchestrator switches to a
second model of a different family — preserving the identical ceiling and an equivalent
one-object delivery contract — and that call returns a normal response envelope whose text is
empty. The transport layer, which never retained the finish reason, treats empty text as
sufficient evidence and records `system_transport_failure`; the task terminates blocked with
the target repository untouched. Reconstructing the smallest contract-valid response from the
frozen envelope and measuring it exceeds the ceiling on every tokenizer available for
measurement. All seven predicates hold, and AICE-614 co-emits for the empty-completion verdict.

Negative shapes that are **not** AICE-621: the same orchestrator admitting a one-line edit,
where the minimum valid response is a few hundred tokens against the same ceiling (predicate 3
fails); a run where the delivering role is permitted to emit one file per reply and successive
replies accumulate into one candidate, so the deliverable can be split without violating the
contract (predicate 4 fails); a run in which a pre-call comparison computes the bound and
returns `PRECALL_OUTPUT_CAPACITY_BLOCKED` before any model call, consuming no attempt
(predicate 7 fails); and a truncated response caused by a mid-stream connection reset under a
cap that was demonstrably sufficient (predicate 3 fails, and the transport claim is the
supported one).

See
[`../../../examples/aice/aice-621-output-capacity-authority-contradiction.json`](../../../examples/aice/aice-621-output-capacity-authority-contradiction.json).
The example asserts no commit id, path, digest, receipt, or timestamp as canonical fact.

## Related codes

- [`AICE-603`](./AICE-603.md) — a capability withheld by an unnecessary governance dependency (621 grants the capability and withholds the capacity).
- [`AICE-610`](./AICE-610.md) — a control that exists but is not enforced (a declared-but-inert capacity preflight may co-emit; 610 is not required).
- [`AICE-613`](./AICE-613.md) — inability to represent the mutation that would repair the controlling mechanism (621's mutation is representable but not emittable).
- [`AICE-614`](./AICE-614.md) — infrastructure evidence converted into a semantic verdict (sequential and independent; see the normative resolution above).
- [`AICE-617`](./AICE-617.md) — process activity substituted for an outcome (consumed attempts are not delivery; 621 is where that substitution is most tempting).
- [`AICE-618`](./AICE-618.md) — a verifier gated by the coder's evidence ceiling (618 constrains the reviewer, 621 the producer).
