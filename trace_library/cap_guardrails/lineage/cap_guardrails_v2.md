# CAP-Guardrails / Anti-Freeze Layer (Version 2)

CAP-Guardrails is the meta-layer that protects CAP from becoming the
frozen system it was built to detect. Without it, an over-zealous CAP
runtime can spend its entire ActionBudget on auditing the audit and
never let a transition happen.

---

## Purpose

> CAP defends against foolish action.
> CAP-Guardrails defend against foolish inaction dressed up as wisdom.

The layer answers two questions:

1. Is the current CAP pipeline doing more cost than the task warrants?
2. Is the inaction we are committing right now actually a hidden form
   of avoidance, freeze, or budget self-justification?

---

## Ontology

### Risks (closed enum)

| Risk | Meaning |
|---|---|
| `analytical_paralysis` | Audit consumed the budget the action was supposed to use. |
| `budget_underestimation` | A "no budget" claim is a defensive rationalization, not a hard fact. |
| `frozen_container` | Quarantine / Cold Storage became a graveyard; nothing thaws. |
| `fast_mode_abuse` | Speed used as a cover to bypass verifier / Release Gate / authorization. |
| `escalation_avoidance` | Conflict or irreversible signal appeared and was ignored. |

### Guardrail Actions (closed enum)

```text
enter_fast_mode
require_reality_floor
schedule_patrol_gap
force_escalation
stop_audit
take_minimal_action
hold_for_human
no_action
```

These are routing actions. The layer does not mutate; it tells the upstream OCM pipeline what to do next.

### Fast Mode Verdicts (closed enum)

```text
FAST_ALLOWED        cheap path is admissible
FAST_DENIED         use the normal OCM/CAP pipeline
ESCALATE_REQUIRED   conflict / boundary / irreversibility present
```

### Forbidding Signals (closed enum)

Any of these signals **forbids** Fast Mode (forces `FAST_DENIED`):

```text
git_seal
memory_canonicalization
security_boundary
repo_identity_mismatch
live_browser_write
financial_decision
legal_decision
medical_decision
destructive_operation
new_architectural_frame
anchor_conflict
high_uncertainty
```

### Soft Budget Claim Kinds (closed enum)

These are claims that represent potential avoidance and must pass through the `RealityFloor`:

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

---

## Fast Mode Specification

Fast Mode is the cheap, bounded, truth-safe execution path for stable scenes where the heavy CAP pipeline would cost more than the task.

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

A soft budget claim ("no time", "no energy", "too risky", "let's defer") is not a hard fact. The layer requires a RealityFloor probe before accepting it as a budget constraint:

```text
soft claim -> reality floor probe
  -> verifier cost actually known?
  -> danger of the change actually scored?
  -> cheaper targeted test available?
  -> full review really required, or smoke enough?
  -> if floor agrees: accept claim
  -> if floor disagrees: reject claim as rationalization
```

Hard facts (declared, observable evidence) bypass the floor:

```text
deadline at 18:00, code is at 17:55  -> hard
laptop battery at 3%                 -> hard
agent has no permission for push     -> hard
```

---

## Patrol Gap for Frozen Containers

Quarantine and Cold Storage prevent perceived overheating but must not become a graveyard. Every frozen item carries a patrol contract:

```text
frozen_at              timestamp
reason_frozen          one of Patrol Freeze Reasons (see above)
next_patrol_at         when must be re-examined
recompile_path?        if relevant: how can the content return to a live state
read_only_extraction?  what can be quoted now without releasing
```

Patrol is read-only by default; re-canonicalization still requires Release Gate.

