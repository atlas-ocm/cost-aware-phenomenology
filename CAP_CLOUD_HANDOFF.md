# CAP cloud handoff — local stage of `CAP_REWORK_BRIEF.md`

Written 2026-09-24 by the local Driver (Claude Fable 5.1, Claude Code 2.1.278
on Windows 10). Read `CAP_REWORK_BRIEF.md` first; this file is the state of
the unfinished work. The commit that contains this file is the branch tip;
its hash is reported in the local Driver's final message, not here.

## 1. Base, branch, verified revision

| item | value |
|---|---|
| repository | `https://github.com/atlas-ocm/cost-aware-phenomenology` (`origin`) |
| base | `origin/main` = `e65b9af4b28d3c97950c667448a32c24adc44a0e` — identical to the revision the architect read; `git fetch --prune` confirmed no newer remote commit |
| research branch | `research/ameba-executable-cycle`, created from that base in a separate worktree (`F:/VibeCoding/CAP-wt-ameba-cycle`) |
| why a separate worktree | the maintainer's checkout `F:/VibeCoding/Shard-Theory/CAP` is on `main`, 28 commits ahead of `origin/main` (AICE / evidence docs, none touching `reference/python/cap` or `02_subsystems`) and carries uncommitted AICE candidate work; it was left untouched, and those 28 commits are **not** on this branch |
| verified code revision | `5b84998` (whole-route costs, run 009): full suite `1022 passed, 2 skipped`, five criteria re-run in a detached worktree (§2.11); the run-010 commit adds only `reference/python/scripts/build_execution_record.py` (path B's result, oracle green at that commit, suite unchanged). Earlier verified points: `bbbc26c` (936), `989a7e2` (941), `8d23161` (981; `scripts/check_repo.ps1` exit 0), `ebe0ba0` (1004), `fc87e62` (1011); always 2 skipped |
| commits on the branch (oldest first) | `602fa63` test(layout), `aa6048f` docs(budget), `bbbc26c` feat(budget), then `90e1c72` handoff, `7b24b6a` run 003, `2be76e6` run 003 correction, `989a7e2` feat(budget) Breach = Recovery-Only, `336af16` feat(spec) execution-record schema, `8d23161` feat(cap) execution-record validator, then `1db22cf` records (runs 004, 005a, 005b; execution records for 002/004/005a/005b; the prepared COM-Log link packet), `ebe0ba0` feat(cap) COM-Log link, `9942901` run-006 records, `26535dc` handoff wording, `2731484` run 007, `8bc15b5` run 007 revision 2, `68914ff` executed bytes of run 005a, `5a5e2e9` handoff wording, `fc87e62` feat(cap) record binding (run 008), `78a8598` run-008 records, `c0c8cba` prepared route-costs packet, `5b84998` feat(spec,cap) whole-route costs (run 009), `844bcca` run-009 records, `7bc4780` prepared comparison, then the run-010 commit (records, the landed builder script); comparison results on branches `cmp/run-010-path-A` (`71a0248`) and `cmp/run-010-path-B` (`fa10bfd`) |

Naming: the repository had no branch convention (only `main` had ever
existed); `research/<topic>` follows the brief's wording and the
`<prefix>/<name>` form used in the maintainer's sibling repositories.

## 2. What was actually changed, and which postconditions were checked

### 2.1 `602fa63` — the standard check was red in any checkout not named `CAP`

Baseline at `e65b9af4` in the research worktree: `30 failed, 894 passed,
2 skipped`; `check_repo.ps1` exit 1 at the unit-test step. Cause: two test
modules resolved `CAP_ROOT = parents[4] / "CAP"`. Fix: both resolve
`parents[3]`; the private external packs stay at `REPO_ROOT.parent / "Patch"`
and are skipped when absent. Checked: the two modules `30 passed, 2 skipped`;
full suite `924 passed, 2 skipped`; neighbour case with the external packs
reachable through a temporary junction `62 passed` (32 external cases
collected). Authored by NoMCP cheap_coder `gemma4:31b-cloud`; verdict
`ACCEPT` by `deepseek-v4.1-flash:cloud`; driver adjudicated. Record:
`validation_artifacts/ameba_cycle/run_001_layout_fix/`.

### 2.2 `aa6048f` — the TotalRisk trace named in the brief, resolved by evidence

`observer_budget.md` line 32 was the only carrier of `RiskWeight × P(failure)`;
`transition_cost.md`, `operator_admissibility.md`, the worked example
(60% = 25% + 35%), `com_log_schema.json` (`allowed_total_risk_percent` bounds
the plain sum), `budget_calculus.total_risk` and its 41 tests all bound the
plain sum of RiskWeights, and no artifact supplies a separate `P(failure)`.
The prose line was corrected; code and tests unchanged. Same family:
`GLOSSARY.md` gave RTF values 0.4 / 0.7 / 1.0 against the doc ranges and
`MODE_RTF_RANGE`; corrected to the ranges. Found afterwards: `spec/operator_alphabet.json`
(`risk_tolerance_factors`, v1.1) also carries 0.4 / 0.7 / 1.0, so the glossary was not the
only carrier and that correction chose a side without seeing the spec; the glossary now
names both, and the spec-vs-doc/code discrepancy is open (§5). No code reads the
alphabet's values. Driver-authored, docs only.

Deferred, not dropped: if `P(failure)` is ever meant to be a separate axis, it
needs a producer (no schema, case or COM-Log carries it today) and a decision
whether `RiskWeight` stays the probability-weighted band.

### 2.3 `bbbc26c` — telemetry ceiling and numeric admissibility rule (the executable-cycle step)

`telemetry_gating.md` (ceiling table) and `operator_admissibility.md`
(telemetry-then-budget rule) had no code. Added to `budget_calculus.py`,
additively: `TELEMETRY_MAX_RISK`, `max_permitted_risk(state)`,
`operator_admissibility(risk_weight, active_operator_risks,
allowed_total_risk, telemetry_state) -> "admissible" | "blocked_by_telemetry"
| "blocked_by_budget"`; 12 tests (`cgm_03`, the worked example, Breach
pause-only, ordering, equality, ValueError). Items 3–5 of the rule are
deliberately **not** encoded (both docs now say so in a Numeric Contract
section). Authored by NoMCP fallback_coder `deepseek-v4.1-flash:cloud` after
`gemma4:31b-cloud` satisfied the oracle but deleted two existing constants
(caught by the module's own tests, attempt set aside); verdict `ACCEPT` by
`glm-5.3-flash:cloud`; driver adjudicated. Record:
`validation_artifacts/ameba_cycle/run_002_telemetry_admissibility/`.

### 2.4 Handoff commit — docs and records only

`CAP_REWORK_BRIEF.md` (verbatim copy of the brief, once),
this file, `validation_artifacts/ameba_cycle/` (two run records),
`REPRODUCIBILITY.md` (expected test result on a clone; layout note),
`validation_artifacts/README.md` (index entry).

### 2.5 Run 003 — evidence only, no transition

`validation_artifacts/ameba_cycle/run_003_numeric_coverage/`: what the new
gate can decide from the 25 pack cases. 0 of 25 carry structured operator
risk weights; with driver transcription of the prose numbers the gate agrees
with `cgm_03`, contradicts `cgm_07` (the ceiling table's Breach = 0 blocks the
stabilizers Fixation 20 / Hold 10 / Cleanup 15 that the Breach row, the Budget
Recovery paragraph and the validated case permit; correction_001 in the run
directory fixes an earlier "Boundary" transcription slip), classifies `pal_h01`'s 40% as `depleted` where the
prose says "partial" (behaviour consistent), and cannot touch `cgm_06`
(no persistent-fault code). `02_subsystems/telemetry_gating.md` now flags the
Breach contradiction as open next to its Numeric Contract. Nothing was
changed to make either side green.

### 2.6 `989a7e2` — Breach is Recovery-Only, decided by operator identity

Operator decision of 2026-09-24 executed and verified (run 004). The alphabet's
`Recovery-Only` gate carries a machine-readable `permitted_operators` list;
`operator_alphabet.budget_gate_permitted_operators` reads it (no guessing from
prose); `TELEMETRY_MAX_RISK` has no breach key; `max_permitted_risk("breach")`
is `None`; `operator_admissibility(operator, risk_weight, active_operator_risks,
allowed_total_risk, telemetry_state)` returns `not_computed` for any missing
input, `blocked_recovery_only` for a non-recovery operator at Breach whatever
its weight, the budget check for recovery operators, the unchanged
ceiling-then-budget rule elsewhere. The zero-risk-at-Breach test is gone. Docs
aligned by the driver. Authored by `deepseek-v4.1-flash:cloud` after
`gemma4:31b-cloud` failed on a missing `import pytest`; verdict `ACCEPT` by
`glm-5.3-flash:cloud`. Record: `run_004_breach_recovery_only/`.

### 2.7 `336af16` + `8d23161` — the executed-transition record (the binding the operator asked for)

The operator's probe showed that a Release Gate `pass` with unresolvable
references and a Mirror Frame without any `evidence_ref` both pass JSON Schema.
`spec/transition_execution.schema.json` binds one executed transition: object
and revisions before/after, the candidate and its postcondition defined before
execution, the actor / tool / hashed inputs / receipt, the re-observation,
per-criterion checks with result references (a `pass` needs exit 0; a
`postcondition_met` record needs every check passing), divergence fed back,
measured costs apart from estimates (`money` is `"unknown"` or a number),
`identity_independently_verified` explicit. `cap/execution_record.py`
resolves every reference, input hash, git revision and criterion coverage and
returns problems instead of raising; `scripts/validate_execution_record.py` is
the CLI; the boundary "schema accepts, validator rejects" is a test. Real
records: `run_004_breach_recovery_only/transition_execution_record.json` and,
retroactively, `run_002_telemetry_admissibility/transition_execution_record.json`,
each with its checks re-run by the driver at the obtained revision in a
detached worktree and the outputs kept as files (`checks/`). Records of the
change itself: `run_005a_execution_record_schema/` and
`run_005b_execution_record_validator/` (the unsplit task failed twice first: a
relay-hosted route killed at the 600 s tool ceiling, then a detached route whose
fallback hit its own 600 s wall; see the 005a README and `failed_route/`).

### 2.8 `ebe0ba0` — candidate step ↔ COM-Log record, with risk-weight provenance (run 006)

Operator's item 2 executed: `adjustment_step` gains an optional `com_log_ref`;
`cap/candidate_gate.py` gates a linked step from the COM-Log record and the
cycle state through `operator_admissibility`, keeps `risk_weight_source` /
`estimate_status`, returns `not_computed` with a reason for any missing link or
input, and marks every record as not full admissibility. Full suite `1004 passed, 2 skipped`.
The prepared packet under `prepared/com_log_link/` is the one that ran. Record:
`run_006_com_log_link/`.

### 2.9 Run 007 — review of `26535dc`: what the validator binds, and corrections

The review reported, and `run_007_record_binding_gap/` reproduces on the
shipped example, that `validate_execution_record` accepts a record whose stored
result says `exit=1` while the record says pass, a check made at another
existing revision, a check command that differs from its criterion, and a stray
text file as receipt with `provenance_established: true`. Cause: the validator
resolves references, hashes, revisions and coverage and never reads a stored
result. So the "binding" of §2.7 holds for the existence and identity of the
referenced files, not yet for their content. The next bounded step is prepared
and not executed (§7, item 0). Corrections made without code: `execution.tool`
of the records of runs 005a, 005b and 006 (their coding routes ran detached;
only the verdict stage was relayed); whole-route costs per run in
`route_costs_correction_001.json` (the records hold the closing attempt only);
run 005a's stored packet differs from the executed bytes by line endings
(correction_003 there). All records at this commit still pass the validator as
it is. No code changed in this commit; the full suite was not re-run for it.

### 2.10 `fc87e62` — the execution record bound to its stored carriers (run 008)

The packet prepared in run 007 (revision 2) executed as written through the
installed NoMCP path B relay inside one native Workflow. `validate_execution_record`
gains four binding rules, each a named problem: one `exit=` line in a stored
result equal to `exit_code`; `checks[].command` equal to the criterion's
`check_command`; the checked, re-observed and object revisions resolving
through `git rev-parse` to one commit (with `--repo` only); with
`provenance_established`, the receipt's `decision`, closing-attempt
`model_served` and `inputs.packet` / `inputs.check_files` hashes matching
by value, nothing else counting. Example stand-ins updated; seven tests
added; existing checks and strings unchanged. Statuses, kept apart: route
`CHEAP_PASS` (gemma4:31b-cloud, 12 turns, 9,315 output tokens, 58.5 s; the
first cheap close since run 001); verdict `ACCEPT` by `deepseek_v41_flash`;
checks c1–c6 re-run at `fc87e62` in a detached worktree, all exit 0; driver
acceptance on the diff; transport: the launch finished in the foreground
(71 s), so the path B wait mechanism was not exercised. Consequences: the
original run 005a record is refused on its stored input hash (negative
control, intended) and a corrected record referencing the stored executed
bytes resolves beside it; runs 002, 004, 005b, 006 and the example resolve.
Record: `run_008_record_binding/`, the first built under the new rules.
A passing record now means the named links between the record and its
stored carriers are checked; full provenance is still not established.

### 2.11 `5b84998` — the record carries whole-route costs bound to the receipt (run 009)

Schema 0.2: `schema_version` enum 0.1/0.2; optional `costs.route` (every attempt
in order with role, `model_served`, turns, output tokens, wall; `turns_total`;
`output_tokens_total`; `router_wall_s`), required when the version is 0.2.
Validator rules 5 and 6, each a named problem: `costs.route` must equal the
receipt's attempts (`first_attempt`, plus `fallback_attempt` when
`fallback_used`), their sums and `total_wall_s`; `costs.measured` must equal the
receipt's closing attempt. The closing attempt never stands in for the route.
Historical 0.1 records keep resolving; the example is a 0.2 record; eleven
tests added. Statuses, kept apart: route `FALLBACK_PASS` (gemma4 set aside on
its own tests; deepseek-v4.1-flash closed it; whole route 76 turns, 59,053
output tokens, 422.6 s against the closing attempt's 52 / 43,932 / 321.0);
verdict: first `OBJECT` by `glm53_flash` on a stray empty file the worker left,
removed by the driver (one recorded intervention), second `ACCEPT` on the
cleaned tree; checks c1–c5 re-run at `5b84998`, all exit 0; transport: path B
exercised (background launch, eight `wait` calls, `COLLECTED`) on the second
launch, the first killed by a relay deviation (it read the output file instead
of waiting). Record: `run_009_route_costs/`, the first 0.2 record, with its
`record_spec.json` committed so a repository script can rebuild it (§7 item 2).

### 2.12 Run 010 — Adjustment against a fixed baseline path: one pair, a probe

The same bounded change (a repository script that rebuilds run 009's record
from its artifacts and `record_spec.json`) was routed twice from `7bc4780`
through the same NoMCP mode-1 route inside one Workflow of four relays: path
A with a packet that states goal, CLI, inputs, exit codes and checks (no
Mirror Frame, no candidate), path B with the same packet plus the observed
derivation from a Mirror Frame and the forbidden outcomes of a
CandidateTransition; same oracle, same checks, own worktrees, A first, B not
informed by A; design, cost method and hypotheses fixed beforehand
(`prepared/adjustment_comparison/README.md`). Both paths: cheap tier set
aside on the oracle's fourth case, fallback closed, verifier `ACCEPT` (A after
a provider deadline on its first call), checks re-run at `71a0248` / `fa10bfd`.
Route: A 55 turns, 39,217 output tokens, 315.9 s; B 52 / 32,351 / 307.1 s;
driver authoring A about 2 min, B about 7 min. H1 (fewer attempts) not
supported; the token and wall difference is within what one pair cannot
separate from noise; H0 not rejected. Both cheap attempts failed the oracle's first case (the
plain rebuild) on resolving `checks[].result_ref` (A invented the check-file
names, B joined the ref onto the run directory) and its fourth case (a
construction detail of the oracle); packet A said nothing about `result_ref`,
packet B named it and called record paths repo-relative without saying that
`result_ref` resolves against the repo root. Corrected on 2026-09-25 after the
NoMCP session's reading of the receipts (run 010 README, correction_001); the
first wording named c4 only and called the miss packet-independent. Path B's script landed by a rule chosen after the
results (lower whole-route cost among the accepted). Path A has no execution
record: the record schema presupposes a Mirror Frame and a candidate. Record
and comparison: `run_010_adjustment_comparison/`. A second pair from the same
base with the same packets (01:33–01:52; results on `cmp/run-010-pair2-path-A|B`,
records under `pair_2/`): route A 51 turns / 32,896 output tokens / 305.8 s, B
32 / 24,319 / 267.5 s; both cheap attempts set aside again, for different reasons
than in pair 1. Across the two pairs B is cheaper than A on every route unit, and
the within-path swing between pairs is as large as the between-path difference:
a consistent direction, not an established effect.

