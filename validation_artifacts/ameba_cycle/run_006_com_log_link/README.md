# Run 006 — candidate step ↔ COM-Log record, with risk-weight provenance

Status: `recorded run / research-only`. The operator's item 2 of 2026-09-24,
executed from the packet that had been prepared and kept under
`prepared/com_log_link/` (`coding_packet.json` here is that packet).

## 1. Initial state and the input available before the choice

- Tree at `1db22cf`, clean, pushed; full suite `981 passed, 2 skipped`
  (`mirror_frame.json`; declared state `source: user` = the operator's
  decision: the six risk axes and the cost bands stay and are never converted
  to a RiskWeight; the gate's inputs already exist in COM-Log; a route step
  is linked to one COM-Log record; active operators come from the cycle
  state; the assigned RiskWeight keeps its source and estimate status; missing
  inputs mean the gate is not computed; a numeric pass is not full
  admissibility).
- Observed: `adjustment_step` had no reference to a COM-Log record;
  `operator_admissibility` had the operator-first signature from run 004; no
  function gated a step from a linked record.

## 2. Proposed transition

`candidate_transition.json`: mode `repair`; one optional field on the schema
(`com_log_ref`, non-empty string) and one small module
(`cap/candidate_gate.py`) with tests; `loop_risk` estimated highest (0.2)
after the evening's one-detail misses of the cheap tier.

## 3. Action actually executed

NoMCP mode 1, direct through the shim (detached); declared checks: the
driver's oracle (`oracle_link.py`, red on the baseline with
`ModuleNotFoundError: cap.candidate_gate`), the gate and schema tests, the
budget-calculus tests.

| stage | model (identity per CLI report, not independently verified) | turns | output tokens | wall s | outcome |
|---|---|---|---|---|---|
| cheap_coder | `gemma4:31b-cloud` | 9 | 3,861 | 17.8 | oracle exit 0 (the module was right), but two of its own tests asserted the wrong behaviour (`test_boundary_at_breach_admits`, `test_over_budget_at_breach_blocks`: 2 failed, 56 passed); set aside (local stash) |
| fallback_coder | `deepseek-v4.1-flash:cloud` | 31 | 16,842 | 92.7 | oracle exit 0; 69 passed; 91 passed; `FALLBACK_PASS` |

Objects changed: `spec/adjustment_layer.schema.json` (one optional property),
`reference/python/tests/test_adjustment_layer_schema.py` (two tests added),
new `reference/python/cap/candidate_gate.py` and
`reference/python/tests/test_candidate_gate.py`.

## 4. Observed result, postcondition check, costs

See `transition_execution_record.json` and `checks/` (each criterion re-run by
the driver at the obtained revision in a detached worktree). Driver probe on
the landed module: a linked Fixation 20 at Breach with allowed 45 and active
[10] is `admissible` with `estimate_status: assigned`; a step without
`com_log_ref` is `not_computed` with a reason; Boundary at Breach is
`blocked_recovery_only`; every record carries
`numeric_pass_is_full_admissibility: false` and the three unchecked items.
Full suite `1004 passed, 2 skipped`. Costs in the receipt and the record;
money unknown.

## 5. Divergence between expectation and result; Adjustment

- Expected: the cheap tier closes a small task whose oracle it satisfied.
  Observed: the implementation was correct and the worker's own tests were
  wrong; the declared-checks rule ("the worker's tests must pass too") set
  the attempt aside and the fallback rewrote both. Fifth one-detail miss of
  the cheap tier tonight, and the first where the miss was in the tests, not
  the code. No CAP-level Adjustment; no oracle weakened; no code written by
  the driver.
- What is now possible and not yet done: a real candidate step can carry
  `com_log_ref` and be gated numerically. No real transition has such a
  record yet; the first one will carry an engineering-assigned RiskWeight and
  must say so. The operator's acceptance items 1–4 are the oracle; item 5
  (one candidate through the whole chain to a verified postcondition) is this
  run's execution record, produced with the format from run 005.
- Still true: a numeric `admissible` through this link is not full
  admissibility; items 3–5 of the rule remain unchecked by code.
