# Architectural Groundhog Loop

**Unofficial draft. Status: Research-only. NON-CANONICAL.**

> ✅ **PROMOTED.** This candidate's evidence and reasoning were canonically published as
> [`AICE-620`](../codes/AICE-620.md). This dossier is retained as promotion provenance — it
> records the state of the class *before* publication and is **not** updated to track later
> edits to `AICE-620.md`, which is authoritative. `status` and `canonical code` below are the
> historical values at candidate time and are preserved, not corrected, per
> `WITHDRAWN != DELETED`-style retention; see [Authority status](./README.md#authority-status).

Aliases: *Displaced Execution Authority Returns*; *Canonical Path Exists, Competing Authority
Returns*; «Це ж було вже».

## Identity

```
working title           Architectural Groundhog Loop
machine name            CANONICAL_EXECUTION_PATH_REINTRODUCTION
status                  EVIDENCE_BACKED_PROVISIONAL   (historical, at candidate time)
canonical code          UNASSIGNED                    (historical, at candidate time)
number reserved         false                         (historical, at candidate time)
operator-selected code  AICE-620   (future publication identity only, at candidate time)
promotion_status        PROMOTED
promoted_to             AICE-620
registry                EXCLUDED
schema                  EXCLUDED
defined-code count      EXCLUDED
static skills           EXCLUDED
```

```
PROPOSED_CODE           != CANONICAL_CODE
OPERATOR_SELECTED_NUMBER != REGISTRY_ASSIGNMENT
EVIDENCE_BACKED         != PUBLISHED
```

The operator has named `AICE-620` as the intended future publication identity. That naming is
recorded here as provenance only. It assigns nothing, reserves nothing, and does not alter the
canonical unassigned set (`AICE-600`, `AICE-601`, `AICE-603`, `AICE-617` remain unassigned at
`389ac4b`; `AICE-620` is outside the registry's declared range entirely).

## Source and provenance limits

The source episode spans three repositories. None of them is this one.

| Repository | Role | Pinned state |
|---|---|---|
| `cap-processor` | primary current evidence | HEAD `f64c8d8` |
| `coder-quality-v1-integration` | historical source, read-only forensic use only | HEAD `4e682ef` |
| `Shard-Theory` (parent of this repo) | governance contract surface | `CAP-MCP-CLIENT-CONTRACT.md` |

`coder-quality-v1-integration` is **not** an active MCP source, runtime dependency, canonical
repository, migration target, or implementation base. It is cited solely because
`cap-processor`'s own root commit `c0eb8b6` (2026-07-12) is a bulk materialization that carries
no pre-materialization chronology: `git log -S 'COMPATIBILITY WRAPPER'` inside `cap-processor`
returns only that one commit. The displacement history therefore is not observable from
`cap-processor` alone.

Provenance classes used below:

```
PRIMARY_PERSISTED         committed bytes or persisted runtime artifacts
HISTORICAL_CORROBORATION  commit-message text, used only to date or label, never to establish
TEST_EXECUTION            runtime artifact produced by a test suite, not an operator run
NOT_FOUND_IN_BOUNDED_EVIDENCE_UNIVERSE
```

Stated limits:

- No `loop_jobs` database row was located inside the three named repositories. The durable
  job table's *runtime* exercise is `NOT_FOUND_IN_BOUNDED_EVIDENCE_UNIVERSE`. Its *definition*
  and its *invocation path* are `PRIMARY_PERSISTED`. Absence of the DB here is not evidence
  that no such row has ever existed — a `.nsl` runtime base outside the bounded universe was
  observed to exist and was deliberately not read.
- Several `autoloop_*` runtime records carry test-shaped objectives (`'x'`, `'  '`,
  `'fix bug'`) and are classified `TEST_EXECUTION`. They are used to demonstrate *mechanism*,
  never to claim production usage.
- No claim below rests on a commit message alone. Every load-bearing claim cites file bytes.

## Core definition

An execution path that previously possessed or could exercise independent control authority is
explicitly subordinated, displaced, or reduced to a thin adapter when another path becomes the
canonical execution spine. The displaced path remains executable and later regains independent
lifecycle, identity, state, routing, retry, admission, mutation, cancellation, lease, or
terminal authority **without a new premise uniquely requiring duplicated control authority**,
recreating a competing execution topology that the earlier architectural decision was intended
to remove.

```
CANONICAL_SPINE_ESTABLISHED
AND COMPETING_AUTHORITY_DISPLACED
AND CANONICAL_SPINE_REAFFIRMED
AND DISPLACED_PATH_REMAINS_EXECUTABLE
AND DISPLACED_PATH_REGAINS_INDEPENDENT_AUTHORITY
AND NO_NEW_PREMISE_UNIQUELY_REQUIRES_DUPLICATED_AUTHORITY
AND MATERIAL_WORKFLOW_EFFECT_EXISTS
  -> CANONICAL_EXECUTION_PATH_REINTRODUCTION
```

The incident admits two forms. **Form A**: a subordinate path gains authority. **Form B**: a
former authority is displaced and later returns. The source episode is Form B. The returning
path did **not** originate subordinate, and this record makes no such claim.

## Observed episode

### E1 — initial authority (2026-07-02)

`coder-quality-v1-integration@c62c009` introduces `MCP/cap_auto_task_loop_v0.py` (+541 lines).
Its docstring declares it a *"MCP-owned BOUNDED coder/verifier loop controller ABOVE the
existing sealed one-pass task-controller"* owning *"a bounded retry budget (max_loops <= 2)"*,
deterministic retry gates, and deterministic escalation outputs. `run_auto_task` is born
**authoritative**.

### E2 — explicit displacement (2026-07-06 16:19)

`coder-quality-v1-integration@d2041a2` (`MCP/cap_auto_task_loop_v0.py`: +68 / −136) removes from
`run_auto_task`, in one commit: `_classify_blocked`, the `COMMIT_ALLOWED` terminal decision, the
`COMPLETED_NO_LIVE` terminal, the `INFRA_BLOCKED` terminal, the same-failure-fingerprint
escalation, the `n >= max_loops` escalation, the missing-receipt gate, and every
`rollback_status` retry gate.

The receiving module `MCP/cap_fsm_loop_transition_v0.py`, added in the same commit, states in
its own bytes:

> "Before this slice the cross-attempt decision ladder (retry budget, same-failure fingerprint
> escalation, rollback/evidence gates, max-loop escalation, terminal classification, and the
> COMMIT_ALLOWED decision) lived INSIDE run_auto_task — i.e. the autorunner was the hidden
> lifecycle owner. That ladder now lives here … run_auto_task becomes a thin driver that
> executes one bounded attempt and OBEYS the returned transition."

This is displacement stated in the displaced-from module's replacement, not in a commit message.

### E3 — reaffirmation (2026-07-06 23:28 → 2026-07-07 00:39, and standing)

- `b4885a1` adds `parent_loop_id` + `parent_lifecycle_path` to the returned summary as, in its
  own docstring bytes, *"the FSM parent lifecycle handle as the primary identifier"*.
- `292861f` adds `MCP/cap_fsm_driver_loop_v0.py` (`drive_loop`) and re-exports it through
  `MCP/cap_probe_workflow.py` with the comment *"re-exported here so `cap_probe_workflow.drive_loop`
  is the declared owner. run_auto_task is now a compatibility wrapper …"*.
- The re-export mechanism is the reaffirmation instrument: at `f64c8d8`,
  `cap_probe_workflow.py:60` binds `decide_loop_transition` and `cap_probe_workflow.py:67` binds
  `drive_loop`, under the comment at line 64 naming the workflow module *the declared owner*.
- `Shard-Theory/CAP-MCP-CLIENT-CONTRACT.md:10` — *"MCP is the workflow/control plane."*
  Line 12 — *"Call `start_task` before any non-trivial work. Do not skip or substitute."*
  Line 15 — *"Do not bypass, self-route, or substitute a local fallback."*
  The contract contains **zero** occurrences of `run_auto_task` or any `loop_*` tool.

### E4 — survival

`git log --diff-filter=D -- MCP/cap_auto_task_loop_v0.py` is empty in `cap-processor`. The path
was never deleted, never disabled, never expiry-sealed. At `f64c8d8` it is a registered,
model-facing MCP tool: `cap_probe_loop_mcp.py:21-36` declares `Tool(name="run_auto_task", …)`,
`cap_probe_mcp.py:2266` splices `LOOP_TOOLS` into the advertised catalog, and
`cap_probe_mcp.py:4049-4050` dispatches it.

### E5 — authority return (2026-07-13 → 2026-07-14)

**`c6cd3d5` (2026-07-13 20:06 +0300)** adds `MCP/cap_probe_loop_jobs.py`,
`MCP/cap_probe_loop_mcp.py`, `MCP/cap_probe_loop_worker.py` (+664 / +121 / +108) and takes
`cap_probe_mcp.py` to +4 / −149. `run_auto_task` becomes a submit-and-return tool over a detached
job with its own primary identity.

**`59a033a` (2026-07-14 02:50 +0300)** is where control authority returns. Two byte-level facts,
both still present at `f64c8d8`:

1. `cap_auto_task_loop_v0.py:761` intercepts the FSM's own transition kinds:

   ```python
   if _is_coder_path_active() and transition.get("kind") in (_fsm_txn.KIND_RETRY, _fsm_txn.KIND_ESCALATE):
       return _coder_gate_renderer(n)
   ```

   `_coder_gate_renderer` (line 716) calls `_rea.decide_coder_transition` (line 719), a second
   cross-attempt decision function with its own `policy_version = "coder_budget.v0"` at
   `cap_coder_reassignment_v0.py:273-306`, returning `retry_same_job` / `reassign` /
   `terminal_budget_exhausted` / `terminal_nonreassignable`. Returning `None` signals RETRY to
   `drive_loop`. **An FSM `KIND_ESCALATE` can therefore be converted into another attempt by the
   loop plane.** The comment introduced with it says so plainly: *"the deterministic coder
   budget gate owns retry/reassign/terminate for a coder FAILURE."*

2. `cap_auto_task_loop_v0.py:899-909` substitutes the FSM driver's bound:

   ```python
   effective_max_loops = (
       _rea.MAX_TOTAL_CODER_EXECUTIONS_PER_PARENT_LOOP     # 4
       if task_type == TASK_TYPE_CODE_CHANGE
       else max_loops
   )
   ...
   return _driver.drive_loop(max_loops=effective_max_loops, hooks=hooks)
   ```

   The caller-supplied `max_loops` is hard-validated to `[1, MAX_LOOPS_CEILING]` with
   `MAX_LOOPS_CEILING = 2` at lines 60 and 849-852 — and then discarded on the code-change path
   in favour of a constant owned by the loop plane. Line 631 feeds the same substituted value
   into `loop_state["max_loops"]`, so `decide_loop_transition` evaluates its budget rule against
   a bound the loop plane chose. `git log -S 'effective_max_loops'` returns exactly one commit,
   `59a033a`; the string is absent at `c6cd3d5`.

`cap_probe_workflow.py` contains **zero** occurrences of `decide_coder_transition` or
`cap_coder_reassignment` — the deliberate re-export that made `decide_loop_transition` and
`drive_loop` FSM-plane-owned was not repeated for the returning decision function.

### E6 — actual execution after the return

Machine-derived from `cap-processor` at `f64c8d8`:

- `runtime_local/mvp_auto_runner_operator_receipts/`: 20 files matching `autoloop_*`, 6 distinct
  loop ids, earliest `20260713T123803Z`, latest `20260722T131734Z`. Receipt
  `autoloop_e8ae577e7a2ff7a4_a1-20260722T131734Z.json` postdates both `c6cd3d5`
  (2026-07-13T17:06:14Z) and `59a033a` (2026-07-13T23:50:44Z). `PRIMARY_PERSISTED`.
- `MCP/workflow_loop_records/`: 9 distinct `autoloop_*` ids, each with a `.json` snapshot and a
  `.lifecycle.json` handle. `autoloop_47956c60f214e1a3` (2026-07-24T21:54:34Z, `mode: live`,
  objective *"Add a focused regression test asserting cap_scout_report_v0.normalize…"*) records
  a full `loop_started → attempt_started → transition_decided → loop_terminal` sequence.
  `PRIMARY_PERSISTED`.
- `autoloop_a863c54d1ddb7f1a` (`TEST_EXECUTION`, objective *"wire reassignment end to end"*)
  demonstrates the override end-to-end: `"loop_attempts": 3`; attempt 2's recorded
  `transition_decided` is `"kind": "escalate"`; the `state_trace` that follows it is
  `RETRY_ALLOWED`; attempt 3 runs. The FSM escalated and the loop retried.

### E7 — material effect

Bound below.

## Authority comparison

Cells cite `coder-quality-v1-integration` for the first two columns and `cap-processor@f64c8d8`
for the third.

| Authority dimension | Before displacement (`c62c009`) | After FSM canonicalization (`292861f`) | After reintroduction (`f64c8d8`) |
|---|---|---|---|
| Primary task/job identity | `run_auto_task`-derived `autoloop_*` base id | FSM parent lifecycle handle (`b4885a1`) | `loop_jobs.loop_id` PRIMARY KEY (`cap_probe_loop_jobs.py:50`); the FSM handle is nullable column `fsm_parent_loop_id` (line 63) |
| Lifecycle state | in-memory attempt state only | `drive_loop` iteration; no persisted job state | 8 states + `TERMINAL` frozenset, persisted (`cap_probe_loop_jobs.py:24-35`, table lines 49-69) |
| Transition authority | `run_auto_task` decision ladder | `decide_loop_transition`, re-exported (`cap_probe_workflow.py:60`) | FSM retained for PASS/blocked kinds; `KIND_RETRY`/`KIND_ESCALATE` intercepted on the coder path (`cap_auto_task_loop_v0.py:761`) |
| Retry budget | owned by `run_auto_task` (`c62c009` docstring) | owned by FSM (`d2041a2` removals) | bound supplied by loop plane: `effective_max_loops` (`cap_auto_task_loop_v0.py:899-909`, fed to FSM at line 631) |
| Reassignment ledger | NOT_APPLICABLE | NOT_APPLICABLE | loop plane: `coder_budget` (line 539), `reassignment_history` (line 543), `_rea.advance_reassignment` (line 605) |
| Routing / model selection | runner (`cap_model_assignment_policy`) | runner | runner — `assign_model` remains sole selector; `cap_probe_workflow.py` re-export absent for `decide_coder_transition` but no model authority moved |
| Admission | NOT_ESTABLISHED | NOT_ESTABLISHED | `loop_jobs.submit_loop` + `request_digest` (`cap_probe_loop_jobs.py:114-167`) |
| Cancellation | NOT_APPLICABLE | NOT_APPLICABLE | loop plane: `cancel_requested` column (line 61), `worker_finish_cancel` (line 494), `mark_complete` refuses when cancel is set (lines 541, 554) |
| Leases | NOT_APPLICABLE | NOT_APPLICABLE | loop plane: `_LOOP_LEASE_SECONDS = 240` (line 37), `claim_loop` (line 306), `reap_stale_loops` (line 622) |
| Terminal classification | `run_auto_task` (`_classify_blocked`) | FSM decides kind; driver renders `LOOP_*` by design | FSM for non-coder kinds; loop plane emits `LOOP_CODER_BUDGET_EXHAUSTED` / `LOOP_ESCALATED` from its own gate (`cap_auto_task_loop_v0.py:733-754`) |
| Terminal result persistence | receipt files only | receipt files only | `terminal_result_json` column (`cap_probe_loop_jobs.py:64`), written by `mark_complete` (line 565) |
| Apply / rollback authority | runner / Driver | runner / Driver | runner / Driver — UNCHANGED |

Two dimensions are honestly negative: **routing/model selection** and **apply/rollback** never
returned. This candidate does not claim a total authority reversal.

## Trigger predicates — all required

**T1 — CANONICAL_EXECUTION_SPINE_ESTABLISHED.** `d2041a2` moves the cross-attempt ladder into
`cap_fsm_loop_transition_v0` and re-exports it through `cap_probe_workflow` so that, in the
commit's own words and in the module's own bytes, the FSM plane owns the transition; `292861f`
extends this to loop iteration via `drive_loop`. `cap_probe_workflow.py:60,64,67` still carries
that binding at `f64c8d8`.

**T2 — COMPETING_PATH_PREVIOUSLY_DEMOTED_OR_DISPLACED.** Established by the `d2041a2` removals
enumerated in E2 and by `cap_fsm_loop_transition_v0.py`'s own ownership paragraph. The phrase
*"run_auto_task is now a compatibility wrapper"* appears in `cap_probe_workflow.py` at
`292861f`, and *"run_auto_task is now a COMPATIBILITY WRAPPER / SHELL"* is still in
`cap_auto_task_loop_v0.py`'s docstring at `f64c8d8` (lines 3-5). The path did **not** originate
subordinate; it was displaced.

**T3 — CANONICAL_SPINE_LATER_REAFFIRMED.** `b4885a1` + `292861f` + the standing client contract
(`CAP-MCP-CLIENT-CONTRACT.md:10,12,15`). Honest limit: the parent lifecycle handle introduced by
`b4885a1` is `observe_only` by its own bytes (`cap_probe_workflow.py:409-416`), so the
reaffirmation is a *declaration plus a re-export binding*, not an enforcement mechanism. See the
AICE-610 differential.

**T4 — DISPLACED_PATH_REMAINED_EXECUTABLE.** Never deleted (`--diff-filter=D` empty); live and
advertised as an MCP tool at `cap_probe_loop_mcp.py:21-36` + `cap_probe_mcp.py:2266,4049-4050`.
Not mere source presence.

**T5 — DISPLACED_PATH_REGAINED_INDEPENDENT_AUTHORITY.** Established on **retry authority** and
**cross-attempt transition authority** by `cap_auto_task_loop_v0.py:761` and `:899-909`, and on
**job identity / lifecycle state / terminal result persistence** by
`cap_probe_loop_jobs.py:24-69`. The distinction demanded by the ruling is respected: the
`loop_jobs` row on its own is transport bookkeeping; the *authority* claim rests on the
transition interception and the budget substitution, neither of which is transport.

**T6 — NO_NEW_PREMISE_UNIQUELY_REQUIRES_DUPLICATED_AUTHORITY.** A new operational requirement
genuinely existed: `c6cd3d5` states it as moving the loop *"out of the long synchronous MCP
request"*. This record does **not** deny it. The narrow finding is:

```
ASYNC_TRANSPORT_NEEDED  !=  SECOND_EXECUTION_FSM_NEEDED
```

- The async premise explains `loop_jobs`, the detached worker, leases, and cancellation. Those
  fall inside the legitimate-async-adapter boundary and are **not** charged here.
- The async premise does **not** explain the retry-authority return. `effective_max_loops` and
  the `KIND_RETRY`/`KIND_ESCALATE` interception are absent at `c6cd3d5` and enter only at
  `59a033a`, whose stated premise is scorer reassignment — a different requirement that has no
  synchrony component.
- `c6cd3d5`'s own message asserts *"no new DB/FSM/selector"*, i.e. the author's contemporaneous
  position was that the async requirement did **not** require a second lifecycle authority.
  That claim is `HISTORICAL_CORROBORATION` and is used only as a necessity witness *against*
  necessity, never to establish topology.
- No design note, ADR, or markdown surface in `cap-processor` mentions `decide_coder_transition`
  or `coder_budget.v0`. A unique-necessity witness for placing the returning decision outside
  the FSM plane is `NOT_FOUND_IN_BOUNDED_EVIDENCE_UNIVERSE`.

**T7 — AUTHORITY_REINTRODUCTION_ACTUALLY_OCCURRED.** E6. The path is exercised, not dormant.

```
DORMANT_EXECUTABLE_PATH  !=  REINTRODUCED_EXECUTION_AUTHORITY
```

**T8 — MATERIAL_WORKFLOW_EFFECT_ESTABLISHED.** Three consequences, strongest first.

*DUPLICATED_RETRY_AUTHORITY.* On the code-change path the executed attempt bound is `4`, chosen
by `cap_coder_reassignment_v0.MAX_TOTAL_CODER_EXECUTIONS_PER_PARENT_LOOP`, while the same file
declares `MAX_LOOPS_CEILING = 2` (line 60), validates the caller's argument against it (lines
849-852), and documents *"max_loops <= 2"* in its module docstring (line 14). Two retry
authorities coexist and the effective bound is the one neither surface advertises. The runtime
record `autoloop_a863c54d1ddb7f1a` shows `loop_attempts: 3` with `RETRY_ALLOWED` recorded
immediately after an FSM `escalate`.

