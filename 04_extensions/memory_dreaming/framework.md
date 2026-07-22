# CAP Memory Dreaming

Memory Dreaming is an offline memory-recompilation layer for CAP runtimes. It
reads existing memory, transcripts, retrieval traces, and COM telemetry, then
produces reviewable candidate artifacts. It does not train the model and it
does not write to canonical memory directly.

The short form:

```text
L0/L1 memory state + transcripts + artifacts + COM telemetry
  -> offline Dream run
  -> candidate memory store + memory diff + review report
  -> verifier / human approval / release gate
  -> approved canonical memory store
```

## Scope

Memory Dreaming is useful when a runtime has accumulated cross-turn state that
needs consolidation, de-duplication, contradiction handling, or provenance
repair. It is not a replacement for RAG, validators, or fine-tuning.

- RAG retrieves evidence for the current question.
- Validators inspect current outputs.
- Fine-tuning changes model tendencies.
- Memory Dreaming proposes maintenance diffs over external memory state.
- CAP decides which diffs may become canonical.

The core invariant is:

```text
No memory becomes canonical merely because a model compressed it.
```

## Ontology

### Memory store classes

| Term | Meaning | Write rule |
|---|---|---|
| `RawTraceStore` | Raw session traces, tool traces, and user-visible exchanges | Evidence input; not canon |
| `CanonicalMemoryStore` | Approved long-lived anchors and their provenance | Read-dominant; updated only by approved diff |
| `CandidateMemoryStore` | Dream output prepared for review | Writeable by Dream run; not canonical |
| `QuarantineLedger` / `L1-Q` | Contaminated, weak, contradictory, or unsafe nodes | No truth authority |
| `SupersededAnchorLedger` / `L1-D` | Superseded or retired anchors kept for audit | Append-only audit surface |
| `MemoryDiffLedger` | Explicit proposed operations from the Dream Compiler | Review surface |
| `DreamReviewReport` | Verifier results, approval status, and blocked items | Gate evidence |
| `TranscriptTraceSet` | Raw conversations, tool traces, and session references | Read-only input |
| `ComTelemetrySet` | COM logs, state transitions, validation outcomes | Read-only input |

### Memory node fields

Every proposed or canonical memory node must carry:

```text
id
content
claim_type
status
confidence
provenance
evidence_count
contradicts
supersedes
valid_from
valid_until
review_required
```

Allowed `claim_type` values:

- `fact`
- `preference`
- `project_state`
- `decision`
- `boundary`
- `hypothesis`

Allowed `status` values:

- `raw`
- `proposed`
- `approved`
- `deprecated`
- `superseded`
- `quarantined`
- `rejected`

`proposed` is the normal output status of a Dream run. `approved` is assigned
only after verifier and approval gates pass.

## Framework

### Dream run input

Field names below match the machine-readable schema
[`../../spec/memory_dreaming/run.schema.json`](../../spec/memory_dreaming/run.schema.json).
Each `*_refs` field is an array of `source_ref` pointers, not inlined stores.

```text
canonical_store_refs
proposed_store_refs
quarantined_store_refs
superseded_ledger_refs
session_transcript_refs
artifact_refs
com_telemetry_refs
policy
```

### Dream run output

```text
candidate_store
memory_diff
review_items
rejected_items
telemetry
```

### Pipeline

1. Read canonical memory, proposed memory, quarantined memory, superseded
   ledger refs, artifact refs, transcripts, and COM telemetry.
2. Detect duplicate anchors, stale anchors, contradictions, weak provenance,
   contaminated traces, and unsupported promotions.
3. Propose explicit diff operations.
4. Run verifier checks against evidence, contradiction risk, transition cost,
   and source validity.
5. Route every diff to `pass`, `needs_review`, or `block`.
6. Apply only approved diffs to canonical memory.
7. Keep rejected and superseded state for audit.

## Diff Operations

| Operation | When needed | Effect |
|---|---|---|
| `keep` | Existing node remains valid | No canonical change |
| `reconcile` | Nodes are compatible duplicates or partials | Merge, de-dupe, strengthen provenance |
| `deprecate` | Node is stale but not false | Move out of active authority |
| `supersede` | Newer approved node replaces older node | Preserve old node in ledger |
| `retcon` | Old anchor had the wrong interpretation | Mark old anchor superseded and propose replacement |
| `quarantine` | Node is contaminated, contradictory, or weakly sourced | Remove from authority path |
| `rollback` | Candidate diff or candidate store is unsafe | Reject candidate and keep last approved snapshot |

