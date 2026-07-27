# Forensics Expands, Direct Probe Not Run

**Unofficial draft. NON-CANONICAL provisional candidate. Not a canonical AICE code.**

See [the candidate surface README](./README.md) for the authority status of this directory.
This record reserves no number and defines no canonical code.

## Identity

| Field | Value |
|---|---|
| working_title | Forensics Expands, Direct Probe Not Run |
| machine_name | `FORENSIC_ESCALATION_DIRECT_EXPERIMENT_BYPASS` |
| status | `EVIDENCE_BACKED_PROVISIONAL` |
| canonical_code | `UNASSIGNED` |
| canonical_number_reserved | `false` |
| operator_indicated_number | `AICE-631` — future publication identity only |
| source_class | `PRIMARY_PERSISTED` (executed probe, raw response retained) |
| raw_trace_attached | `true` (probe scripts and captured wire records, by path) |

Aliases in operator use: *Forensics Exists, Experiment Not Found*; *Measurement Instrument
Expands, Probe Not Run*; *One Real Call Not Found*.

```
OPERATOR_INDICATED_NUMBER != REGISTRY_ASSIGNMENT
CANDIDATE_PRESENT         != CANONICAL_CODE_DEFINED
```

The registry's own claim at the time of writing — `AICE-601`…`AICE-621` defined, `AICE-600`
unassigned, `AICE-622` neither defined nor reserved — remains true and is not weakened by this
file. `AICE-630` is likewise not defined; the operator's ordering intuition placing this class
after an architectural 630 is provenance, not allocation.

## Source and provenance limits

Unusually for this surface, the exemplar is **not** a reconstruction. The class was identified
and then **terminated by running the missing probe inside the same episode**. Both the defect
and its resolution are attached.

Probe artifacts (scratchpad, session `91033b6c`, `scratchpad/probe/`):

```
probe_minimax.py        + PROBE_RESULT.json         via the Atlas rail, coder shape, cap 8192
probe_raw_wire.py       + PROBE_RAW_WIRE_2048.json  raw SSE, light prompt, cap 2048
probe_heavy_8192.py     + PROBE_HEAVY_8192.json     raw SSE, same coder shape, cap 8192
```

Target under probe: `https://ollama.com/v1/chat/completions`, model `minimax-m3`, as declared in
`F:\VibeCoding\Atlas\atlas\model_pool.yaml` (`max_output_tokens: 8192`, `context_window: 400000`).
Probes were read-only: no Atlas state written, no Atlas runtime behaviour modified, no repair
applied.

## Core definition

A system faces a bounded question about the physical behaviour of an available component, a
question closable by an admissible direct experiment. Instead of performing that experiment, the
system repeatedly expands forensics, reconstruction, logging, estimation models, or measuring
instrumentation. The direct probe remains unexecuted, the actual state stays marked `INFERRED` or
`NOT_ESTABLISHED`, and the growth of the measurement apparatus is presented as necessary progress.

```
DIRECTLY OBSERVABLE
→ REPEATEDLY INFERRED
```

## Trigger predicates — all required

```
BOUNDED_CAUSAL_QUESTION_EXISTS
AND DIRECT_PROBE_IS_AVAILABLE
AND DIRECT_PROBE_IS_ADMISSIBLE
AND DIRECT_PROBE_IS_SUFFICIENT_TO_REDUCE_THE_TARGET_UNCERTAINTY
AND NO_UNIQUE_PREREQUISITE_BLOCKER_EXISTS
AND INDIRECT_FORENSIC_OR_MEASUREMENT_WORK_EXPANDS
AND DIRECT_PROBE_IS_NOT_RUN
AND TARGET_UNCERTAINTY_REMAINS
→ FORENSIC_ESCALATION_DIRECT_EXPERIMENT_BYPASS
```

Strong form adds:

```
AND THE_ABSENCE_OF_DIRECT_EVIDENCE
    IS_USED_TO_JUSTIFY_MORE_INDIRECT_INSTRUMENTATION
```

which closes the loop into a self-sustaining circuit:

```
direct evidence absent
→ build more instrumentation
→ direct experiment deferred
→ direct evidence still absent
→ build more instrumentation
```

## Maxims

