# CAP-Guardrails / Anti-Freeze Layer

CAP-Guardrails is the cross-cutting meta-layer that protects CAP from becoming the
frozen system it was built to detect. Without it, an over-zealous CAP runtime can
spend its entire `ActionBudget` auditing the audit and never let a transition
happen. The layer emits routing directives only: it never mutates anchors, never
commits, never releases.

---

## Purpose

> CAP defends against foolish action.
> CAP-Guardrails defend against foolish inaction dressed up as wisdom.

The layer answers two questions in real time:

1. Is the current CAP pipeline doing more cost than the task warrants?
   (the audit-payback problem)
2. Is the inaction we are committing right now a real consequence of missing
   resources, or a hidden form of avoidance, freeze, or budget self-justification?

---

## Layer Placement

CAP-Guardrails is **not** an additional sequential stage in the chain
`Mirror → Looking-Glass → Context Hygiene → Adjustment → Verifier → Release Gate`.
It sits **across** the whole chain as cross-cutting supervision over resource spend:

```text
       User Intent
            │
       Mirror Layer (determines target state B)
            │
  [CAP-Guardrails meta-supervision] ──▶ Fast Mode / Stop / Escalation
            │
Looking-Glass / DSSD / Role Orchestration / Context Hygiene
            │
       Adjustment Layer (selects route into C)
            │
         Verifier
            │
       Release Gate
            │
        Executor
```

It operates at two points:

1. **Input-gating** — decides whether a task takes the heavy analytical path or the
   lightweight **Fast Mode** path.
2. **Inline-auditing** — detects loops, audit recursion, and endless verification,
   and forcibly re-routes.

The layer issues **routing directives exclusively**. It never alters anchors, never
performs commits, never issues releases.

---

## Ontology

Each closed enum below is defined **exactly once**. Later sections reference an enum
by name and must not re-list its values inline.

### Risks (closed enum)

| Risk | Meaning |
|---|---|
| `analytical_paralysis` | Audit/risk-checking consumed more resource (tokens, time) than the action itself was meant to cost. |
| `budget_underestimation` | A "no budget" claim is a psychological rationalization or resistance, not an objective fact. |
| `frozen_container` | Quarantine / Cold Storage became a data graveyard; nothing returns to the live loop. |
| `fast_mode_abuse` | Speed / the lightweight path used to bypass Verifier, Release Gate, or authorization. |
| `escalation_avoidance` | A critical conflict, vulnerability, or irreversible signal was ignored or concealed. |

### Guardrail Actions (closed enum)

| Action | Meaning |
|---|---|
| `enter_fast_mode` | Route the task onto the lightweight computational track. |
| `require_reality_floor` | Run the grounding procedure for soft budget claims against facts. |
| `schedule_patrol_gap` | Emit a patrol contract so frozen items can be re-examined / thawed. |
| `force_escalation` | Forcibly hand control to a higher level (Human / Upstream). |
| `stop_audit` | Immediately break the checking/decomposition loop. |
| `take_minimal_action` | Perform the simplest safe action and close the tick. |
| `hold_for_human` | Block execution until explicit human confirmation. |
| `no_action` | Nothing detected; proceed on the normal OCM chain. |

These are routing actions. The layer does not mutate; it tells the upstream OCM
pipeline what to do next.

### Fast Mode Verdicts (closed enum)

| Verdict | Meaning |
|---|---|
| `FAST_ALLOWED` | The cheap path is admissible. |
| `FAST_DENIED` | Cheap path refused; use the normal OCM/CAP pipeline. |
| `ESCALATE_REQUIRED` | A critical conflict / boundary / irreversibility is present; escalate. |

### Forbidding Signals (closed enum)

Any one of these signals forbids Fast Mode (forces `FAST_DENIED`):

