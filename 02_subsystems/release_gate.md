# Release Gate

The Release Gate is the layer that decides whether a candidate output can
move from `hypothesis / candidate / generated` to `released / accepted /
canonical / allowed-to-act`. It is a process predicate. It does not
canonicalize state on its own; it emits a verdict that an executor consults.

---

## Purpose

> Release Gate guards the transition from possible to permitted.

The model may propose. The verifier may inspect. The Release Gate decides
whether the candidate has the right to be released. Physical action that
is irreversible or destructive still requires a separate authorization
even when the gate passes.

This is the engineering response to the failure mode where a system
elegantly proves its own correctness inside its own axioms. The gate
treats model output as a `claim`, not as evidence. Evidence has to be
independent.

---

## Place in OCM

```text
Observation
  -> Hypothesis
  -> Candidate Transition
  -> Verification
  -> Release Gate
  -> Canonicalize / Apply / Block / Rework / Rollback
```

In Adjustment Layer form:

```text
Current state B
  -> infer prior cause A
  -> propose transition to desired C
  -> Verifier
  -> Release Gate
  -> commit C / reject C / rework C / rollback
```

---

## What the gate checks

Order matters. Identity and boundary checks run before quality checks: a
high-quality candidate that targets the wrong repo or memory store must be
blocked before its claim quality is even scored.

1. **Identity boundary** — right repo, right session, right memory store,
   right target.
2. **Provenance** — what produced the candidate; was the producer entitled
   to produce it.
3. **Evidence** — what supports the claims; is the evidence independent of
   the producer.
4. **Anchor compatibility** — does the candidate conflict with canonical
   anchors; if yes, is there a reconcile or retcon path.
5. **Boundary safety** — does the action stay inside permission, sandbox,
   and domain limits.
6. **Reversibility** — can the action be undone; if not, an explicit human
   authorization is required.
7. **Cost / budget** — does the transition fit observer budget and risk
   tolerance.
8. **Witness policy** — who confirmed; was the witness independent of the
   author.
9. **Role authority** — is the current agent permitted to release at all.
10. **Timing / appropriateness** — is this the right moment.

---

## Verdicts

Three canonical verdicts:

| Verdict | Meaning |
|---|---|
| `pass` | The candidate may be released to its declared target. Evidence is sufficient, no blocking conflicts, boundaries respected, rollback understood. |
| `needs_fix` | The intent is plausible but a precondition is missing. Examples: weak evidence, incomplete rollback, unclear witness, partial diff. |
| `blocked` | The candidate must not be released. Examples: canonical conflict with no reconcile path, boundary violation, destructive action without authorization, high risk. |

The existing CAP proxy gate code uses the names `release`,
`rewrite_required`, `block` for the same three states; the canonical
subsystem vocabulary is `pass` / `needs_fix` / `blocked` to match the rest
of the CAP schema family (lowercase enums, no spaces). The mapping is:

```text
release          == pass
rewrite_required == needs_fix
block            == blocked
```

A fourth runtime status `deferred` is reserved for cases where the gate
could not run (e.g. inputs missing); it is not a canonical verdict and
must be resolved by either rerunning the gate or escalating to human
review.

---

## Critical separation: semantic release vs physical seal

Release Gate `pass` is necessary but not sufficient for any
physically-irreversible action.

```text
ReleaseGate pass != git commit allowed
ReleaseGate pass != memory canonicalized automatically
ReleaseGate pass != irreversible action allowed
```

The full pipeline requires four distinct authorities:

```text
ReleaseGate:              "verifier considers the candidate ready"
PhysicalAuthorization:    "operator/user explicitly authorized the seal"
PhysicalBoundary:         "this concrete action class is allowed at all"
RepoIdentityBoundary:     "the action targets the intended repository"
```

A clean Release Gate `pass` that is followed by an unauthorized physical
write is a process failure. The executor, not the gate, is responsible for
checking the other three authorities before any irreversible step.

---

## Data model

The full schema lives at
[`../spec/release_gate.schema.json`](../spec/release_gate.schema.json).
The shape is:

```text
ReleaseCandidate = {
  id, target, current_state, inferred_cause?, proposed_state,
  claims[], evidence[], affected_anchors[], risks[], rollback_plan?,
  author_role, verifier_verdict?, created_at
}

ReleaseGateResult = {
  verdict, candidate_id, target,
  reasons[], missing_evidence[]?, anchor_conflicts[]?, boundary_violations[]?,
  required_fixes[]?, required_authorizations[]?,
  confidence, reversible, recommended_next_action,
  audit_log_ref?  // required when verdict == pass
}

ReleasePolicy = {
  require_evidence, min_evidence_strength,
  require_verifier, require_rollback_plan,
  allow_anchor_conflict,
  allow_model_self_approval,  // locked to false
  require_human_authorization_for_irreversible
}
```

Targets:

```text
memory_anchor | code_change | config_change | doc_claim |
strategy_decision | agent_output | tool_action | git_seal |
external_publication
```

Recommended next actions:

```text
release | revise | collect_evidence | run_verifier |
reconcile_anchors | rollback | request_human_authorization | block
```

---

## Default release policy

```text
require_evidence:                                  true
min_evidence_strength:                             medium
require_verifier:                                  true
require_rollback_plan:                             true
allow_anchor_conflict:                             false
allow_model_self_approval:                         false
require_human_authorization_for_irreversible:      true
```

`allow_model_self_approval` is a constant `false` in the schema. It is
not a knob.

---

## Invariants

The schema enforces the structural invariants directly. Tests enforce the
process invariants.