## 3. Exact commands, dependencies, inputs and outputs

Environment used locally: Python 3.12.10, pytest 9.0.0, jsonschema 4.26.0
(`reference/python/requirements.txt`), git 2.51, Windows 10, PowerShell 5.1.

```bash
# unit tests (the only test command; works on any OS)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p no:cacheprovider reference/python/tests
# expected on a standalone clone, per revision: bbbc26c 936 passed; 989a7e2 941; 8d23161 981; ebe0ba0 1004; fc87e62 1011; 5b84998 and every later commit 1022; always 2 skipped

# the remaining steps of scripts/check_repo.ps1, as plain Python (the .ps1 needs PowerShell)
python -m compileall -q reference/python
python reference/python/scripts/validate_artifacts.py                 # Total issues: 0
python reference/python/scripts/memory_dreaming/validate_example.py
python reference/python/scripts/aice/check_aice.py
python reference/python/scripts/validate_extension_case_packs.py     # 0/0 + [warn] pack missing is expected on a clone
python reference/python/scripts/run_proxy_policy_pack.py --print-md  # Passed: 8, Failed: 0
python reference/python/scripts/demo_llm_proxy_policy.py --counter-source
python reference/python/cap_lite.py
python reference/python/scripts/run_llm_dialogue_benchmark.py --print-md

# executed-transition records: every reference, hash, revision and criterion must resolve
python reference/python/scripts/validate_execution_record.py validation_artifacts/ameba_cycle/run_004_breach_recovery_only/transition_execution_record.json --repo .
python reference/python/scripts/validate_execution_record.py validation_artifacts/ameba_cycle/run_002_telemetry_admissibility/transition_execution_record.json --repo .
```