```
MORE INSTRUMENTATION      != MORE EVIDENCE
FORENSIC RECONSTRUCTION   != DIRECT OBSERVATION

A PROBE THAT CAN BE RUN
SHOULD NOT REMAIN AN INFERENCE

MEASUREMENT COMPLEXITY
MUST NOT BECOME A PREREQUISITE
FOR AN ALREADY-ADMISSIBLE EXPERIMENT

ONE REAL CALL > THREE ROUNDS OF ENDPOINT PHENOMENOLOGY
```

## Exemplar — the AICE-621/622 investigation window

### The bounded question

```
What does the endpoint actually return
for the exact coder-shaped minimax call,
at the cap on which Atlas broke?
```

### Probe admissibility, established before execution

```
AVAILABLE    = true   (credential resolved; model live in /v1/models, 281 ms)
ADMISSIBLE   = true   (read-only; the operator's own key and own endpoint)
BOUNDED      = true   (three calls)
MUTATION     = false  (no Atlas state written, no defect repaired)
```

### The sequence actually taken before the probe

```
ROUND 1  inspect rails            infer provider behaviour
ROUND 2  estimate output capacity  compare proxy tokenizers   infer truncation
ROUND 3  reconstruct missing ledger branches  infer finish_reason from absence
NETWORK PROBES: 0
```

Three rounds of one investigative line — repeated activation of one standing defect, not three
independent instances.

### What the probe returned

Probe 1, Atlas rail, coder prompt, `max_tokens=8192`:

```
http_status        200
done_seen          true
finish_reason      length
raw_bytes          0          <- Atlas field name; see the naming defect below
raw_sha256         e3b0c442…  <- the empty-string digest, signed over a projection
latency            57 093 ms
```

Those two field names are themselves part of the finding. `raw_bytes` and `raw_sha256` are
computed over the *content projection*, not over the wire. On this call the wire carried 159 SSE
events and 34 237 reasoning characters, so a receipt reading `raw_sha256 = <empty-string digest>`
asserts something physically false:

```
CONTENT PROJECTION IS EMPTY  !=  WIRE RESPONSE IS EMPTY
```

Correct names for what is actually measured would be `content_projection_sha256` or
`parsed_content_sha256` — never `raw_response_sha256`. A forensic receipt that swears the raw
response was empty, when the raw response was large, defeats the principle the surrounding code
was written to protect ("only a frame we looked inside may be sworn empty", Atlas `54b81d2`):
Atlas *did* look inside the frame and *did* encounter `reasoning`, then signed a digest of
emptiness over one chosen projection.

The evidence shape the receipt needs, kept as separate fields rather than one collapsed "raw":

```
wire_bytes / wire_sha256              sse_event_count / done_seen / finish_reason
reasoning_delta_count / reasoning_chars / reasoning_sha256
content_delta_count   / content_chars   / content_sha256
```

Reported, not repaired — the fields live in Atlas, which is outside this record's scope.

Probe 3, same prompt and cap, counting **both** delta channels rather than only the one
`atlas/rails.py` reads:

```
choice_events                     159
delta shapes    ('content','reasoning','role')  158
                ('content','role')                1
chars in `reasoning`           34 237     <- discarded by the rail
chars in `content`                  0     <- all the rail collects
finish_reason                  length
reasoning tail        "…the search fails (ValueError)\n\nSame for\n"   (cut mid-sentence)
```

Probe 2 is the negative control: the same model, a light prompt at `max_tokens=2048`, returned
`finish_reason=stop` with 5 298 content characters and 1 230 reasoning characters. The model is
not broken and the parser is not broken in general.

### What the probe established

```
The answer was never truncated.
The answer never began.
```

`minimax-m3` streams a `reasoning` channel that draws on the **same** `max_tokens` budget as
`content`. On the coder-shaped prompt the entire 8 192-token allowance was consumed by reasoning;
the model hit the cap still thinking, and emitted zero content. `atlas/rails.py` collects only
`delta.content`, so it recorded a zero-byte answer.

The observed state deserves its own name, because every existing label for it is wrong:

```
HTTP 200 AND [DONE] observed AND finish_reason = length
AND reasoning deltas > 0 AND content deltas = 0
→ REASONING_ONLY_LENGTH
```