| Id | Statement | Where |
|---|---|---|
| RG-01 | Candidate cannot release itself. A `verdict: pass` requires an explicit `verifier_verdict` and an `author_role` that is not the verifier role. | Schema + test |
| RG-02 | Model output is not evidence by itself. `evidence` entries of kind `human_statement`, `runtime_observation`, `prior_anchor`, `test_result`, `log`, `diff`, `file_reference`, or `external_source` are evidence; bare model claims are not. | Schema enum |
| RG-03 | `pass` does not imply physical authorization. `verdict: pass` carries no field permitting commit / push / canonical write. Required authorizations remain in the executor's domain. | Doc invariant |
| RG-04 | Missing evidence cannot produce `pass`. `verdict: pass` requires `evidence` with `minItems: 1` and `min_evidence_strength` honored. | Schema |
| RG-05 | Canonical anchor conflict blocks release unless a reconcile or retcon path exists. `anchor_conflicts` non-empty with `verdict: pass` requires `recommended_next_action: reconcile_anchors`. | Schema |
| RG-06 | Irreversible transition requires human authorization. `reversible: false` with `verdict: pass` requires `required_authorizations` non-empty. | Schema |
| RG-07 | Release Gate emits verdict; it does not mutate canonical state. Schema has no `applied_diff` field. The executor reads the verdict and acts separately. | Schema shape |
| RG-08 | Every `pass` must leave an audit trace. `verdict: pass` requires `audit_log_ref`. | Schema |
| RG-09 | Verifier and Release Gate are separate roles. `author_role` must not be `release_gate`, and `verifier_verdict.role` must not be `author`. | Schema |
| RG-10 | Boundary violation dominates quality. `boundary_violations` non-empty forces `verdict: blocked` regardless of evidence quality. | Schema |

---

## Algorithm

```text
evaluate_release(candidate, policy):
  1. identity boundary       -> blocked on mismatch
  2. provenance              -> blocked if producer is the gate itself
  3. evidence                -> needs_fix if below min strength
  4. anchor compatibility    -> blocked if conflict and no reconcile path
  5. boundary safety         -> blocked on violation (dominates)
  6. rollback                -> needs_fix if missing; blocked if irreversible
                                and no human authorization
  7. cost                    -> needs_fix if exceeds budget
  8. verifier                -> propagate verifier verdict (pass / needs_fix /
                                blocked) but never upgrade a verifier blocked
                                to pass
  9. emit verdict + audit_log_ref
```

The verdict is the strictest result across all checks. A `blocked` at
step 5 is not overridden by a `pass` at step 8.

---

## Relation to Memory Dreaming

The Dream Compiler relies on Release Gate as its canonicalization
boundary:

```text
old memory store + transcripts + telemetry
  -> dream candidate store
  -> diff
  -> verifier
  -> Release Gate
  -> approved canonical memory store
```

The forbidden route is `dream output -> direct canonical memory`. Without
the gate Memory Dreaming would become an auto-canonicalizer for
hallucinated traces.

The Dream Compiler also produces four exit kinds that the gate must
classify:

```text
canonicalize    candidate -> L1-C, no conflict
reconcile       anchor A + candidate B -> merged anchor C
retcon          old anchor superseded with explicit reason; new anchor
                proposed; old preserved in L1-D
rollback        candidate or change recognized as harmful;
                state restored to last approved snapshot
```

See [`../04_extensions/memory_dreaming/framework.md`](../04_extensions/memory_dreaming/framework.md)
for the dream-side semantics. The gate side is the same regardless of
producer.

---

## Audit log shape

Every `pass` must reference a COM-Log event:

```json
{
  "domain": "Governance",
  "node": "ReleaseGate",
  "status": "ReleaseGatePassed",
  "candidate_id": "cap-layer-042",
  "target": "code_change",
  "verdict": "pass",
  "reasons": ["evidence present", "rollback covered", "no anchor conflicts"],
  "audit_log_ref": "com_log/2026-05-18/release_gate/cap-layer-042",
  "timestamp": "2026-05-18T00:00:00.000Z"
}
```

Equivalent statuses for the other two verdicts:

```text
ReleaseGatePassed
ReleaseGateNeedsFix
ReleaseGateBlocked
ReleaseGateDeferred   (runtime-only, not a canonical verdict)
```

---

## Why this exists

The gate is the engineering answer to a Goedelian failure mode: a system
can prove its own correctness inside its own axioms. Without an external
gate the system silently canonicalizes its own claims.

```text
Independent evidence
+ Witness
+ No anchor conflict
+ Reversible-or-authorized
+ Right to release
=> permitted
```

Anything short is `needs_fix` or `blocked`. Persuasiveness of the
candidate is not a substitute for any of the five.

---

## Existing implementation surfaces

- [`../reference/python/cap/proxy_release_gate.py`](../reference/python/cap/proxy_release_gate.py)
  is the deterministic lexical proxy used by the LLM dialogue benchmark.
  It scores generated text against patterns and emits
  `release / rewrite_required / block`. These three states are the
  canonical `pass / needs_fix / blocked` under the equivalence above.
- [`../reference/python/cap/release_gate_adjudication.py`](../reference/python/cap/release_gate_adjudication.py)
  prepares boundary cases for human adjudication when the proxy gate
  disagrees with a blinded reviewer.
- Validation artifacts live in
  `validation_artifacts/llm_dialogue_benchmark/hard_holdout/`, including a
  v0.2 preregistration and per-model gate reports.

The subsystem doc and `release_gate.schema.json` are the canonical
specification; the proxy implementation is one realisation of it.
