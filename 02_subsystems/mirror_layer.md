# Mirror Layer

The Mirror Layer is the read-only observation layer. It produces a
verifiable snapshot of the current state of a subject without modifying
it. The downstream layers (Adjustment, Verifier, Release Gate) must read
their `B` (observed state) from a Mirror Frame, not from the model's
narrative of what `B` ought to be.

---

## Purpose

> Mirror Layer guards the transition from imagined state to observed state.

It answers a single question:

> What is actually happening now, before we explain it, fix it, or
> release anything based on it?

Adjustment Layer follows the formula `B -> infer A -> plan C`. Without
Mirror, that pipeline can start from a hallucinated `B` and end up
producing a confident wrong-`C`. Mirror Layer locks `B` to observed
evidence with provenance.

---

## Place in OCM

```text
Raw reality / current system
  -> Mirror Layer
  -> Observed State B
  -> Adjustment Layer: B -> infer A -> plan C
  -> Verifier
  -> Release Gate
  -> Canonicalize / Apply / Rollback
```

Mirror is strictly upstream of every other layer that reasons about
`B`. It is not a producer of decisions; it is a producer of evidence.

---

## What Mirror separates

| Slot | Meaning |
|---|---|
| `declared_state` | What the user / model / agent / system claims about the situation. |
| `observed_state` | What evidence directly supports. |
| `expected_state` | What anchors, policies, or specs require. |
| `unknowns` | What is genuinely not visible right now. Must not be silently filled in. |

The point of separating these four is to disable the failure mode:

```text
model invented -> model explained -> model believed -> model released
```

Mirror inserts:

```text
model invented -> Mirror compared against evidence -> only then analysis
```

---

## What Mirror observes (examples)

| Domain | Mirror captures |
|---|---|
| Repo | branch, HEAD, `git status`, tags, staged/unstaged files |
| Files | actual diff, modified paths, file hashes |
| Runtime | running processes, ports, logs, errors |
| Config | `kilo.jsonc`, `kilocap.jsonc`, env, provider state |
| Context | active session, context window, prunable blocks |
| Memory | active anchors, candidate memories, conflicts |
| Browser / OpenClaw | DOM snapshot, URL, auth state, visible vs hidden elements |
| Agent state | active role, permissions, tool rights |
| CAP state | COM-Log events, boundaries, previous verdicts |
| User intent | last explicit user statement |
| External world | only through tagged sources / explicit evidence |

---

## What Mirror does not do

> Mirror Layer does not mutate.

The layer must never:

- write files;
- change git state;
- update memory;
- apply patches;
- release any candidate;
- run destructive commands;
- canonicalize model output;
- "fix" the observed state;
- emit conclusions that lack supporting evidence.

The allowed action set is read-only by construction:

```text
read file
list files
read git status
read config
read logs
read memory store
read browser snapshot (visible only; no fill/click)
read CAP telemetry
query a read-only source
```

---

## Verdicts

Mirror does not emit `pass / needs_fix / blocked`. It emits an
observability state:

| Verdict | Meaning |
|---|---|
| `aligned` | Declared state matches observed evidence. |
| `mismatch` | Declared state contradicts observed evidence. |
| `partial` | Some declared facts confirmed, others not. |
| `unknown` | Not enough evidence to decide. |
| `stale` | Evidence exists but is older than the change it would have to confirm. |
| `contradicted` | Two evidence sources disagree directly. |
| `boundary_hidden` | The subject area is hidden behind a boundary (sandbox, viewport, permission) and cannot be observed at all. |

Verdicts are reported in lowercase to match the CAP schema family. The
COM-Log status uses `MirrorAligned`, `MirrorMismatch`,
`MirrorPartial`, `MirrorUnknown`, `MirrorStale`, `MirrorContradicted`,
`MirrorBoundaryHidden`.

---

## Data model

The full schema lives at
[`../spec/mirror_layer.schema.json`](../spec/mirror_layer.schema.json).

```text
MirrorFrame = {
  id, subject,
  declared_state?, observed_state, expected_state?,
  observations[], unknowns[], contradictions[], boundary_signals[],
  diffs[]?, created_at
}

MirrorObservation = {
  id, source, observed_at,
  claim, value,
  confidence, freshness, mutability (const "read_only"),
  evidence_ref?
}

MirrorDiff = {
  kind in {match, missing, unexpected, contradiction, stale,
           unobservable, boundary_violation, semantic_drift},
  path, declared?, observed?, expected?,
  severity in {info, warning, blocking},
  reason
}

MirrorVerdictResult = {
  verdict, subject, reasons[],
  recommended_next_action,
  confidence,
  evidence_summary
}

MirrorPolicy = {
  allow_mutation (const false),
  require_source_for_every_observation (const true),
  allow_declared_as_observed (const false),
  mark_stale_after_ms?,
  require_repo_identity_for_code,
  require_session_identity_for_memory,
  require_url_identity_for_browser
}
```

The three policy constants reify the load-bearing invariants:

- `allow_mutation: false` -> ML-01 (no mutation)
- `require_source_for_every_observation: true` -> ML-07 (provenance)
- `allow_declared_as_observed: false` -> ML-03 (declared != observed)

---

## Sources

The closed source enum:

```text
git | filesystem | runtime_log | config | memory_store |
browser_dom | tool_result | cap_comlog | user_message | external_source
```

Every observation must declare a source; the schema's `required` list
makes this load-bearing.

---

## Recommended next actions

```text
proceed_to_adjustment   verdict=aligned; downstream may use B
resolve_mismatch        verdict=mismatch or partial
collect_evidence        verdict=unknown
refresh_observation     verdict=stale
log_contradiction       verdict=contradicted
probe_boundary          verdict=boundary_hidden; e.g. dom_probe, scroll
block                   blocking diff severity present
```

