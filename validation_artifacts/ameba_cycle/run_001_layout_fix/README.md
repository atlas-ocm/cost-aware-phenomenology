# Run 001 — layout fix (first end-to-end cycle on a real repository)

Status: `recorded run / research-only`. One pass of the cycle the brief asks for,
applied to this repository itself, with every artifact produced by the tool
that produced it and nothing simulated:

```text
observed state + goal + constraints + available actions + budget
  -> candidate next state and route            (candidate_transition.json)
  -> action by an existing executor            (nomcp_coding_receipt.json)
  -> observed result and checked postcondition (this file, section 4)
  -> Adjustment if expectation != result       (this file, section 5)
```

Formats: `mirror_frame.json` validates against `spec/mirror_layer.schema.json`;
`candidate_transition.json` validates against `spec/adjustment_layer.schema.json`.
The two NoMCP receipts are verbatim copies of what the router and the verifier
runner wrote; no new schema was introduced for them, because the
CandidateTransition schema deliberately carries no executor fields (ADJ-09) and
the executor already writes its own receipt.

## 1. Initial state and the input that was actually available before the choice

- Repository: `atlas-ocm/cost-aware-phenomenology`, worktree
  `F:/VibeCoding/CAP-wt-ameba-cycle`, branch `research/ameba-executable-cycle`
  created from `origin/main` = `e65b9af4` (the revision the architect read).
- Observed with git and pytest only (`mirror_frame.json`): clean tree; full
  suite `30 failed, 894 passed, 2 skipped`; `scripts/check_repo.ps1` exit 1 at
  the unit-test step; every failure a `FileNotFoundError` under
  `F:/VibeCoding/CAP/spec/...` raised from two test modules that compute
  `CAP_ROOT = parents[4] / "CAP"`.
- Declared state contradicted: REPRODUCIBILITY.md expects "all tests pass".
  The declared state holds in the original checkout layout
  (`F:/VibeCoding/Shard-Theory/CAP`) and nowhere else.
- Goal: a checkpoint whose standard check is usable as a postcondition in any
  checkout, including a cloud clone. Constraints and budget: see
  `candidate_transition.json` (`input.constraints`, `candidate.cost`).
- Available actions considered: fix the two modules; rename the checkout;
  vendor the external packs. The last two are recorded as rejected
  alternatives in the verdict.

## 2. Proposed transition, grounds, constraints, expected postcondition

`candidate_transition.json`: mode `repair`, three-step reversible route,
verdict `route_found`. Expected evidence after apply: the two modules exit 0;
the full suite exits 0; with the external packs reachable all 32 external cases
are collected and pass; the diff names only the two modules.

Cause status at proposal time was `likely` (read from the source), not
`confirmed`; it was confirmed by the outcome, not assumed.

## 3. Action actually executed and objects changed

Executor: the NoMCP mode-1 route through the global shim
(`nomcp.py coding coding_packet.json ...`), driven from one native Workflow with
one thin Haiku relay per stage (`nomcp-haiku`, one Bash call each).

From `nomcp_coding_receipt.json`:

| field | value |
|---|---|
| decision | `CHEAP_PASS` |
| model_requested / model_served | `gemma4:31b-cloud` / `gemma4:31b-cloud` |
| model_identity_status | `ESTABLISHED` (provider `firstParty` as reported by the CLI's `modelUsage`; this is the CLI's report, not an independent identity probe) |
| turns / output_tokens / wall_s | 6 / 666 / 4.77 |
| fallback_used / seam_used | false / false |
| touched | `reference/python/tests/test_latent_cause_reconstruction_schema.py`, `reference/python/tests/test_looking_glass_schema.py` |
| diffstat | 2 files changed, 9 insertions(+), 11 deletions(-) |

Committed as `602fa63` (`test(layout): resolve spec and examples from the
repository root, not a sibling named CAP`).

## 4. Observed result, postcondition check, costs

- Declared check (baseline, run by the router before the worker): exit 1,
  `30 failed, 2 skipped`. After the worker: exit 0, `30 passed, 2 skipped`.
- Independent verdict (`nomcp_verdict_receipt.json`): verifier
  `deepseek-v4.1-flash:cloud` chosen explicitly (not the coding model);
  `ACCEPT`, 27.9 s, transport 200, parse ok. Packet = diff, diff-stat,
  untracked list, and a recheck run by the packet builder; see
  `verify_packet.json`.
- Driver adjudication on the same tree: full suite `924 passed, 2 skipped`
  (44 s); neighbour case with the external packs reachable through a temporary
  NTFS junction at `<parent>/Patch`: `62 passed`, 32 external case ids
  collected, junction removed afterwards; `git diff` limited to the two
  modules; both files `i/lf w/lf`.
- Workflow model pin check (`experiments/workflow_models.py` in the NoMCP
  checkout): 2 agents, both `claude-haiku-4-5-20251001`, OK.
- Costs, kept in their own units and never summed: worker 666 output tokens,
  6 turns, 4.77 s; verifier 27.9 s (token count not reported by the runner);
  two Haiku relays 19,222 tokens, Workflow wall 73 s; driver checks about
  2 minutes of wall time. Money: unknown (subscription-served models, no
  per-call price is exposed). Risk realised: none of the six axes fired.

## 5. Divergence between expectation and result; Adjustment

- Expectation vs result on the transition itself: none. Every item of
  `expected_evidence_after_apply` was observed.
- One driver-side divergence outside the transition: a shell heredoc that was
  meant to write the *next* packet failed to parse and wrote nothing; the
  Adjustment was to write the same files with a different tool and re-validate
  the oracle on the baseline before routing. Recorded because the brief asks
  for divergences to be kept, not because it changed this run.
- Contribution of CAP layers to this run, stated per layer and not summed:
  Mirror separated the declared "all tests pass" from the observed 30 failures
  and named the layout dependence (useful: it chose the first change);
  Adjustment's schema forced an explicit desired state, a rollback plan and a
  verifier requirement before any edit (useful as discipline; its numeric
  risk/cost fields were estimates with no measurement behind them); Budget
  gate, telemetry gate, Looking-Glass, Context Hygiene, Role Orchestration and
  Release Gate were not exercised as code in this run — Role Orchestration's
  "no self-review" rule was applied by the route shape (coder != verifier !=
  adjudicator), not by any CAP runtime.