*AUTHORITATIVE_LINEAGE_FRAGMENTATION.* Two disjoint identity namespaces, both persisted, with no
join in either direction: `MCP/workflow_sessions/` holds 67 session files (34 of them
`anchored_*`), of which **0** contain the substring `autoloop` and **0** contain `loop_id`;
`MCP/workflow_loop_records/` holds 9 `autoloop_*` snapshots plus 9 lifecycle handles, of which
**0** contain `anchored_`. None of
`cap_auto_task_loop_v0.py`, `cap_probe_loop_jobs.py`, `cap_probe_loop_mcp.py`,
`cap_probe_loop_worker.py`, `cap_fsm_driver_loop_v0.py`, `cap_fsm_loop_transition_v0.py` calls
`start_task`, `process_step_result`, or `_save_workflow` — the only occurrences of those names
across the six files are three docstring lines disclaiming the calls.

*CONTRACT_EXECUTION_CONTRADICTION.* `CAP-MCP-CLIENT-CONTRACT.md:12` requires `start_task` and
forbids substitution; `run_auto_task` is an advertised, exercised MCP entrypoint that reaches no
`start_task`. `grep -rn 'run_auto_task' --include='*.md'` over `cap-processor` returns **zero**
hits: the path is neither declared canonical nor declared retired anywhere in governance prose.

