# Adjustment Layer — Validation Results

Status: `research-only / three-model identity-verified / holdout clean`
Date: 2026-05-02

---

## Headline Numbers

```text
Deterministic baseline (main):             8/8  expectation_mismatch_count = 0
Deterministic baseline (holdout):          9/9  expectation_mismatch_count = 0

comet_12b_v.7-i1            verdict/primary: 8/8 (main) / 9/9 (holdout)
silicon-maid-7b-imatrix     verdict/primary: 8/8 (main) / 9/9 (holdout)
fimbulvetr-11b-v2           verdict/primary: 8/8 (main) / 9/9 (holdout)
```

All three identity-verified models reached 8/8 on the main pack and 9/9 on the holdout pack. Identity verification (LM Studio `/v1/models` query and response-model field match) was enforced for all model runs.

---

## Main Case Pack

8 cases, all prefixed `pal_`. Each case probes a specific Adjustment Layer guard or routing mode.

| Case ID | Mode / Guard Tested | Expected Verdict |
|---|---|---|
| `pal_01` | Desire Pressure — admissible forward route under Full budget | `desire_pressure_route_admissible` |
| `pal_02` | Desire Pressure — route blocked by leakage screen | `leakage_invalidated` |
| `pal_03` | Problem Pressure — recovery routing from damage state | `problem_pressure_route_admissible` |
| `pal_04` | Markov Bridge — admissible intermediate states | `markov_bridge_constructed` |
| `pal_05` | Schrödinger Bridge — minimal distribution deformation | `schrodinger_bridge_minimal` |
| `pal_06` | Budget Gate — route exceeding budget blocked | `budget_blocked` |
| `pal_07` | Anti-Collapse Guard — output attempting to collapse into generic domain advice | `anti_collapse_advice_rejected` |
| `pal_08` | Looking-Glass chain — upstream bridge informs forward routing | `lg_chain_routes_from_upstream` |

The case pack lives in `Patch/adjustment_layer_case_pack.md` and `Patch/adjustment_layer_cases/`.

---

## Holdout Case Pack

9 fresh cases, all prefixed `pal_h_`. The holdout cases are not derived from the main pack; they probe boundary conditions and edge cases that the main pack does not cover.

Key holdout boundaries:

- **Anti-collapse advice on relationship domain** — model attempts "communicate more / set boundaries" slogan instead of route reweighting
- **Symptom-only repair while leakage active** — model attempts to close the visible symptom (e.g., incident budget overrun) without addressing upstream margin depletion
- **Cross-domain leakage screen** — route in one domain (e.g., work recovery) that consumes budget from another (e.g., body margin) is correctly invalidated
- **Underdetermined upstream bridge** — Looking-Glass produces multiple plausible upstream candidates; Adjustment Layer must route conservatively
- **Dependent-being anchor preservation** — care-floor anchor (pet, child, elder) is preserved during recovery routing
- **False repair recognition** — apology + gift without behavioral change recognized as false repair, not as resolution
- **Unilateral repair labor leakage** — relationship-recovery route requiring one-sided sacrifice flagged as leakage
- **Reserve-rebuild precedence** — recovery routing places reserve rebuild before reactivation of generosity
- **Status-credit pressure invalidation** — gift-credit pressure recognized as leakage rather than warmth

All 9 holdout cases passed across all three models with verdict and primary reading aligned.

The holdout pack lives in `Patch/adjustment_layer_holdout_case_pack.md` and `Patch/adjustment_layer_holdout_cases/`.

---

## Authoritative Artifacts

**Deterministic baseline (main):**
```text
Patch/adjustment_layer_non_llm_core_2026-05-02/adjustment_layer_non_llm_core_summary_compat.json
```

**Deterministic baseline (holdout):**
```text
Patch/adjustment_layer_holdout_non_llm_core_2026-05-02/adjustment_layer_holdout_non_llm_core_summary_compat.json
```

**LLM comparison report (main):**
```text
comparison_reports/adjustment_layer_llm_model_comparison.md
```

**LLM comparison report (holdout):**
```text
comparison_reports/adjustment_layer_holdout_llm_model_comparison.md
```

**Final status note:**
```text
Patch/adjustment_layer_final_status_note.md
```

---

## Permitted Use

```text
desire-pressure input  -> admissible forward path reweighting (no delivery guarantee)
problem-pressure input -> bounded recovery routing from damage state
Markov bridge          -> admissible intermediate states without impossible jumps
Schrodinger bridge     -> minimal path distribution deformation under new constraints
budget gate            -> blocks expensive routes when observer budget exhausted
leakage screen         -> invalidates routes with known structural leakage
Looking-Glass chain    -> upstream bridge informs forward routing
```

## Not Permitted Use

```text
generic domain advice
coaching or motivational psychology
delivery guarantees
impossible route construction
advice collapse into non-structural reading
symptom-only routing when upstream bridge is available
```

---

## Chain With Looking-Glass

```text
Looking-Glass diagnoses:   observed outcome -> upstream bridge -> split point
Adjustment Layer routes:   current pressured state -> admissible future trajectory
```

These must not be collapsed. They are sequential, not interchangeable. When the chain is active, the Adjustment Layer routes from the depleted source state identified by Looking-Glass, not from the visible symptom.

---

## What This Validation Supports

- The Adjustment Layer's two input modes (Desire Pressure / Problem Pressure) are distinguishable across models.
- The two bridge constructions (Markov / Schrödinger) produce model-consistent outputs on the validation cases.
- The three guards (Budget Gate, Leakage Screen, Anti-Collapse Guard) fire correctly across models on both main and holdout packs.
- The Looking-Glass chain integration produces routing that addresses the upstream bridge rather than the visible symptom.
- The framework's anti-collapse discipline holds under stress: models do not slide into generic domain advice, motivational coaching, or moralization despite strong default training in those directions.

## What This Validation Does Not Support

- A claim that the layer can guarantee delivery of any desired outcome
- A claim that the layer is a substitute for domain expertise (legal, medical, financial)
- A claim that route reweighting produces routes — it produces *admissible candidates*; whether they are executed and succeed is downstream
- Promotion beyond `research-only`

---

## Compression

```text
Three identity-verified models, eight main cases, nine holdout cases.
All three models match verdict and primary reading 8/8 main, 9/9 holdout.
The Adjustment Layer routes admissible paths under budget,
leakage, and anti-collapse constraints.
A path is not admissible because it is desired.
It is admissible because it is reachable within constraints.
```