```text
Freeze for safety.
Patrol for relevance.
Recompile for life.
Release only through gate.
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
| CG-06 | Fast Mode forbidden under canonical / irreversible / security / memory / repo_mismatch / live_write_risk. | if Fast Mode verdict = FAST_ALLOWED then `forbidding_signals` empty. |
| CG-07 | Soft budget claim accepted only after RealityFloor probe. | if action = enter_fast_mode AND soft_budget_claims non-empty then `reality_floor_passed: true` required. |
| FM-01 | Fast Mode is not careless mode. | `policy.fast_mode_is_careless = const false`. |
| FM-02 | Fast Mode requires stable anchors. | If verdict = FAST_ALLOWED, then `anchor_support` in `{medium, strong}`. |
| FM-03 | Fast Mode cannot perform irreversible transitions. | If verdict = FAST_ALLOWED, then `irreversible_risk = 0`. |
| FM-04 | Fast Mode must stop when sufficient. | `stop_condition` required when `fast_mode_caps` present. |
| FM-05 | Fast Mode escalates on conflict. | If `stale_critical_triggers > 0` OR `anchor_support = weak`, verdict cannot be FAST_ALLOWED. |
| FM-06 | Free budget does not justify deeper analysis. | `policy.free_budget_extends_analysis = const false`. |
| FM-07 | Fast Mode must leave a trace. | `audit_log_ref` required when verdict = FAST_ALLOWED. |

---

## Relation to Other Layers

| Layer | Role in Guardrails Loop |
|---|---|
| Observability Protocol | Supplies budget/progress/trigger telemetry to detect risks. |
| Mirror Layer | Verifies if the scene is stable before Fast Mode entry. |
| Context Hygiene | Prevents Fast Mode from reading contaminated/stale context. |
| Cross-Domain Drain | Detects `analytical_paralysis` as spikes in `drain_ratio`. |
| Dynamic Subject-State Detection | Distinguishes fast conscious step from avoidance. |
| Anti-drama Detection | Blocks budget extension requests based on narrative pressure. |
| Adjustment Layer | Constructs cheap C0/C1 routes within Fast Mode caps. |
| Verifier | In Fast Mode, trimmed to `targeted` but not disabled. |
| Release Gate | Absolute block on any forbidding signal regardless of guardrails. |

---

## Pipeline

```text
1. Read telemetry (audit cost so far, progress, stale triggers).
2. Score input: anchor_support, conflict_density, intent_ambiguity,
                irreversible_risk, soft_budget_claims, frozen_items.
3. Detect risks: analytical_paralysis / budget_underestimation /
                 frozen_container / fast_mode_abuse / escalation_avoidance.
4. Compute Fast Mode verdict: FAST_ALLOWED | FAST_DENIED | ESCALATE_REQUIRED.
5. Choose action per risk-to-action routing (CG-01..CG-05).
6. If enter_fast_mode: emit fast_mode_caps + stop_condition + audit_log_ref.
7. If require_reality_floor: require explicit reality_floor_passed=true on any
   acceptance of a soft budget claim.
8. If schedule_patrol_gap: emit patrol_gap record (frozen_at, reason_frozen,
   next_patrol_at, optional recompile_path / read_only_extraction).
9. If force_escalation / hold_for_human: hand off to upstream OCM pipeline;
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
- Any `FAST_ALLOWED` verdict has empty `forbidding_signals`, medium/strong anchor support, and zero `irreversible_risk`.
- Any `enter_fast_mode` action with soft budget claims has `reality_floor_passed: true`.
- Any `FAST_ALLOWED` leaves an `audit_log_ref`.
- Any `frozen_container` action comes with a patrol gap detailing `next_patrol_at`.
- Policy constants (FM-01, FM-03, FM-06, etc.) were not altered.

---

## Canonical Invariant

```text
Free budget is not a license for deeper audit.
Stable scene is not a license for weaker authority.
"Quick" never overrides "must pass the gate".
Quarantine is not a graveyard; it is a patrol assignment.

CAP defends canonical state from foolish action.
CAP-Guardrails defend CAP itself from becoming a Frozen System.
```

---

## Schema and References

The full JSON schema is located at [`../spec/cap_guardrails.schema.json`](../spec/cap_guardrails.schema.json).
A worked example is available at [`../examples/cap_guardrails_decision_example.json`](../examples/cap_guardrails_decision_example.json).