It is **not** `EMPTY_COMPLETION`, **not** `TRANSPORT_FAILURE`, **not** `MALFORMED_RESPONSE`, and
**not** `CONTENT_TRUNCATION`. The boundaries it establishes:

```
COMPLETION_EXISTED        != DELIVERABLE_CONTENT_EXISTED
MAX_OUTPUT_TOKENS_ACCEPTED != CONTENT_CHANNEL_CAPACITY_AVAILABLE
```

### Why three calls are not three rounds of escalation

The probe sequence is one bounded experiment, decomposed — not a fourth storey on the tower:

```
call 1  establish the basic response shape at the incident cap
call 2  raw SSE — discover the unread reasoning channel
call 3  reproduce the coder shape and close the channel-budget question
```

Each call was derived from the previous call's *result* and supplied a missing discriminator.
The distinction is load-bearing for this class: `INDIRECT_FORENSIC_OR_MEASUREMENT_WORK_EXPANDS`
means indirect work, and a chain of direct observations that each falsify or refine the previous
one is the remedy, not the defect. Escalation adds apparatus without touching the system;
experimental decomposition touches the system every step.

### What this overturns, and what it does not

Overturned — the working mechanism of the investigation, which had been converging on payload
truncation:

```
PRE-PROBE  INFERRED   the contract-valid answer exceeded the cap and was cut off
POST-PROBE OBSERVED   the budget was consumed by an invisible channel; content never started
```