## Forbidden inference

```
THIN_ADAPTER                     != COMPETING_CONTROL_PATH
CANONICAL_IN_PROSE               != CANONICAL_IN_EXECUTABLE_TOPOLOGY
DEMOTION_IN_PROSE                != DEMOTION_IN_EXECUTABLE_TOPOLOGY
NEW_TRANSPORT_REQUIREMENT        != NEW_LIFECYCLE_AUTHORITY_REQUIREMENT
NEW_REQUIREMENT_EXISTS           != UNIQUE_NECESSITY_FOR_DUPLICATED_AUTHORITY
PATH_STILL_CALLABLE              != PATH_HAS_RETURNED_AS_AUTHORITY
RETIRED_AUTHORITY_STILL_EXECUTABLE != RETIRED_ARCHITECTURE
CLAIM_IN_COMMIT_MESSAGE          != PERSISTED_INDEPENDENTLY_READABLE_EVIDENCE
NOT_FOUND_IN_BOUNDED_EVIDENCE_UNIVERSE != CONTRARY_EVIDENCE_CANNOT_EXIST
```

Several front doors are legitimate when they converge immediately: one job identity, one
lifecycle, one state model, one routing decision, one retry ledger, one terminal result. Entry
multiplicity is not the incident. Non-convergence is.