| Signal | Gloss |
|---|---|
| `git_seal` | Repository / commit lock. |
| `memory_canonicalization` | Canonical-memory write / RAG-core rewrite. |
| `security_boundary` | Crossing a security boundary. |
| `repo_identity_mismatch` | Repository identity mismatch. |
| `live_browser_write` | Direct write / action in a live browser. |
| `financial_decision` | Financial decision. |
| `legal_decision` | Legal decision. |
| `medical_decision` | Medical decision. |
| `destructive_operation` | Destructive / delete operation. |
| `new_architectural_frame` | Creation of a new architectural frame. |
| `anchor_conflict` | Direct conflict of active anchors. |
| `high_uncertainty` | High entropy / uncertainty. |

### Soft Budget Claim Kinds (closed enum)

Claims that represent potential avoidance and must pass through the `RealityFloor`:

```text
no_time
no_energy
too_risky
let_us_defer
too_expensive
not_ready
context_overflow
```

### Patrol Freeze Reasons (closed enum)

```text
contamination
overheat
weak_provenance
anchor_conflict
awaiting_evidence
intentional_park
```


### NO_MAP_NO_WORK Scout Levels (closed enum)

```text
LEVEL_0
LEVEL_1
LEVEL_2
```

### NO_MAP_NO_WORK Need Verdicts (closed enum)

```text
BUILD
MODIFY_EXISTING
CONFIG_ONLY
DOC_ONLY
TEST_ONLY
DO_NOT_BUILD
NEEDS_MORE_EVIDENCE
NEEDS_REGISTRY
MODIFY_DOCS_FIRST
INCONCLUSIVE_DO_NOT_BUILD
```

### NO_MAP_NO_WORK Registry Status (closed enum)

```text
REGISTRY_PRESENT_COMPLETE
REGISTRY_PRESENT_KNOWN_INCOMPLETE
REGISTRY_PRESENT_UNKNOWN_COVERAGE
NEEDS_REGISTRY
GENESIS_REGISTRY_REQUIRED
```

### NO_MAP_NO_WORK Scout Status (closed enum)

```text
VALIDATED
SELF_REPORT_ONLY
NEEDS_VERIFICATION
INVALID_SCHEMA
STALE_MAP
LEVEL_DRIFT_DETECTED
PROTECTED_SURFACE_REQUIRES_DRIVER
```

### NO_MAP_NO_WORK Seal Status (closed enum)

```text
PASS
BLOCKED_LEVEL_DRIFT
BLOCKED_REGISTRY_DRIFT
BLOCKED_STALE_MAP
BLOCKED_SELF_REPORT_EVIDENCE
BLOCKED_MISSING_DRIVER_SIGNOFF
BLOCKED_INVALID_OVERRIDE
BLOCKED_INVALID_DRIVER_SIGNATURE
BLOCKED_INVALID_GUARDRAIL_VERSION
BLOCKED_GUARDRAIL_VERSION_MISMATCH
BLOCKED_PROTECTED_SURFACE_UNVALIDATED
BLOCKED_TTL_EXPIRED
```

### NO_MAP_NO_WORK Protected Surface (closed enum)

```text
YES
NO
UNKNOWN
```

### NO_MAP_NO_WORK Protected Detection Source (closed enum)

```text
REGISTRY_PATH_MATCH
DIFF_CLASSIFIER
DRIVER_SEMANTIC_REVIEW
INDEPENDENT_VERIFIER
UNVALIDATED
```

### NO_MAP_NO_WORK Evidence Authenticity (closed enum)

```text
RUNTIME_CAPTURED
VERIFIER_RERUN
DRIVER_SPOT_CHECKED
CI_GENERATED
HASH_ONLY
SELF_REPORTED
```

### NO_MAP_NO_WORK Level Validation Source (closed enum)

```text
DRIVER
INDEPENDENT_VERIFIER
RUNTIME_DIFF_CLASSIFIER
CI_CHECK
DETERMINISTIC_RULE
UNVALIDATED
```