The full script (`.\scripts\check_repo.ps1`) also renders prompt manifests,
adjudication packs and the rewrite-shaper smoke into `$env:TEMP`; on Linux run
it with `pwsh` if available, otherwise the Python steps above cover every
correctness check it performs.

Validating a run record against the schemas:

```bash
python - <<'EOF'
import json, jsonschema
for s, d in (("spec/mirror_layer.schema.json", "validation_artifacts/ameba_cycle/run_002_telemetry_admissibility/mirror_frame.json"),
             ("spec/adjustment_layer.schema.json", "validation_artifacts/ameba_cycle/run_002_telemetry_admissibility/candidate_transition.json")):
    errs = list(jsonschema.Draft202012Validator(json.load(open(s, encoding="utf-8"))).iter_errors(json.load(open(d, encoding="utf-8"))))
    print(d, "VALID" if not errs else [e.message for e in errs])
EOF
```

Inputs and outputs of the two executor runs are inside the run directories
(`coding_packet.json` -> `nomcp_coding_receipt.json`; `verify_packet.json` ->
`nomcp_verdict_receipt.json`). The ephemeral oracle of run 002 is copied as
`oracle_admissibility.py`; run it from the repository root with `python -B`.

## 4. Component map (promised -> code -> check -> boundary)

Built to choose the first change; scope of the negative searches: `grep -rn`
over `reference/python`, `spec/`, `02_subsystems/`, `04_extensions/` at
`e65b9af4`, plus CodeGraph (74 files indexed).

