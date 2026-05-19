# CAP-Guardrails / Anti-Freeze Layer

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

## Five risks (closed enum)

| Risk | Meaning |
|---|---|
| `analytical_paralysis` | Audit consumed the budget the action was supposed to use. |
| `budget_underestimation` | A "no budget" claim is a defensive rationalization, not a hard fact. |
| `frozen_container` | Quarantine / Cold Storage became a graveyard; nothing thaws. |
| `fast_mode_abuse` | Speed used as a cover to bypass verifier / Release Gate / authorization. |
| `escalation_avoidance` | Conflict or irreversible signal appeared and was ignored. |

---

## Guardrail actions (closed enum)

```text
enter_fast_mode
require_reality_floor
schedule_patrol_gap
force_escalation
stop_audit
take_minimal_action
hold_for_human
```

These are routing actions. The layer does not mutate; it tells the
upstream OCM pipeline what to do next.

---

## Fast Mode

Fast Mode is the cheap, bounded, truth-safe execution path for stable
scenes where the heavy CAP pipeline would cost more than the task.

### Entry conditions (all must hold)

```text
anchor_support       >= medium
conflict_density     <= 0.10
stale_critical_triggers == 0
boundary_risk        <= 0.20
intent_ambiguity     <= 0.20
irreversible_risk    == 0
canonical_change     == false
self_approval        == false
```

### Fast Mode is forbidden when any of these are present

```text
git seal
memory canonicalization
security boundary
repo identity mismatch
live browser write
financial / legal / medical decision
destructive operation
new architectural frame
anchor conflict
high uncertainty
```

### Execution caps under Fast Mode

```text
social_top_k             1
repair_depth             1
retcon_depth             1
caw_iterations           0
semantic_passes          0 or 1
max_verifier_depth       targeted
max_context_expansion    minimal
allow_architecture_review  false
allow_canonicalization     false
allow_irreversible_action  false
```

### StableSceneShortCircuit verdict

```text
FAST_ALLOWED        cheap path is admissible
FAST_DENIED         use the normal OCM/CAP pipeline
ESCALATE_REQUIRED   conflict / boundary / irreversibility present
```

---

## RealityFloor for soft budget claims

A soft budget claim ("no time", "no energy", "too risky", "let's defer")
is not a hard fact. The layer requires a RealityFloor probe before
accepting it as a budget constraint:

```text
soft claim: "no budget for the verifier"
  -> reality floor:
       verifier cost actually known?
       danger of the change actually scored?
       cheaper targeted test available?
       full review really required, or smoke enough?
  -> if floor agrees: accept claim
  -> if floor disagrees: reject claim as rationalization
```

Hard facts (declared, observable evidence) bypass the floor:

```text
deadline at 18:00, code is at 17:55: hard
laptop battery at 3%: hard
agent has no permission for git push: hard
```

---

## Patrol Gap for frozen containers

Quarantine and Cold Storage prevent perceived overheating but must not
become a graveyard. Every frozen item carries a patrol contract:

```text
frozen_at              timestamp
reason_frozen          one of {contamination, overheat, weak_provenance, anchor_conflict, awaiting_evidence, intentional_park}
next_patrol_at         when must be re-examined
recompile_path?        if relevant: how can the content return to a live state
read_only_extraction?  what can be quoted now without releasing
```

Patrol is read-only by default; re-canonicalization still requires
Release Gate.

---

## Invariants

| Id | Statement | Enforcement |
|---|---|---|
| CG-01 | `analytical_paralysis` requires action in `{stop_audit, enter_fast_mode, take_minimal_action}`. | if/then |
| CG-02 | `budget_underestimation` requires action `require_reality_floor`. | if/then |
| CG-03 | `frozen_container` requires action `schedule_patrol_gap`. | if/then |
| CG-04 | `fast_mode_abuse` requires action `force_escalation`. | if/then |
| CG-05 | `escalation_avoidance` requires action `force_escalation` or `hold_for_human`. | if/then |
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

Schema at
[`../spec/cap_guardrails.schema.json`](../spec/cap_guardrails.schema.json);
worked example at
[`../examples/cap_guardrails_decision_example.json`](../examples/cap_guardrails_decision_example.json).