### NO_MAP_NO_WORK Waiver Types (closed enum)

```text
OVERRIDE
SPOT_CHECK_WAIVER
STALENESS_WAIVER
EVIDENCE_WAIVER
PROTECTED_SURFACE_WAIVER
```

### NO_MAP_NO_WORK Level Drift Incident Kinds (closed enum)

```text
LEVEL_0_FALSE_TRIVIAL
LEVEL_1_TO_LEVEL_2_DRIFT
PROTECTED_SURFACE_UNDECLARED
GENERAL_LEVEL_DRIFT
```

---

## Fast Mode Specification

Fast Mode is the cheap, bounded, truth-safe execution path for stable scenes where
the heavy CAP pipeline would cost more than the task.

### Entry Conditions (all must hold)

```text
anchor_support             in {medium, strong}
conflict_density           <= 0.10
stale_critical_triggers    == 0
boundary_risk              <= 0.20
intent_ambiguity           <= 0.20
irreversible_risk          == 0
canonical_change           == false
self_approval              == false
```

Additionally, **no Forbidding Signal** (see Ontology) may be present. Any one of
them forces `FAST_DENIED`.

### Execution Caps under Fast Mode

```text
social_top_k               1
repair_depth               1
retcon_depth               1
caw_iterations             0
semantic_passes            0 or 1
max_verifier_depth         targeted
max_context_expansion      minimal
allow_architecture_review  false
allow_canonicalization     false
allow_irreversible_action  false
```

---

## RealityFloor for Soft Budget Claims

A soft budget claim (a Soft Budget Claim Kind: "no time", "no energy", "too risky",
"let's defer") is not a hard fact. The layer requires a RealityFloor probe before
accepting it as a budget constraint:

```text
soft claim -> RealityFloor probe
  -> verifier cost actually known?
  -> danger of the change actually scored?
  -> cheaper targeted test available?
  -> full review really required, or smoke enough?
  -> if floor agrees (evidenced):    accept claim as a real constraint
  -> if floor disagrees (rationalized): reject claim as avoidance
```

Hard facts (declared, observable evidence) bypass the floor:

```text
deadline at 18:00, code is at 17:55  -> hard
laptop battery at 3%                 -> hard
agent has no permission for push     -> hard
```

---

## Patrol Gap for Frozen Containers

Quarantine and Cold Storage prevent perceived overheating but must not become a
graveyard. Every frozen item carries a patrol contract:

```text
frozen_at              timestamp
reason_frozen          one of Patrol Freeze Reasons (see Ontology)
next_patrol_at         when the item must be re-examined
recompile_path?        if relevant: how the content can return to a live state
read_only_extraction?  what can be quoted now without releasing
```

Patrol is read-only by default; re-canonicalization still requires Release Gate.

```text
Freeze for safety.
Patrol for relevance.
Recompile for life.
Release only through the gate.
```

---

## Invariants