| component | promised behaviour (doc) | actual code / extension point | existing check | boundary of confirmation / gap |
|---|---|---|---|---|
| Transition cost | cost = Σ resource costs + RiskWeight×FailureCost + rollback + cross-domain drain; risk bands | `budget_calculus.classify_risk_zone`, `total_risk` | `test_budget_calculus.py` | only the band arithmetic is code; no cost decomposition, rollback or drain arithmetic; `CandidateTransition.cost` is five ordinal bands, no units |
| Observer budget | AllowedTotalRisk = budget × RTF; bands; three modes; defer/downgrade/pause | `allowed_total_risk`, `classify_budget_state`, `permitted_risk_zones_for_budget`, `cycle_decision` | same | `cycle_decision` picks defer/downgrade/pause by a fixed rule; no search for a lower-risk substitute; TotalRisk prose fixed in `aa6048f` |
| Telemetry gating | four states from signals; ceiling table; auto-downgrade | **new** `TELEMETRY_MAX_RISK`, `max_permitted_risk` (`bbbc26c`) | new tests | state *classification from signals* has no code; `validator.py` only checks Breach ⇒ Recovery-Only |
| Operator admissibility | five-item rule; downgrade sequence | **new** `operator_admissibility` (items 1–2) | new tests incl. `cgm_03` and the worked example | items 3–5 (preconditions, SplitPoint alignment, reversibility) not encoded; no downgrade-sequence search |
| COM Grammar | 13 operators, 16 statuses, COM-Log v1.1, reverse-first parse | `spec/com_log_schema.json`, `operator_alphabet.json`, `validator.validate` | schema tests; falsifiability claim 7 | structure only; no text→COM-Log parser (ROADMAP v0.3) |
| Adjustment dynamics | route reweighting, Markov/Schrödinger bridges, BudgetGate over routes, leakage screen, anti-collapse | `spec/adjustment_layer.schema.json` + example | 44 schema tests (ADJ-01..10); `validate_extension_case_packs.py` | invariants only; no route computation, no bridge, no route-level budget gate in code; validation = 3-LLM label agreement on 17 prose cases |
| Mirror | declared / observed / expected / unknown; observability verdict | `spec/mirror_layer.schema.json` + example | 31 schema tests | no observer code; in runs 001/002 the frame was written by the driver from git/pytest/grep |
| Looking-Glass, Latent Cause | retrodiction, A-reconstruction | schemas + examples; 32 external cases | tests parametrized over the packs | packs live in the private parent checkout (`Shard-Theory/Patch`); absent on a clone → `2 skipped`, `0/0` |
| Release gate | possible → permitted; lexical proxy gate | `proxy_release_gate.py` (dialogue text), `release_gate.schema.json` | tests, hard-holdout reports | the lexical gate targets dialogue outputs, not code changes; the commits here were gated by NoMCP verdicts + driver, not by CAP code |
| Context hygiene, anchor decay, cross-domain drain, role orchestration, DSSD, witness independence, anti-drama, guardrails, cycle state machine | runtime disciplines | schemas + examples only | schema tests | no runtime; "no self-review" was applied by route shape, not by CAP code |
| Memory Dreaming | offline recompilation with release gate | `spec/memory_dreaming/` + example + `validate_example.py` | schema tests | no runtime |
| CAP Lite | policy middleware before an LLM call | `cap_lite.py` | 4 tests | dialogue policy, not the transition cycle |
| Falsifiability | seven claims | `falsifiability_gates.py` (claims 1, 7) | 12 tests | claims 2–6 deferred by manifest |
| Deterministic baselines (Tier 1 of methodology.md) | "a non-LLM core implementation runs the case pack" | not in the repository; only expected labels per case | `validate_artifacts.py` checks model_runs exist and match ids | Tier 1 is not reproducible from the repository; `deterministic_baseline.json` is an aggregate of hand-set expectations |