## False-positive boundary

### Negative control 1 — legitimate authority migration (must not fire)

`cap-processor`, all 2026-07-24: `4c91b0c` attaches a scout-scorer **shadow** to `assign_model`
→ `1ed3e59` makes scorer selection **authoritative** → `573a267` **retires** legacy scout
selector authority → `d2d27f2` **fully decommissions** the legacy runtime, deleting
`_scout_scorer_shadow` from `cap_model_assignment_policy.py`, deleting
`test_p4b2a_scout_scorer_shadow_v0.py` (119 lines), and adding
`test_p4b2e_legacy_scout_runtime_decommissioned_v0.py` to assert the decommissioning holds.

This is the same repository, the same month, and the same kind of authority transfer — closed
properly. It defeats **T4**: the displaced path did not remain executable. The contrast is the
point: this project demonstrably knows how to retire competing authority. It did so for the
*selector* and not for the *execution spine*.

### Negative control 2 — legitimate async adapter (must not fire)

An adapter that owns a transport id, a queue position, a cancellation request, and a
worker lease, while the semantic lifecycle, routing, retry policy, and terminal classification
stay with the canonical spine, defeats **T5**. Had `59a033a` never landed, `loop_jobs` alone
would sit on this side of the line, and this record would not exist.

### Negative control 3 — thin adapter with immediate convergence (must not fire)

