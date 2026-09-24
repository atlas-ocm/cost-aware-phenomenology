# Run 003 — what the numeric gate can decide from the existing case packs

Status: `evidence run / research-only`. No transition was proposed or
executed; this run asks one bounded question of the repository and records
the answer. Files: `coverage.json` (per case, which structured fields could
feed the gate), `gate_outputs.json` (what `operator_admissibility` and the
budget functions compute on the cases that carry numbers). Everything was
computed by the functions in `reference/python/cap/budget_calculus.py` at
`bbbc26c`; no model was involved; wall time under one second.

Question: after `bbbc26c` made the telemetry ceiling and the numeric
admissibility rule executable, which of the 25 validation cases (8 COM
Grammar, 8 + 9 Adjustment Layer) can the gate actually decide, and does it
agree with the cases' expectations?

## F1. Coverage: the packs do not carry the gate's inputs

| structured field in `constraints` | cases |
|---|---|
| `telemetry_state` | 2 of 25 (`cgm_03`, `cgm_07`) |
| `allowed_total_risk` | 1 of 25 (`cgm_03`) |
| operator risk weights | 0 of 25 |
| percentages present only in prose (`summary` / `claim_attempt`) | 3 of 25 (`cgm_03`, `cgm_07`, `pal_h01`) |
| gate computable from structured fields alone | 0 of 25 |
| gate computable after the driver transcribes the prose numbers | 3 of 25 |

Reading: the packs validate *readings* (an expected verdict and label per
case), not *decisions*. The "non-LLM core implementation" of Tier 1 in
`03_validation/methodology.md` could not have been computed from these
inputs; either the cases need structured operator fields or a parser
(ROADMAP v0.3) has to produce them. The three transcriptions below are the
driver's, not a parser's, and are marked as such in `gate_outputs.json`.

## F2. `cgm_03` — the gate agrees with the case

Inputs: `telemetry_state = overheating`, `allowed_total_risk = 30` (both
structured); operators transcribed from prose: Inversion 80, Hold 10,
Fixation 20. Computed: Inversion `blocked_by_telemetry`; Hold `admissible`;
Fixation `admissible` with Hold active (total 30 = ceiling). This is the
downgrade the case expects.

## F3. `cgm_07` — the gate contradicts the case, and the docs contradict themselves

Inputs: `telemetry_state = breach` (structured); operators transcribed from
prose: Fixation 20, Hold 10, Boundary 15, a domain action 50;
`allowed_total_risk` is not given, 100 was used to isolate the ceiling.
Computed: all four `blocked_by_telemetry`; only a zero-risk operator is
admissible.

The case expects the opposite for the stabilizers: "only stabilizers
(Fixation 20%, Hold 10%, Boundary 15%) are permitted; domain actions above
50% are frozen", with three-model agreement recorded in
`validation_artifacts/com_grammar/`. The source of the disagreement is
inside `02_subsystems/telemetry_gating.md`:

- the Risk Throttling table: `Breach | 0% (Pause only)`;
- the Four Gate States row for Breach: "Pause on all active operators;
  Fixation on all Leaking nodes";
- the Budget Recovery paragraph: "in Breach state, the framework permits
  only stabilizers (Pause, Fixation)".

Pause/Hold carries 10% and Fixation 15–20% in every worked example and in
the conservation band (10–30%) of `transition_cost.md`, so a 0% ceiling
excludes the very operators the same document says Breach permits. The code
encodes the table as written; the oracle and the test added in `bbbc26c`
(`breach` permits only risk 0) encode the same table line and therefore
inherit the contradiction — they must not be read as settling it.

Two readings, each with what it would change:

1. Breach = 0%, Pause only. Then `cgm_07`'s expectation and the two prose
   passages are wrong and would change, and "Pause" would need a 0% risk
   weight that no example gives it.
2. Breach permits the conservation band (≤ 30%) restricted to stabilizer
   operators. Then the table line, `TELEMETRY_MAX_RISK["breach"]`, the test
   and the oracle change, and the gate needs an operator whitelist input it
   does not have today.

Which reading is intended is an operator decision; nothing here was changed
to make either side green.

## F4. `pal_h01` — a naming mismatch, not a behavioural one

The case calls a 40% budget "partial, not zero". The numeric contract
classifies 40 as `depleted` (30–50) and permits the conservation zone only,
which is consistent with the case's point (a cheaper route rather than a
total block). Only the band name differs from the prose.

## F5. `cgm_06` — persistent fault has no code

`cycles_open = 4 >= threshold = 3` is structured, but no function in
`reference/python` encodes the Persistent Fault Candidate rule; not
computable.

## F6. The cycle's own candidates cannot be gated yet

A `CandidateTransition` (`spec/adjustment_layer.schema.json`) carries six
risk axes in [0, 1] and five ordinal cost bands, and no telemetry state or
AllowedTotalRisk. The gate consumes a RiskWeight in percent, a telemetry
state and an AllowedTotalRisk. There is no mapping between the two
vocabularies, so `operator_admissibility` could not have been applied to the
candidates of runs 001 and 002 either. Closing this is a schema decision and
belongs to the ordinary coding route once the intended reading is chosen.