## 5. Decisions: kept, merged, removed, deferred

- Kept: every layer as documentation and schema; `budget_calculus.py` as the
  single numeric seam (extended, not duplicated); the existing artifact
  formats for the run records; the repository's own check as the postcondition.
- Merged: nothing. Removed: nothing — no ablation has been run yet, so no
  layer's contribution is established either way (see §7).
- Deferred with reasons: `P(failure)` as a separate axis (no producer); items
  3–5 of admissibility (no inputs); a downgrade-sequence / candidate selector
  (no reproduced failure asks for it yet); a cycle runner script (would be a
  mechanism ahead of a failure); vendoring the external packs (private).
- Decided by the operator on 2026-09-24 and executed: Breach = Recovery-Only
  by operator identity (`989a7e2`). Decided and executed in run 006 (§2.8): the
  six risk axes and the cost bands stay; no conversion to percent; the gate's
  inputs come from a linked COM-Log record and the cycle state; the RiskWeight's
  source and estimate status are recorded; missing inputs give `not_computed`
  (packet, oracle and verify stage under `prepared/com_log_link/`).
- Decided by the operator the same evening and executed: the executed-transition
  record with a reference-resolving validator (§2.7) is the binding every future
  run must produce; a numeric gate may be part of it, the binding comes first.
