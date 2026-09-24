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
| verified code revision | `bbbc26c` (`feat(budget): ...`): full suite `936 passed, 2 skipped`; `scripts/check_repo.ps1` exit 0 in 46 s |
| commits on the branch (oldest first) | `602fa63` test(layout), `aa6048f` docs(budget), `bbbc26c` feat(budget), then the handoff commit `90e1c72` (this file, the brief copy, the run records, docs updates); then the run 003 commit (evidence record, docs flag, this update) |

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
`MODE_RTF_RANGE`; corrected to the ranges. Driver-authored, docs only.

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
stabilizers that the Breach row, the Budget Recovery paragraph and the
validated case permit), classifies `pal_h01`'s 40% as `depleted` where the
prose says "partial" (behaviour consistent), and cannot touch `cgm_06`
(no persistent-fault code). `02_subsystems/telemetry_gating.md` now flags the
Breach contradiction as open next to its Numeric Contract. Nothing was
changed to make either side green.

## 3. Exact commands, dependencies, inputs and outputs

Environment used locally: Python 3.12.10, pytest 9.0.0, jsonschema 4.26.0
(`reference/python/requirements.txt`), git 2.51, Windows 10, PowerShell 5.1.

```bash
# unit tests (the only test command; works on any OS)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p no:cacheprovider reference/python/tests
# expected on a standalone clone at bbbc26c: 936 passed, 2 skipped

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
- Open after run 003, operator decision, not a coding task: which reading of
  Breach is intended (ceiling 0% = Pause only, or the conservation band with a
  stabilizer whitelist); and whether a `CandidateTransition` should carry the
  gate's inputs (RiskWeight percent, telemetry state, AllowedTotalRisk) or a
  mapping from its [0, 1] risk axes is defined. The test and oracle of
  `bbbc26c` encode the table line and inherit the contradiction.
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
- Local-only state that is not on the branch: Gemma's set-aside attempt
  (stash `33843e76` in the local worktree); the raw scratch receipts (copied
  into the run records); the Workflow transcripts; the 28 unpushed commits on
  the maintainer's `main`.

## 7. Next concrete unfinished step

1. Reproduce on the cloud clone: the pytest command in §3 at `bbbc26c` or
   later must give `936 passed, 2 skipped`; record the clone's directory name
   and OS as an environment difference, not a defect.
2. Fix the baseline path before any comparison (brief §6). Proposed and not
   yet run: for the next bounded change on this repository, run it twice from
   the same commit — (a) the executor route alone (packet, checks, verdict,
   driver) and (b) the same route preceded by a Mirror Frame and a
   CandidateTransition — and compare on the brief's five axes (postcondition
   met and constraints violated; unverified completion claims; interventions,
   retries, regressions, rollbacks; time and tokens in their own units; new
   evidence produced). Two runs of one change is a probe, not a result.
3. Run 003 is done locally (see §2.5). It leaves an OPERATOR DECISION, not a
   coding task: which reading of Breach is intended. Do not change
   `TELEMETRY_MAX_RISK`, the docs, the test or the oracle to make either side
   green before that is decided; both readings and what each would change
   are in the run 003 README (F3).
4. Vocabulary gap to close before the gate can act inside the cycle (run 003,
   F6): a `CandidateTransition` carries six risk axes in [0, 1] and five
   ordinal cost bands and no telemetry state or AllowedTotalRisk; the gate
   consumes a RiskWeight percent, a telemetry state and an AllowedTotalRisk.
   Decide from the next real runs whether the candidate carries the gate's
   inputs or a mapping is defined; either is a schema change and goes through
   the ordinary coding route with the schema tests as the postcondition.
5. Then decide, from data, whether Adjustment's route-level BudgetGate
   (`adjustment_dynamics.md` §Budget Gate) should be code, or whether the
   per-operator gate is sufficient.

## 8. What is available from the cloud and what exists only locally

Available on the branch: all code, tests, docs, schemas, examples, the two run
records with verbatim receipts, the brief, this file.

Local only: the 32 external Looking-Glass / Latent Cause cases
(`F:/VibeCoding/Shard-Theory/Patch`); the NoMCP checkout (`F:/VibeCoding/Nomcp`)
and the shim (`~/.claude/nomcp/`), which need a local Ollama endpoint — in the
cloud the executor is whatever the platform provides; keep the same route
shape (a coder that is not its own verifier, an explicit verifier, a
postcondition that is an existing repository check, the driver adjudicating)
and record the requested and served model identity as the platform reports
it; the maintainer's checkout with its 28 unpushed `main` commits and
uncommitted AICE work; the scratchpad with raw receipts and Workflow
transcripts.