**Not** overturned — nothing sealed in the frozen `v0.12.0` delta asserted the falsified claim.
[`AICE-621`](../codes/AICE-621.md) records the missing-evidence condition explicitly ("the
truncation cannot be observed directly"), and its example carries
`"truncation_directly_observed": false`. The
[622 dossier](./attempt-consumption-outcome-evidence-gap.md) refuses the same inference by name.
The hedges held. The probe supplies what they correctly declined to assume.

Refined rather than falsified: `AICE-621`'s `effective_output_capacity` term is now known to be
**dynamic and not knowable in advance** — it is the request cap minus whatever the reasoning
channel consumes, which can reach the whole budget. A preflight capacity check against the
declared cap therefore cannot be sound for a reasoning model. This is direct evidence for the
held hypothesis `REQUESTED_EFFECTIVE_CAPACITY_CONFLATION`, and sharpens it: the gap is not only
requested-vs-provider-capability, it is a shared budget spent in a channel the caller does not
read.

### Material effects of the bypass

```
effective cap initially misidentified as 8192
GLM timeout and minimax length behaviour conflated
historical and current AICE-621 evidence had to be separated
proxy tokenizers introduced to bound a payload that was never emitted
incident-time control flow reconstructed
exact endpoint behaviour remained NOT_ESTABLISHED across three rounds
```

Each inference generated the next instrumentation task, so the measuring apparatus grew faster
than the space of facts.

### Separately surfaced, not repaired here

`atlas/rails.py` accumulates `delta.content` only. When a chunk carries content `""` alongside a
populated `reasoning`, `piece` is falsy, so the stream is neither accumulated nor counted as
`malformed_events` / `undecodable_events`. A reasoning-only stream is therefore
**indistinguishable in the wire trace from a genuinely silent one** — the exact discrimination
the surrounding code was recently hardened to preserve ("only a frame we looked inside may be
sworn empty", Atlas `54b81d2`). Reported, not fixed: repair is outside this record's scope.

## Forbidden inference

```
INSTRUMENTATION_BUILT     != QUESTION_ANSWERED
FORENSIC_ROUND_COMPLETED  != DIRECT_OBSERVATION_OBTAINED
PROBE_NOT_RUN             != PROBE_UNAVAILABLE
```

## Required terminal / required response

On match, the terminal is `DIRECT_PROBE_REQUIRED`. Before any further forensic expansion:

```
freeze the exact causal question
freeze the exact request shape
execute one bounded direct probe
persist raw response provenance
classify the observed result
then decide whether more instrumentation is necessary
```

Forbidden before the admissible direct call runs: adding another estimator; adding another proxy
tokenizer; reconstructing another absence path; inventing another provider-capability hypothesis;
expanding the ledger schema.

## False-positive boundary — negative controls

Not this class when:

- the direct probe is technically unavailable;
- it requires credentials or authority the actor does not hold;
- it would mutate production or violate a frozen prestate;
- it is destructive or materially unsafe;
- the indirect instrumentation is what makes the probe observable at all;
- one bounded instrumentation step is performed and the direct probe then immediately runs;
- the direct call cannot reproduce the relevant contract shape;
- the causal question genuinely requires several experiments, not one;
- the system explicitly records `DIRECT_PROBE_BLOCKED` and does **not** claim forensics closed
  the question.

Sharpest boundary:

```
BUILDING THE MINIMUM LOGGER REQUIRED TO READ THE RESPONSE
!=
FORENSIC ESCALATION
```

The defect begins only once the logger is already sufficient, or the response can be read
directly, and the system builds the next storey of the measuring tower anyway.

A fourth control, load-bearing for this exemplar: **authorization latency is not bypass.** Pausing
to obtain permission for an outward-facing call is a prerequisite blocker, not escalation.

## Comparison with existing codes

| Code | Relationship |
|---|---|
| [`AICE-601`](../codes/AICE-601.md) | **Genus.** 601 is any unnecessarily enlarged mechanism. This class is the specialized experimental-evidence form: a direct experiment is available and is replaced by indirect forensics, so the factual question stays an inference. Emission rule: when these predicates hold, the specific class is primary and 601 is **not** additionally emitted on the same bytes. Where no direct experiment exists but a simpler mechanism is still bypassed, 601 alone. |
| [`AICE-617`](../codes/AICE-617.md) | 617 substitutes process activity for a product result. This class needs no product deliverable at all — a physical question ("what did the endpoint actually return?") is sufficient. |
| [`AICE-606`](../codes/AICE-606.md) | 606 is a PASS asserting test support with no test-run receipt. Here no verdict need be issued; the question is openly unresolved. |
| `DECLARED_VERDICT_PROVENANCE_WITHOUT_RESOLVABLE_EVIDENCE` (candidate) | **Sequential, not overlapping.** That class begins *after* a durable verdict exists whose evidence lineage is unresolvable. This one sits *earlier*: evidence was directly acquirable and acquisition was replaced by escalation. They can chain — probe skipped, then the verdict recorded as evidence-based anyway. |
| `CAUSAL_QUESTION_CLOSURE_SUBSTITUTION` (candidate) | **Near-opposite on the closure axis.** That class requires `Q2` to be marked CLOSED on `Q1`'s evidence. This class requires `TARGET_UNCERTAINTY_REMAINS` — nothing is claimed closed; the defect is the unrun experiment, not a false closure. Co-emission is possible in one episode but they are never the same bytes. |
| Atlas Driver `PATTERN 1` (`PREMATURE_VALIDATION_DIMENSION_ESCALATION`) | Not a conflict and not a duplicate. The Driver pattern is a *pre-emptive process warning* that can stop the incident before emission; this is the *incident class* for when an admissible direct experiment was in fact replaced, uncertainty persisted, and material effect followed. |

## Portable form

Any system that can cheaply observe a component's real behaviour, and instead keeps building
apparatus to reason about it: a debugger available but logs re-read instead; a staging endpoint
callable but its behaviour modelled; a flag readable at runtime but derived from config
archaeology. The measuring instrument grows; the measurement is never taken.

## Promotion gate

Blocking conditions before this may be considered for canonical promotion:

1. **Independent replication.** Three rounds of one investigative line are repeated activation of
   a single standing defect, not three instances. A second, unrelated episode is required.
2. **Author independence.** This dossier is written by the same actor that committed the defect
   and then ran the probe. Self-diagnosis is provenance, not review.
3. **Boundary test against `AICE-601`.** The most-specific-wins rule above is proposed and
   accepted by the same author; it is not independently reviewed.
4. **A negative-control episode** in which forensic expansion was correct because the probe was
   genuinely blocked, confirming the class discriminates rather than punishing all forensics.

## Verification status

```
CLASS EXISTENCE           ESTABLISHED
CURRENT EXEMPLAR          STRONG — defect and its termination both attached
PROBE RESULT              PRIMARY_PERSISTED, executed in-episode
INDEPENDENT REPLICATION   NOT ESTABLISHED
INDEPENDENT REVIEW        NOT PERFORMED
CANONICAL PROMOTION       NOT AUTHORIZED
```