- Open: which RiskToleranceFactor carrier is canonical: `observer_budget.md` +
  `MODE_RTF_RANGE` (0.5-0.7 / 0.7-0.85 / 0.85-0.95) or `spec/operator_alphabet.json`
  `risk_tolerance_factors` (0.4 / 0.7 / 1.0). Recommendation received with the
  review of `26535dc`: keep the docs + `MODE_RTF_RANGE` policy as canonical
  (Conservative 0.5-0.7, Nominal 0.7-0.85, Expansion 0.85-0.95), align the
  alphabet with it and name one source of the values; an engineering-policy
  choice that keeps current behaviour, not a proof of the numbers; the values
  are to be marked as engineering-assigned. Repeated by the reviewer of
  `8bc15b5`. Not executed: the alphabet change is a spec mutation for the
  ordinary coding route, after the operator confirms.
- Decided after the review of `26535dc` (run 007): costs of a transition are
  the whole route (every attempt, baseline, checks, verifier), not the closing
  attempt; the records keep the closing attempt until the schema has a place
  for route totals, and `route_costs_correction_001.json` carries the whole
  route per run meanwhile. A record that passes the validator is not, by that
  fact alone, a record whose stored results support it, until §7 item 0 lands.
- Rejected hypotheses: rename the checkout to `CAP` (hides the assumption);
  encode the whole five-item rule with invented inputs; treat one green
  trajectory as evidence of minimal cost.

## 6. Constraints, baseline failures, unknowns

- Baseline failures separated from changes: the 30 layout failures and the
  `check_repo.ps1` exit 1 existed at `e65b9af4` in any checkout not named
  `CAP`; they are not caused by this branch.
- Governance gaps reported honestly (Level 3): the `cap-probe` MCP
  (`start_task`, `log_episode`) is stopped by the brief's instruction, so no
  episode was logged and no `RoleTaskSpec` was obtained; routing followed the
  NoMCP policy (cheap coder → checks → fallback; explicit verifier ≠ coder;
  driver adjudicates; driver never edited code or tests). Commit and push of
  the research branch are authorized by the brief; nothing was merged to
  `main`, no tag, no force-push.
- Unknowns kept as unknown: money cost of model calls (subscription-served,
  no price exposed); served-model identity is the executing CLI's report, not
  an independent probe; whether the cloud platform can run the NoMCP shim
  (it cannot: local Ollama and a local checkout — see §8).