| Id | Statement | Enforcement |
|---|---|---|
| CG-01 | `analytical_paralysis` requires action in `{stop_audit, enter_fast_mode, take_minimal_action}`. | Schema if/then |
| CG-02 | `budget_underestimation` requires action `require_reality_floor`. | Schema if/then |
| CG-03 | `frozen_container` requires action `schedule_patrol_gap`. | Schema if/then |
| CG-04 | `fast_mode_abuse` requires action `force_escalation`. | Schema if/then |
| CG-05 | `escalation_avoidance` requires action `force_escalation` or `hold_for_human`. | Schema if/then |
| CG-06 | `FAST_ALLOWED` is forbidden if any `forbidding_signal` is present. | Schema enforces the contrapositive: `FAST_ALLOWED => forbidding_signals` empty. |
| CG-07 | A soft budget claim is accepted only after a RealityFloor probe. | if action = `enter_fast_mode` AND `soft_budget_claims` non-empty then `reality_floor_passed: true` required. |
| CG-08 | `enter_fast_mode` is admissible only when the Fast Mode verdict is `FAST_ALLOWED`. | if action = `enter_fast_mode` then `verdict == FAST_ALLOWED` required. |
| FM-01 | Fast Mode is not careless mode. | `policy.fast_mode_is_careless = const false`. |
| FM-02 | Fast Mode requires stable anchors. | If verdict = `FAST_ALLOWED`, then `anchor_support` in `{medium, strong}`. |
| FM-03 | Fast Mode cannot perform irreversible transitions. | If verdict = `FAST_ALLOWED`, then `irreversible_risk = 0`. |
| FM-04 | Fast Mode must stop when sufficient. | `stop_condition` required when `fast_mode_caps` present. |
| FM-05 | Fast Mode escalates on conflict. | If `stale_critical_triggers > 0` OR `anchor_support = weak`, verdict cannot be `FAST_ALLOWED`. |
| FM-06 | Free budget does not justify deeper analysis. | `policy.free_budget_extends_analysis = const false`. |
| FM-07 | Fast Mode must leave a trace. | `audit_log_ref` required when verdict = `FAST_ALLOWED`. |
| NMW-01 | Producing agents cannot validate their own Scout Level. | `level_validation_source` must not be `UNVALIDATED` for any authorizing Scout Map. |
| NMW-02 | Protected surface is detected by registry/path/diff/Driver review, not agent claim. | Protected edits require Level 2 and verified evidence. |
| NMW-03 | `BUILD` cannot rely on missing registry or self-reported/hash-only evidence. | Schema if/then on `need_verdict = BUILD`. |
| NMW-04 | Driver bypasses require signed Waiver Records. | Waiver schema requires `driver_signature`. |
| NMW-05 | Scout Maps are snapshots and expire. | Snapshot hashes + `ttl_expiration`; stale/expired maps block seal. |
| NMW-06 | Level drift is quarantined, not retroactively legitimized. | `BLOCKED_LEVEL_DRIFT` requires quarantine record. |
| NMW-07 | Guardrail version mismatch blocks seal. | Current schema admits only the current `guardrail_version`; mismatches use `BLOCKED_GUARDRAIL_VERSION_MISMATCH`. |

---

## Deployment Profiles

The spec is **dual-use by binding, not by fork**: one specification, two deployment
profiles. The core — Risks, RealityFloor, Patrol Gap, Guardrail Actions — is
domain-agnostic. A deployment **binds which Forbidding Signals its executor can
actually raise**.

| Aspect | coding-agent profile | conversational-bot profile |
|---|---|---|
| Live Forbidding Signals | all 12 | all except `git_seal`, `repo_identity_mismatch`, `live_browser_write` |
| Signals that never fire | — | `git_seal`, `repo_identity_mismatch`, `live_browser_write` |
| Signals that REMAIN live | `git_seal`, `repo_identity_mismatch`, `live_browser_write`, `memory_canonicalization`, `security_boundary`, `destructive_operation`, `financial_decision`, `legal_decision`, `medical_decision` | `memory_canonicalization`, `security_boundary`, `destructive_operation`, `financial_decision`, `legal_decision`, `medical_decision` (advice + canonical-memory writes) |

Rules that hold across both profiles:

- A trivial turn with no candidate action and no detected risk routes to `no_action`
  and answers normally. It does **not** enter Fast Mode; therefore FM-07
  (`audit_log_ref`) does **not** fire on ordinary chat.
- Fast Mode is entered **only** when there is a candidate action / transition whose
  cheap path must be gated. Fast Mode is **not** a reasoning-depth selector for chat.
- The absence of a signal in a profile means it never fires there. It does **not**
  mean the spec is coding-only.


---

## NO_MAP_NO_WORK / Scout-Before-Build Gate