An entrypoint that translates input and calls `start_task`, producing one WorkflowState and one
terminal, defeats **T5** and **T8**. Multiple front doors are not the incident.

### Negative control 4 — dormant reactivation surface (must not fire)

A displaced path that regains authority in code but is never exercised defeats **T7**. It is a
risk surface, not an incident.

### Negative control 5 — genuinely invalidating new premise (must not fire)

If a new requirement made the single-spine design unworkable and the record showed the second
lifecycle authority was the minimum way to satisfy it, **T6** fails and the correct terminal is
`BLOCKED_AICE_620_NEW_PREMISE_UNRESOLVED`, not a classification.

### Positive control (should fire)

The source episode: E1 → E7 above.

## Comparison with canonical AICE

### Not AICE-610 — *Control Exists, Enforcement Not Found* (nearest neighbour)

The declaration that the FSM is the single authority is unenforced, which is AICE-610-shaped and
this record concedes the overlap. The additional, distinguishing requirement here is historical
and directional: the path that now escapes enforcement is the *same* path from which the
authority was deliberately taken, and it *regained* that authority afterwards. AICE-610 needs no
prior displacement and no return. A repository that never displaced anything can still be
AICE-610; it cannot be this.

### Not AICE-601 — *Minimum Sufficient Mechanism Bypass*