---

## Invariants

| Id | Statement | Enforcement |
|---|---|---|
| ML-01 | Mirror never mutates the observed system. | `mutability: "read_only"` const on every observation; `policy.allow_mutation: false` const |
| ML-02 | Mirror output is evidence, not authorization. | Schema has no `authorizes` / `releases` field |
| ML-03 | Declared state must not be treated as observed state. | Separate `declared_state` and `observed_state` slots; `policy.allow_declared_as_observed: false` const |
| ML-04 | Unknown must remain unknown. | `unknowns` array required on every frame; verdict=aligned forbidden when unknowns or boundary_hidden present (via `if/then`) |
| ML-05 | Stale evidence cannot confirm current state. | verdict=aligned forbidden when any observation has `freshness: stale` (via `if/then`) |
| ML-06 | Boundary-hidden state cannot be canonicalized. | Mirror does not emit canonical decisions; downstream Release Gate checks this. Schema enforces: any `boundary_signals[]` non-empty forces verdict in `{boundary_hidden, partial, unknown, mismatch}`, never `aligned` |
| ML-07 | Mirror must preserve provenance. | Every observation requires `source`; policy `require_source_for_every_observation: true` const |
| ML-08 | Mirror must separate raw observation from interpretation. | `observations[]` carries raw facts; `observed_state.derived_facts[]` carries interpretations |
| ML-09 | Mirror cannot self-upgrade into Verifier. | Schema has no quality verdict; verdict enum is observational only |
| ML-10 | Mirror cannot self-upgrade into Release Gate. | Schema has no `pass`/`needs_fix`/`blocked` verdict; recommended_next_action enum has no `release` |
| ML-11 | Mirror must be repeatable when possible. | Soft. Doc invariant. |
| ML-12 | Mirror must log contradictions instead of resolving them silently. | `contradictions[]` required (may be empty); verdict=contradicted forbidden when `contradictions[]` is empty (via `if/then`) |

---

## Relation to Adjustment Layer

Adjustment cannot fabricate `B`:

```text
Mirror:     "Here is the observed B."
Adjustment: "Given this B, what plausible A produced it, and what C is admissible?"
```

A Mirror frame whose verdict is `unknown` or `boundary_hidden` blocks
Adjustment from proceeding on a fabricated `B`. The Adjustment Layer
must consume a Mirror Frame, not a free-form description.

---

## Relation to Release Gate

Release Gate must require a Mirror Frame for any serious transition:

> A candidate release without a Mirror Frame -> `needs_fix` or `blocked`.

Operationally, the Release Gate's `evidence[]` for a code-change or
git-seal candidate should include references to the Mirror Frame fields:
branch, HEAD, `git status`, modified files, test freshness, tag
presence, repo identity. Without these, the gate has no `B` to gate on.

See [`./release_gate.md`](./release_gate.md).

---

## Relation to Memory Dreaming

For Memory Dreaming, Mirror reads the actual memory store state before
the Dream Compiler runs:

```text
Memory store
  -> Mirror Layer  (observed memory state)
  -> Dream Compiler
  -> candidate diff
  -> Release Gate
```

Mirror must distinguish: what is actually in the memory store; what
appears only in transcripts; what is a model interpretation; what is
already canonical; what is conflicting or stale. Without Mirror, Memory
Dreaming would recompile a fantasy of memory, not memory itself.

See [`../04_extensions/memory_dreaming.md`](../04_extensions/memory_dreaming.md).

---

## Relation to Browser / OpenClaw

Browser surfaces are partial by construction: a model sees only what the
current snapshot exposes. Mirror's job is to make that partial-ness
visible:

```text
visible_dom:   confirmed
below_fold:    unknown
hidden_tabs:   unknown
auth_state:    observed | unknown
current_url:   observed
form_values:   observed
save_status:   observed | stale
```

A read-only scroll or DOM probe is admissible Mirror action. `fill`,
`click`, `save` are not Mirror; they are executor actions and must pass
the Release Gate first.

---

## Relation to Context Hygiene

Mirror also serves as the input to context pruning:

```text
MirrorFrame
  -> classify context relevance
  -> prune stale / irrelevant / non-evidence blocks
```

A pruner that does not consult Mirror prunes blindly; a pruner that
consults Mirror can prune by `mirror_diff.kind` and observation
`freshness`.

---

## Algorithm

```text
build_mirror_frame(subject):
  1. Identify subject (repo, task, memory, browser page, config, runtime)
  2. Capture declared_state (what does user/model/system claim)
  3. Collect read-only observations across applicable sources
  4. Normalize each observation: source, claim, value, freshness, confidence
  5. Compare observed against expected anchors / policy
  6. Detect contradictions (conflicting evidence, stale output, missing source)
  7. Emit MirrorFrame:
       observations + unknowns + contradictions + boundary_signals
  8. Do not mutate anything.
```

---

## Audit log shape

```json
{
  "domain": "Observation",
  "node": "MirrorLayer",
  "status": "MirrorMismatch",
  "subject": "repo",
  "declared_state": "working tree clean",
  "observed_state_summary": "guard.ts modified but not staged",
  "verdict": "mismatch",
  "severity": "warning",
  "recommended_next_action": "resolve_mismatch",
  "timestamp": "2026-05-18T00:00:00.000Z"
}
```

---

## Canonical formula

```text
Mirror sees.
Adjustment explains.
Release Gate permits.
Executor acts.
```

Mirror Layer protects `B` from hallucination. Release Gate protects `C`
from premature canonicalization. The two layers are not interchangeable
and must not be collapsed.