- Local-only state that is not on the branch: Gemma's set-aside attempts
  (stashes `33843e76`, `6e7b4e56` and the run-005 one, in the local worktree); the raw scratch receipts (copied
  into the run records); the Workflow transcripts; the 28 unpushed commits on
  the maintainer's `main`.
- NoMCP: `d0d9b6c` on the NoMCP master is an in-flight state record of the
  relay-ceiling facts, not a fix of the relay expectation; the transport
  decision is still open there. Update at the end of the evening: the reviewer
  of `2731484` recommended option B (a launch-then-wait rule: the relay waits
  for its own run) and the operator chose it. Per the NoMCP report, path B is
  installed; the integration of the installed components was checked in
  `claude -p` with fake executors. Work on an ordinary task in the local app
  is not yet confirmed (a snapshot-speedup task was proposed for that check;
  CAP does not need to wait for it). Run 008 (§2.10) went through the
  installed relay text; its launch finished in the foreground (71 s), so the
  wait mechanism was not exercised. Run 009 (§2.11) exercised it: background
  launch, eight `nomcp.py wait` calls, `COLLECTED`, receipt bound; the first
  launch of that run was killed because the relay read the output file instead
  of waiting (a prompt-wording class, reported to the NoMCP window). The status
  wording is the NoMCP session's to update on this evidence.

## 7. Next concrete unfinished step

0. **Done in run 008 (`fc87e62`, §2.10): the execution record bound to its
   stored results.** Prepared in run 007 and executed as written. Packet `prepared/record_binding/coding_packet.json`;
   oracle `run_007_record_binding_gap/probe_record_binding.py --expect-closed`
   (exit 1 today, red for the named reason); declared checks: the oracle, the
   validator and schema tests, run 006's record still `OK`. Four rules, each a
   named problem: one `exit=` line in the stored result equal to `exit_code`;
   `checks[].command` equal to the criterion's `check_command`;
   `revision_checked`, the re-observed revision and `object.revision_after`
   resolving through git to one commit (a short and a full SHA are one
   object; applied only with `--repo`); with `provenance_established`, a
   receipt in the router's shape whose specific fields match: top-level
   `decision`, the closing attempt's `model_served` (`fallback_attempt` when
   `fallback_used`, else `first_attempt`), and every hashed input among
   `inputs.packet.sha256` / `inputs.check_files[].sha256`; text anywhere else
   in the receipt counts for nothing. Revised after the review of `2731484`,
   which showed that the first wording ("the receipt text contains the
   values") accepts the right words in the wrong fields. The oracle (revision
   2) requires each negative case to be refused with its named problem and
   keeps three positive controls (unmodified example; router-shaped receipt
   whose fields match; short SHA of the same commit). Acceptance: every
   expectation of the oracle holds, run 006 still resolves, the original record
   of run 005a is refused by rule 4(c) (documented, intended: the negative
   control pins the detection of the byte mismatch, not a permanent refusal
   of that run; a corrected record that references the stored executed bytes
   may pass and is a separate file). A green run means the named
   links between the record and its stored carriers are checked; it does not
   establish full provenance of the execution.
   Landed as prepared; every acceptance item observed (checks c1–c6 of run
   008; the corrected run 005a record resolves, the original is refused).
   Whole-route costs: done in run 009 (`5b84998`, §2.11); every record from
   run 009 on is a 0.2 record whose `costs.route` is bound to its receipt.
1. Reproduce on the cloud clone: the pytest command in §3 must give, per
   revision: `bbbc26c` 936 passed, `989a7e2` 941, `8d23161` 981, `ebe0ba0`
   1004, `fc87e62` 1011, `5b84998` and every later commit 1022, always 2 skipped; record the clone's directory name
   and OS as an environment difference, not a defect.
2. Baseline path fixed and run once (run 010, §2.12; design in
   `prepared/adjustment_comparison/README.md`). As proposed: for one bounded change on this repository, run it twice from
   the same commit — (a) the executor route alone (packet, checks, verdict,
   driver) and (b) the same route preceded by a Mirror Frame and a
   CandidateTransition — and compare on the brief's five axes (postcondition
   met and constraints violated; unverified completion claims; interventions,
   retries, regressions, rollbacks; time and tokens in their own units; new
   evidence produced). Two runs of one change is a probe, not a result.
   Result of the one pair: both paths reached the postcondition after one
   cheap set-aside each; B's route was cheaper by 3 turns, 6,866 output
   tokens and 8.8 s, at about five more minutes of driver authoring; one pair
   does not separate that from noise. Pair 2 (same packets, no new authoring):
   B cheaper again on every route unit (32 / 24,319 / 267.5 s against
   51 / 32,896 / 305.8 s), four cheap set-asides in four routes; direction
   consistent over two pairs, magnitude within the within-path swing.
