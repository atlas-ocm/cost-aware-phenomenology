# Run 002 — telemetry ceiling and operator admissibility (first measured escalation)

Status: `recorded run / research-only`. Second pass of the cycle on this
repository. Same formats as run 001; the difference is that here the cheap
executor failed its postcondition, the router set its attempt aside and the
fallback executor closed the task, so this run records a real
expectation-versus-result divergence and the Adjustment that followed.

## 1. Initial state and the input available before the choice

- Tree at `aa6048f` (after the layout fix and the docs correction), clean,
  full suite `924 passed, 2 skipped` (`mirror_frame.json`).
- Declared: `telemetry_gating.md` gives a per-state RiskWeight ceiling
  (Clean 90 / Loaded 60 / Overheating 30 / Breach 0) and
  `operator_admissibility.md` gives a telemetry-then-budget rule. Observed:
  `budget_calculus.py` gates by budget only; `grep` finds no ceiling and no
  combined rule anywhere in `reference/python`.
- Goal: the cycle can decide "is this candidate operator admissible now"
  under a telemetry state, so that a case like `cgm_03` (Inversion 80% under
  Overheating with AllowedTotalRisk 30%) is computable rather than read.
- Direct path checked and found insufficient: `cycle_decision()` has no
  telemetry input; `permitted_risk_zones_for_budget()` widens by budget
  state, not by telemetry.

## 2. Proposed transition, grounds, constraints, expected postcondition

`candidate_transition.json`: mode `repair`, additive change to the existing
numeric-contract module, verdict `route_found`. Two authorized checks: an
ephemeral oracle written by the driver from the docs and `cgm_03` (kept
outside the tree, copied here as `oracle_admissibility.py`; red on the
baseline with `ImportError: cannot import name 'TELEMETRY_MAX_RISK'`), and
the module's existing tests (green on the baseline, 75 passed, as the
regression guard). `regression_risk` was estimated highest (0.2) because the
module is shared.

## 3. Action actually executed and objects changed

Executor: NoMCP mode 1 through the global shim, one native Workflow, one
Haiku relay per stage. From `nomcp_coding_receipt.json`:

| stage | model (requested = served, identity ESTABLISHED per CLI report) | turns | output tokens | wall s | oracle | module tests | outcome |
|---|---|---|---|---|---|---|---|
| cheap_coder | `gemma4:31b-cloud` | 8 | 2,595 | 15.9 | exit 0 | exit 2: `ImportError: cannot import name 'MODE_PREFERRED_ZONE'` | postcondition false; set aside (stash `33843e76`, local only) |
| fallback_coder | `deepseek-v4.1-flash:cloud` | 24 | 11,670 | 52.0 | exit 0 | exit 0, 87 passed | postcondition true; `FALLBACK_PASS` |

Gemma's attempt (155 insertions, 10 deletions) implemented the three names
correctly enough to satisfy the oracle but deleted the existing constants
`MODE_RTF_RANGE` and `MODE_PREFERRED_ZONE`, which the existing test module
imports. DeepSeek's attempt is purely additive (147 insertions, 0 deletions):
`TELEMETRY_MAX_RISK`, `max_permitted_risk()`, `operator_admissibility()`
and 12 tests. Committed as `bbbc26c` together with driver-authored Numeric
Contract sections in the two docs.

## 4. Observed result, postcondition check, costs

- Router: both declared checks exit 0 after the fallback (oracle "all
  assertions hold"; module 75 -> 87 passed).
- Independent verdict (`nomcp_verdict_receipt.json`): `glm-5.3-flash:cloud`,
  chosen deterministically because the fallback coder is a DeepSeek model;
  `ACCEPT`, 30.2 s; its reason checks additivity (0 deletions), the exact
  ceiling values, the ordering, and the recheck run by the packet builder.
- Driver adjudication: diff read in full; full suite `936 passed, 2 skipped`
  (44 s); `scripts/check_repo.ps1` exit 0 in 46 s (it exited 1 at the
  baseline of run 001); Workflow model-pin check 2/2 Haiku.
- Costs in their own units: cheap tier 2,595 tokens / 15.9 s wasted on a
  set-aside attempt; fallback 11,670 tokens / 52.0 s; verifier 30.2 s; relays
  21,006 tokens; Workflow wall 158 s; driver checks about 2 minutes. Money:
  unknown (subscription-served). Risk realised: `regression_risk` fired at
  the cheap tier and was contained by the existing tests; no other axis.

## 5. Divergence between expectation and result; Adjustment

- Expected: the cheap tier closes an additive change with named signatures.
  Observed: it satisfied the new oracle and broke an existing definition.
  The oracle alone would have accepted that attempt; the second declared
  check (the module's own tests) is what refused it. Adjustment: none by a
  model. The router's fixed policy restored the baseline state and admitted
  the fallback tier; the driver did not intervene and did not weaken either
  check.
- What this says about the packet: "do not change any existing function"
  was stated in prose and violated; the executable guard is what held. A
  packet for a shared module should always declare that module's existing
  tests as a check, which this one did.
- Candidate row for the NoMCP journal (not written here: that journal lives
  in another repository): a genuine cheap-tier miss on an additive task,
  caught by the regression check, repaired live by the fallback in 24 turns.
- Contribution of CAP layers, per layer: Mirror named the gap as missing
  code rather than wrong code, which fixed the route shape (additive, one
  module); Adjustment's explicit `forbidden_outcomes` and the regression-risk
  estimate matched what actually happened, but they did not prevent it — the
  existing test did. Telemetry gate and admissibility are now code and were
  exercised only by their own tests; nothing in this run used them to choose
  an action.

## Corrections

- correction_001 (2026-09-24, after the review of `26535dc`; see run 007):
  `costs.measured` in `transition_execution_record.json` holds the closing
  attempt only (24 turns, 11,670 output tokens, 51.99 s). The whole route from the same
  receipt is 32 turns, 14,265 output tokens, 71.25 s of router wall, verifier 30.0 s;
  see `../route_costs_correction_001.json`. For comparing transitions the
  whole route is the figure. The record is left as written: its schema has
  no place for route totals (`CAP_CLOUD_HANDOFF.md` section 7).