`NO_MAP_NO_WORK` prevents CAP from building layers, mechanisms, gates, or policies
that later turn out to be duplicates, pipeline conflicts, already-covered behavior,
or dead code. It is not a new sequential runtime layer; it is an amendment to the
existing Scout / TriMozga / Transition Cost discipline.

Core invariant:

```text
Need must be evidenced before Transition Cost is calculated.
No verified map -> no work authority.
```

> [!NOTE]
> **CAP Invariant:**
> The system must not optimize the transition cost for a transition that has not been proven necessary.
> *In short: Do not calculate the price of a bridge until you have proven that the river needs to be crossed.*

### Scope and level validation

The producing agent may propose a Scout Level, but it cannot validate that level.
The level is valid only when validated by a Driver, independent verifier, runtime
diff classifier, CI check, or deterministic rule.

`LEVEL_0` is post-hoc only. It is allowed only for a closed whitelist of trivial
changes (typo-only docs, formatting-only changes, comment-only clarification with
no policy change, behavior-preserving local rename, or test-name rename with no
assertion/fixture behavior change). Actual diff is checked at commit/seal. If the
diff changes behavior, policy, runtime semantics, verifier, registry, seal,
authority, memory, tool access, or routing, the result is `BLOCKED_LEVEL_DRIFT`.

`LEVEL_1` requires a minimal Scout artifact and seal-time reclassification against
actual diff. A claimed Level 1 that touches protected surface becomes Level 2.

`LEVEL_2` is mandatory for new layers, new mechanisms, new gates, new policy,
verifier/release/authority changes, memory/RAG/tool-routing/agent-routing changes,
cross-cutting behavior, permanent code surface, registry changes, or any protected
mechanism.

### Protected-surface detection

Protected-surface detection is never self-classified by the producing agent. Each
Mechanism Registry entry must include:

```text
mechanism_id
name
protected: true | false
owning_file_globs
protected_paths
semantic_review_required: true | false
status
known_overlap
guardrail_version
last_reviewed
```

A change is protected when the actual diff intersects `protected_paths` or matches
`owning_file_globs` of a `protected:true` registry entry. Any edit to guardrail,
verifier, seal, override, registry, authority, memory, tool-access, or routing
files is over-approximated as protected unless cleared by explicit Driver semantic
review.

Protected work always requires Level 2, verified evidence, Driver authority, and
seal-packet visibility, regardless of whether the Need Verdict is `BUILD`,
`MODIFY_EXISTING`, `CONFIG_ONLY`, `DOC_ONLY`, or `TEST_ONLY`.

### Registry and duplicate checks

A duplicate check is not deterministic without a canonical Mechanism Registry. The
registry has explicit coverage status. If coverage is not complete, "not found in
registry" does not mean "does not exist"; doc/code/test search artifacts are still
required.

Any `BUILD` implementation must create or update the registry entry. The seal gate
blocks with `BLOCKED_REGISTRY_DRIFT` if implementation reached seal without the
required registry update.

Genesis registry creation is a Driver-authored root-of-trust action. Because no
prior registry exists, the genesis seal packet must include Driver authorship,
initial coverage status, known gaps, first protected mechanism list, and the
trusted Driver public key or genesis registry hash anchored in validator code or
Driver-managed environment.

### Scout Map schema surface

A Scout Map is valid only as a saved artifact and must include:

```text
report_id
artifact
guardrail_version
requested_change
proposed_level
validated_level
level_validation_source
level_validation_phase
registry_status
registry_entries_checked
protected_surface
protected_detection_source
protected_registry_entries
protected_path_matches
evidence_authenticity
evidence_artifacts
spot_check_records
waiver_records
snapshot_hashes
ttl_expiration
existing_mechanics
pipeline_fit
duplicate_check
already_covered_check
conflict_check
dead_code_or_orphan_risk
minimal_change_route
need_verdict
scout_status
max_scout_iterations
scout_iteration_count
termination_reason
next_action
```