These are ledger operations, not invisible edits.

```text
Every memory mutation must be explainable as a diff.
Every diff must have provenance.
Every retcon must preserve old state.
Every rollback must restore an approved state.
Every canonical update must pass gate.
```

## Reconcile

Reconcile is the preferred path when multiple nodes are compatible. It merges
or de-duplicates without rewriting history.

```text
L1-P / compatible nodes
  -> merge / de-dupe / strengthen provenance
  -> one cleaner proposed anchor
  -> approval gate
  -> optional L1-C
```

Reconcile must not hide dissenting evidence. If two nodes are only apparently
compatible, the operation downgrades to `needs_review`.

## Retcon

Retcon repairs an interpretation while preserving the prior state. It is
needed when an older anchor encoded the wrong reading of an event.

Correct CAP retcon:

```text
old anchor remains as superseded
new anchor becomes proposed
approval gate decides whether the replacement becomes approved
```

Retcon is not a silent overwrite. Silent retcon is memory corruption.

## Rollback

Rollback is a safety boundary. It is used when a Dream candidate store or
candidate diff is unsafe.

Examples:

- the Dream run merged unrelated memories
- the Dream run canonicalized weak evidence
- the Dream run deleted a useful contradiction
- the Dream run collapsed different project branches
- the Dream run accepted contaminated transcripts

Rollback may reject the candidate store, reject a specific diff, or restore the
last approved snapshot. Candidate memory must not damage canonical memory.

## Relation To CAP Layers

Memory Dreaming is a runtime-governance layer:

- Looking-Glass asks why the current memory became this way.
- Latent Cause Reconstruction ranks hidden causes of memory rupture.
- Adjustment Dynamics proposes admissible repair paths.
- Memory Dreaming compiles candidate memory diffs.
- Release Gate decides what may become canonical.

In compiler language:

```text
Dreaming is the compiler.
Reconcile / retcon / rollback are compiler passes.
Release Gate is the linker.
Canonical memory is the built artifact.
```

## Guards

Memory Dreaming may:

- propose memory
- merge compatible candidates
- mark weak nodes for review
- preserve superseded nodes
- quarantine contaminated nodes
- recommend rollback

Memory Dreaming may not:

- canonicalize memory directly
- delete provenance
- hide contradictions
- treat model compression as proof
- mutate canonical input stores in place
- make RAG retrieval unnecessary
- replace human or authorized release review

## Machine-Readable Contract

The corresponding schema is
[`../../spec/memory_dreaming/run.schema.json`](../../spec/memory_dreaming/run.schema.json).
It defines a `MemoryDreamingRun` record with candidate store, `memory_diff`
operations, review items, verifier outcomes, and approval state.

The schema is the enforcement surface for the doc-level invariants in this
extension. In particular it rejects:

- `output.candidate_store[*].status` or `output.rejected_items[*].status` set
  to `approved` or `raw` (Dream cannot self-canonicalize and does not emit
  raw traces);
- `memory_diff` without `provenance` (`minItems: 1`);
- `memory_diff` with `op` in `{keep, reconcile, deprecate, supersede, retcon,
  quarantine}` and no `target_id`;
- `memory_diff` with `op` in `{supersede, retcon}` and no `proposed_id`;
- missing `artifact_refs` or `superseded_ledger_refs` in `input`;
- missing `contradicts`, `supersedes`, `valid_from`, or `valid_until` on a
  memory node;
- `input.policy.allow_direct_canonical_write: true`,
  `input.policy.require_provenance: false`, or
  `input.policy.require_approval: false`;
- `approval.status` in `{not_reviewed, rejected, rolled_back}` combined with a
  non-empty `approved_diff_indexes`;
- `approval.status` in `{approved, partially_approved}` combined with an
  empty `approved_diff_indexes`.

A worked example covering all seven diff operations lives at
[`../../examples/memory_dreaming/run_example.json`](../../examples/memory_dreaming/run_example.json)
and is exercised by
[`../../reference/python/tests/memory_dreaming/test_schema.py`](../../reference/python/tests/memory_dreaming/test_schema.py).

## Status

`research-only / architecture extension`

This document defines the ontology and operational framework. It has not yet
been promoted to a validated benchmark track. Any implementation must report
Dream outputs as candidate artifacts unless an explicit release gate promotes
them.