A second job/lifecycle system is arguably larger machinery than the problem required, and an
AICE-601 reading of `c6cd3d5` alone is defensible. This record is not about the sizing of the
new mechanism; it is about the authority loop — existed, displaced, survived, returned. Note
that AICE-601 is **unassigned** in the canonical registry at `389ac4b`; it is referenced here as
a taxonomy neighbour only.

### Not AICE-603 — *Governance-Induced Service Unavailability*

Governance friction may explain why an alternate route was attractive. That would be a claim
about motive, which this record does not make. AICE-603 concerns the withholding event; this
concerns the later architecture of the route. AICE-603 is likewise **unassigned** at `389ac4b`.

### Not AICE-605 / *Implementation Exists, Release Not Found*

Both concern the implementation↔release axis. Nothing here is missing an implementation or a
release; both execution paths are implemented and both run.

### Open taxonomy question

If a future episode shows a displaced path regaining authority *and* the displacement itself was
never enforced, AICE-610 and this candidate would fire together. Whether that is a merge
condition or a legitimate co-occurrence is unresolved and is left to a promotion episode.

## Portable CAP enforcement requirement (non-implemented)

None of the following is implemented, and this record does not request that it be implemented.

A portable check would need to derive, from executable bytes rather than prose:

1. the set of paths that can produce an independently authoritative terminal result;
2. for each, whether it converges on the declared spine — concretely, whether it reaches
   `start_task` / `process_step_result` or creates a `WorkflowState`;