`max_scout_iterations` defaults to 3. After three inconclusive iterations, the
terminal safe verdict is `INCONCLUSIVE_DO_NOT_BUILD`.

### Evidence authenticity

Artifact hashes prove integrity after creation; they do not prove that grep/search
actually ran. Evidence counts as authentic only if runtime-captured, verifier-rerun,
Driver spot-checked, or CI-generated. Producing agents cannot choose their own
"random" spot-check target. In Day-1 solo mode, the Driver selects spot-check terms
after artifacts are fixed.

### Waivers and Driver signatures

Any Driver bypass is represented as a unified Waiver Record: override, spot-check
waiver, staleness waiver, evidence waiver, or protected-surface waiver. Each waiver
requires Driver authority, seal visibility, and a cryptographic Driver signature.

```text
WAIVER_RECORD:
waiver_id
waiver_type
human_driver
original_status
allowed_scope
reason
accepted_risk
evidence_reviewed
expiration
artifact
seal_visibility
guardrail_version
driver_signature
```

A waiver without a valid Driver signature is invalid and blocks seal as
`BLOCKED_INVALID_DRIVER_SIGNATURE`.

### Scout Map staleness and TTL

A Scout Map is a snapshot at time `T`. It records snapshot hashes of consulted
registry entries, guardrail files, source files, docs, tests, and search artifacts.
The seal gate recalculates these hashes. Mismatch yields `STALE_MAP` /
`BLOCKED_STALE_MAP`.

Scout Maps also expire by TTL even if all hashes still match. Default TTL is 48
hours; protected surface should use 24 hours; security/tool-access/verifier/seal
surfaces should use 12 hours. Expired maps require rerun or a signed Driver
staleness waiver.

### Level drift quarantine

`BLOCKED_LEVEL_DRIFT` has an operational aftermath:

```text
1. Save the current diff as a patch artifact.
2. Create a quarantine branch or isolated quarantine directory.
3. Reset the working tree to the pre-implementation reference.
4. Block auto-merge.
5. Run a fresh Scout Map as if the implementation does not exist.
6. Re-apply or salvage only after an allowing verdict.
7. Include the incident in the seal packet.
```

Repeated drift at any level escalates to Driver review; repeated systematic drift
freezes the producing agent/session until reset.

### Guardrail versioning

Every Scout Map and seal packet carries `guardrail_version`. If the Scout Map
version differs from the current seal-gate runtime version, the seal is blocked as
`BLOCKED_GUARDRAIL_VERSION_MISMATCH`. Recovery requires rerunning the Scout Map
under the current guardrail version or a signed Driver waiver.

### Day-1 deployment profile

Day-1 solo mode is explicitly degraded: runtime classifier, CI artifact capture,
and independent verifier may be unavailable. The trust floor is Driver good faith,
which is accepted residual risk, not solved risk. Even in Day-1 mode, the minimum
required fields are guardrail version, requested change, proposed and
Driver-validated level, protected surface, registry status, evidence summary,
Driver-selected spot-check or signed waiver, Need Verdict, snapshot hashes when
available, and seal-packet reference.

### Telemetry

Telemetry is aggregated from seal packets, not from a separate mutable journal.
Tracked rates include override, waiver, inconclusive, level drift, registry drift,
self-report evidence, stale map, protected-surface changes, verification failure,
gate block, signature failure, and guardrail-version mismatch. If waiver or
override becomes routine, the guardrail is miscalibrated and must be recalibrated
rather than normalized.

---

## Relation to Other Layers

