# Run 004 — Breach is Recovery-Only (operator decision executed and verified)

Status: `recorded run / research-only`. Third executed transition on this
repository; the first whose desired state was set by an operator decision
rather than read from the docs, and the second measured escalation.

## 1. Initial state and the input available before the choice

- Tree at `2be76e6`, clean, full suite `936 passed, 2 skipped`
  (`mirror_frame.json`, declared state `source: user` = the operator's
  decision of 2026-09-24; observed: the code encoded the superseded table line
  `breach = 0`; the alphabet's Recovery-Only gate listed its operators only in
  prose; the validator already tied Breach to `Recovery-Only`).
- Goal, constraints, budget: `candidate_transition.json` (mode `reconcile`,
  kind `reconcile_conflict`; two carriers of the Breach rule disagreed and the
  operator chose which one the code follows).
- Postcondition defined before execution: the driver's oracle
  (`oracle_recovery.py`, outside the tree, red on the baseline with
  `ImportError: cannot import name 'BREACH_BUDGET_GATE'`), the module tests,
  and the alphabet / schema / validator tests.

## 2. Proposed transition

Additive-plus-signature change on the existing numeric contract: a
machine-readable `permitted_operators` list on the alphabet's Recovery-Only
gate; `budget_gate_permitted_operators`; Breach without a numeric ceiling;
`operator_admissibility(operator, ...)` with `blocked_recovery_only` and
`not_computed`; the zero-risk simplification test replaced. `regression_risk`
was estimated highest (0.3) because an existing signature changes.

## 3. Action actually executed and objects changed

Executor: NoMCP mode 1 through the global shim, one native Workflow, one
Haiku relay per stage. From `nomcp_coding_receipt.json` (this receipt already
carries the fields NoMCP added at `caa2feb`: separate stdout/stderr tails,
`check_index`, `timed_out`):

| stage | model (requested = served; identity per CLI `modelUsage`, not independently verified) | turns | output tokens | wall s | oracle | module tests | alphabet/schema/validator tests | outcome |
|---|---|---|---|---|---|---|---|---|
| cheap_coder | `gemma4:31b-cloud` | 14 | 9,535 | 57.4 | exit 0 | exit 0 (89 passed) | exit 1: `NameError: name 'pytest' is not defined` in the new alphabet test | set aside (stash `6e7b4e56`, local only) |
| fallback_coder | `deepseek-v4.1-flash:cloud` | 55 | 25,094 | 131.5 | exit 0 | exit 0 (91 passed) | exit 0 (22 passed) | `FALLBACK_PASS` |

Touched: `spec/operator_alphabet.json` (one key), `cap/operator_alphabet.py`,
`cap/budget_calculus.py`, `tests/test_budget_calculus.py`,
`tests/test_operator_alphabet.py`. Committed as `feat(budget): Breach is
Recovery-Only, decided by operator identity` together with driver-authored
doc alignment (telemetry table row, Budget Recovery sentence, both Numeric
Contract sections).

## 4. Observed result, postcondition check, costs

- Router: all three declared checks exit 0 after the fallback.
- Independent verdict (`nomcp_verdict_receipt.json`): `glm-5.3-flash:cloud`
  (chosen because the fallback coder is a DeepSeek model), `ACCEPT`, 43.0 s;
  its reason walks the five files, the exact semantics, the replaced test and
  the recheck (91 + 22 passed).
- Driver adjudication: diff read in full against the packet; full suite
  `941 passed, 2 skipped` (44 s); Workflow model-pin check 2/2 Haiku.
- Costs in their own units: cheap tier 9,535 tokens / 57.4 s on a set-aside
  attempt; fallback 25,094 tokens / 131.5 s; verifier 43.0 s (token usage not
  in this receipt: the runner gained `attempt_usage` at `caa2feb`, after this
  packet builder was written); relays 25,924 tokens; Workflow wall 319 s;
  driver checks about 2 minutes. Money: unknown. Risk realised:
  `regression_risk` fired at the cheap tier again and was contained by a
  declared existing-test check, as in run 002.

## 5. Divergence between expectation and result; Adjustment

- Expected: the cheap tier closes a change whose every name and rule was
  spelled out. Observed: it implemented the semantics correctly (oracle and
  module tests green) and failed on a missing `import pytest` in the one test
  file it added. The fallback then re-did the whole task (55 turns) for what
  was a one-line defect. Adjustment: none by a model; the router's fixed
  policy restored the baseline and admitted the fallback. Recorded as a
  candidate observation for the NoMCP journal: the route has no "repair the
  set-aside attempt" step, so a trivial miss costs a full second attempt.
- Expectation vs result on the transition itself: none; every item of
  `expected_evidence_after_apply` was observed.
- What the numeric contract now says that it did not before: at Breach the
  operator's identity decides first, then the budget; a missing input yields
  `not_computed`, never `admissible`. What it still does not say: a numeric
  `admissible` is not full admissibility (items 3–5 of the rule are unchecked).
- Not closed by this run (operator's follow-up of the same evening): the
  binding of this executed transition to its object revision, executor call,
  re-observation and per-criterion check results as one machine-checkable
  record with resolvable references. That is the next step (run 005).