3. Done: Breach = Recovery-Only (`989a7e2`, run 004) and the executed-transition
   record (§2.7, runs 005a and 005b). Every further run must produce a
   `transition_execution_record.json` that passes
   `validate_execution_record.py --repo .`; a run without one is not a
   verified transition, whatever its README says. Since `fc87e62` a passing record also has its stored results agreeing
   with it on the named links (run 008, §2.10); full provenance of the
   execution is still not established.
4. Done in run 006 (§2.8): the COM-Log link. Its acceptance items 1–4 are the
   oracle; item 5 (a candidate through the whole chain to a verified
   postcondition) is the run's execution record. What is still missing: no real
   candidate step has a COM-Log record yet, so no real transition has been
   numerically gated; the first will carry an engineering-assigned RiskWeight.
   Superseded text kept for reference: the COM-Log link
   (`validation_artifacts/ameba_cycle/prepared/com_log_link/`: `coding_packet.json`
   is the task text and declared checks, `oracle_link.py` the postcondition,
   `verify_stage.py` the packet builder). Acceptance, from the operator: an
   admissible stabilizer at Breach within budget passes the numeric check; an
   operator outside Recovery-Only is blocked even with a small weight; a
   stabilizer over budget is blocked; missing inputs never give a positive
   result; at least one candidate passes the whole chain to a verified
   postcondition, recorded as an execution record. A numeric pass is still not
   full admissibility (items 3–5 unchecked).
5. Then the main question, now answerable: does Adjustment help choose a
   cheaper reachable transition and reach a verified result? Fix the baseline
   path first (item 2), run the next real change both ways, and compare the
   two execution records on the brief's five axes. A green gate alone does
   not answer it. Fix the baseline path and the same required postcondition
   beforehand: one successfully executed task with Adjustment shows only the
   cost of that execution, not a reduction of the full cost of reaching the
   postcondition.
   Status after run 010: not established either way from one pair (item 2).
   Next: more pairs, on tasks where the two packets differ in exactly what
   the cheap tier tends to miss, with the driver's authoring time measured;
   and a decision on the path-A record problem (the record schema presupposes
   a Mirror Frame and a candidate, so a baseline path cannot be recorded as a
   verified transition; run 010 records path A as receipts, checks and a cost
   summary). The builder script from run 010 lets any driver build 0.2
   records: `python reference/python/scripts/build_execution_record.py . <run_dir> <run_dir>/record_spec.json --out <path>`.
6. Still open from data: whether Adjustment's route-level BudgetGate
   (`adjustment_dynamics.md` §Budget Gate) should be code, or whether the
   per-operator gate is sufficient.

## 8. What is available from the cloud and what exists only locally

Available on the branch: all code, tests, docs, schemas, examples, the run
records 001–010 with verbatim receipts, the prepared packets, the comparison
branches `cmp/run-010-path-A` and `cmp/run-010-path-B`, the brief, this file.

Local only: the 32 external Looking-Glass / Latent Cause cases
(`F:/VibeCoding/Shard-Theory/Patch`); the NoMCP checkout (`F:/VibeCoding/Nomcp`)
and the shim (`~/.claude/nomcp/`), which need a local Ollama endpoint — in the
cloud the executor is whatever the platform provides; keep the same route
shape (a coder that is not its own verifier, an explicit verifier, a
postcondition that is an existing repository check, the driver adjudicating)
and record the requested and served model identity as the platform reports
it; the maintainer's checkout with its 28 unpushed `main` commits and
uncommitted AICE work; the scratchpad with raw receipts and Workflow
transcripts; the executed bytes of run 005a's packet (CRLF, 8,296 bytes,
sha256 `08111685...`, the receipt's `inputs.packet.sha256`): the router keeps
its copy under the out dir it was given, `<scratchpad>/out_coding/inputs/<sha>`
(`inputs.packet.saved` is relative to that out dir, confirmed by the NoMCP
session), and that copy plus the driver's `tasks5a.json` were copied unchanged
to `F:/VibeCoding/CAP-retained-inputs/`. On the reviewer's recommendation the
router copy is now also on the branch as
`run_005a_execution_record_schema/coding_packet.executed.08111685.json` with a
`-text` entry in `.gitattributes` for that exact path (the general
`* text=auto eol=lf` rule stays); blob and fresh-checkout bytes verified
(8,296 bytes, sha256 `08111685...`), so the cloud has the original without
depending on a local disk.