| Layer | Role in the Guardrails loop |
|---|---|
| Observability Protocol | Supplies budget / progress / trigger telemetry to detect risks. |
| Mirror Layer | Verifies whether the scene is stable before Fast Mode entry. |
| Context Hygiene | Prevents Fast Mode from reading contaminated / stale context. |
| Cross-Domain Drain | Detects `analytical_paralysis` as spikes in `drain_ratio`. |
| Dynamic Subject-State Detection | Distinguishes a fast conscious step from avoidance. |
| Anti-drama Detection | Blocks budget-extension requests based on narrative pressure. |
| Adjustment Layer | Constructs cheap C0/C1 routes within Fast Mode caps. |
| Verifier | In Fast Mode, trimmed to `targeted` but not disabled. |
| Release Gate | Absolute block on any forbidding signal regardless of guardrails. |

---

## Pipeline

```text
1.  Read telemetry (audit cost so far, progress, stale triggers).
2.  Score input: anchor_support, conflict_density, intent_ambiguity,
                 irreversible_risk, soft_budget_claims, frozen_items.
3.  Detect risks: analytical_paralysis / budget_underestimation /
                  frozen_container / fast_mode_abuse / escalation_avoidance.
4.  Compute Fast Mode verdict: FAST_ALLOWED | FAST_DENIED | ESCALATE_REQUIRED.
5.  Choose action:
      - no risk detected  -> no_action: proceed on the normal OCM chain
                             (conversational profile: answer normally).
      - otherwise         -> route per risk-to-action mapping (CG-01..CG-05).
6.  If enter_fast_mode: require verdict == FAST_ALLOWED (CG-08); emit
                        fast_mode_caps + stop_condition + audit_log_ref.
7.  If require_reality_floor: require explicit reality_floor_passed=true on any
                             acceptance of a soft budget claim.
8.  If schedule_patrol_gap: emit patrol_gap record (frozen_at, reason_frozen,
                            next_patrol_at, optional recompile_path /
                            read_only_extraction).
9.  If force_escalation / hold_for_human: hand off to upstream OCM pipeline;
                                          do not bypass Release Gate.
10. Emit COM-Log event with detected risks, action, verdict, reasons.
```

### Forbidden Routes

```text
guardrails -> direct release
guardrails -> canonicalize memory
guardrails -> commit / push / destructive action
```

### Allowed Routes

```text
guardrails -> routing decision -> upstream OCM pipeline applies -> normal Release Gate flow
```

---

## Quality Criteria

A guardrails run is valid if and only if:

- Every detected risk maps to the correct action (CG-01..CG-05).
- Any `FAST_ALLOWED` verdict has empty `forbidding_signals`, `anchor_support` in
  `{medium, strong}`, and zero `irreversible_risk`.
- Any `enter_fast_mode` action has verdict `FAST_ALLOWED` (CG-08).
- Any `enter_fast_mode` action with soft budget claims has `reality_floor_passed: true`.
- Any `FAST_ALLOWED` leaves an `audit_log_ref`.
- Any `frozen_container` action comes with a patrol gap detailing `next_patrol_at`.
- A trivial turn with no candidate action / no detected risk routes to `no_action`
  and does not emit `audit_log_ref`.
- The deployment profile is respected: only signals live in that profile may force
  `FAST_DENIED`.
- Policy constants (FM-01, FM-03, FM-06, etc.) were not altered.

---

## Canonical Manifest

```text
Free budget is not a license for excavation or deeper audit.
A stable scene is not a license for weaker quality or weaker authority.
"Quick" never overrides "must pass the gate".
Quarantine is not a graveyard; it is a patrol assignment.

CAP defends canonical state from foolish action.
CAP-Guardrails defend CAP itself from becoming a Frozen System.
```

---

## Schema and References



The schema version for this revision is `0.2`; it includes the original Fast Mode /
Anti-Freeze decision object plus optional `scout_map`, `seal_packet`, and
`telemetry_update` surfaces for `NO_MAP_NO_WORK v4.2`.
The full JSON schema is located at
[`../spec/cap_guardrails.schema.json`](../spec/cap_guardrails.schema.json).
A worked example is available at
[`../examples/cap_guardrails_decision_example.json`](../examples/cap_guardrails_decision_example.json).