3. whether any module supplies a bound or a transition decision to the declared authority rather
   than receiving one from it (the `effective_max_loops` shape);
4. whether an entrypoint advertised to models appears in the governance contract at all.

Check 3 is the load-bearing one and the hardest: it is the difference between a driver being
*called by* the FSM and a driver *parameterizing* the FSM.

```
ENFORCEMENT_DESIGN != ENFORCEMENT_IMPLEMENTED
```

## Required terminal

An episode recording this candidate ends with exactly one terminal. This one ended with
`AICE_620_CANDIDATE_RECORDED_AWAITING_VERIFIER`, superseded on verifier PASS by
`AICE_620_CANDIDATE_RECORDED_AND_VERIFIED`.

## Promotion gate

Not satisfied by this record. Canonical promotion is a separate episode requiring, at minimum:
operator acceptance; explicit number assignment through the registry (the operator's `AICE-620`
selection is not one); a resolution of the AICE-610 overlap above; registry, schema, code-doc,
example, and checker updates; tests; commit; publication; and remote readback.

Recording this candidate reserves no number and modifies no canonical surface.

## Verification status

```
author                   Claude Opus 4.8 (this episode)
canonical mutations      0
registry / schema        untouched
staged bytes             0
commits                  0
pushes                   0
independent verification pending
```
