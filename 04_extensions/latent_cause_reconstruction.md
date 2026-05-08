# Latent Cause Reconstruction (A-Reconstruction)

Latent Cause Reconstruction (also: A-Reconstruction) is a **diagnostic extension** of CAP that runs when the observed rupture B is given but the underlying cause A is not yet known. Where the Looking-Glass layer assumes the user can describe the upstream history, A-Reconstruction is for the case where the user can only describe the visible damage.

Status: `validated / 15/15 deterministic / 28/28 live LLM`.

---

## Purpose

A-Reconstruction is useful when:

- the observer can describe the visible rupture (B) but does not know what caused it
- the observer offers a candidate cause but the candidate is weak (often a moralizing or self-blaming explanation)
- the visible trigger looks too small to explain the damage, suggesting an upstream bridge

The pipeline:

```text
observed rupture B
+ prior history H
+ resource traces R
+ behavioral traces T
+ known causal patterns K
-> latent A candidates
-> A -> B bridge plausibility
-> counterfactual removal
-> ranked cause-repair pairs A_i -> C_i
```

---

## The Anti-Banality Rule

The single most important rule:

> **C is computed from A + B, not from B alone.**

Closing the visible symptom without neutralizing the latent imbalance is **only symptom repair**. An emergency invoice paid while the contingency-buffer leak continues is not stable repair — it is a temporary symptom-clearing that will reproduce the rupture as soon as the next shock arrives.

The pattern:

```text
Weak repair:
B = budget overrun
C = pay the invoice

Cause-level repair:
A + B -> C
where C is the minimum stable state in which A can no longer reproduce B
```

The minimum stable state is the criterion. Anything less is symptom repair, not structural repair.

---

## The B-Inference Pipeline

```text
1. Input:
   observed rupture B

2. Extract:
   damage_vector
   resource_delta
   anchor_pressure
   trigger_event
   reserve_state
   leakage_signals
   recurrence_signals
   language_markers

3. Generate:
   latent A candidates

4. Test each A:
   A -> B bridge plausibility
   counterfactual removal (would B weaken if A were removed?)
   recurrence match (has the pattern appeared before?)
   compression score (how many observed facts does A explain?)

5. Rank:
   probable A distribution

6. Compute:
   C repair states for top A candidates

7. Output:
   ranked cause-repair pairs
   A1 -> C1
   A2 -> C2
   A3 -> C3
```

The output is **not** "the reason is exactly A." The output is "probable A distribution with evidence, counterfactual tests, and repair state per A."

---

## Trigger Is Not Cause

A core distinction:

```text
A = latent imbalance
T = trigger event
B = visible rupture
C = repair state
```

The visible event T can be the trigger without being the cause A. Examples:

**Engineering incident case:**
```text
A = contingency-buffer depletion + unbounded prototype spend
T = emergency database recovery invoice
B = project budget overrun
C = invoice contained + contingency rebuilt + prototype spending gate repaired
```

**Relationship case:**
```text
A = silent debt + unilateral repair labor
T = small fight / cold reply
B = breakup pressure or relational distance
C = mutuality restored, compensation made, or line closed without leakage
```

**Health case:**
```text
A = chronic overload + ignored recovery cost
T = minor illness
B = extended setback / function loss
C = load reduced + recovery margin rebuilt + symptom contained
```

Treating T as A is the most common diagnostic error. A-Reconstruction's purpose is to surface the difference.

---

## Cause Scoring

Multiple A candidates are generated and scored:

```text
CauseScore(A) =
  + trace_match           (does A match the remaining traces?)
  + forward_path_plausibility   (can A produce B through a plausible bridge?)
  + counterfactual_strength     (would B weaken if A were removed?)
  + recurrence_support          (has the same pattern appeared before?)
  + compression_power           (how many observed facts does A explain?)
  - assumption_cost             (how much must be invented?)
  - moralizing_penalty          (does A smuggle blame / punishment story?)
  - fantasy_penalty             (does A require mystical / arbitrary assumptions?)
```

The candidate that explains more traces with less invention scores higher. Moralizing and fantasy candidates are penalized because they have strong narrative pull but produce repair plans that do not actually close the leak.

---

## Repair Sequencing

Repair must be ordered cause-first:

```text
1. Stop or neutralize active A
2. Contain visible B
3. Rebuild the depleted reserve / channel
4. Install the boundary that prevents recurrence
```

For budget / resource cases this means:

```text
First stop optional work that is consuming the base contingency buffer,
then contain the visible invoice / overrun and rebuild the reserve.
```

This is not a ban on optional work or exploration. It is a routing rule:

```text
Clean-margin exploration may remain possible.
Optional work funded from the base / reserve / incident floor is the active leakage.
```

---

## Domain Generality

The same pipeline applies across domains, with domain-specific traces and anchors:

| Domain | A often looks like | C often requires |
|---|---|---|
| Money / Material | optional spend from base reserve, hidden subsidy, status spending | stop leakage + rebuild reserve + boundary rule |
| Relational | silent debt, unilateral repair labor, false repair | surface debt + rebuild mutuality OR compensate / close |
| Health / Body | chronic overload, ignored recovery cost | reduce load + restore recovery margin |
| Work | scope creep, invisible labor, deferred technical debt | trim scope + restore ownership boundaries |
| Self-model | self-verification pressure, identity debt | separate event from self-proof + reduce verification pressure |
| Public / Status | recognition hunger, performance spending | separate truth from social force + stop status overpayment |
| Household | invisible labor, one-sided ownership | make load visible + assign ownership + restore cadence |
| Legal / Institutional | untracked obligation, missing proof | recover evidence + route through formal constraints |
| Dependent care | care duty colliding with depleted reserve | protect dependent + stop unrelated leakage + restore care reserve |
| Attention / Time | open vector subscription, monitoring loop | close or park open loops + reduce monitoring |
| Creative project | scope inflation, identity overload, perfection debt | cut scope to carryable + separate craft from self-proof |

The domain changes what counts as budget, debt, reserve, repair, boundary. The skeleton stays constant.

---

## Validation Status

```text
Deterministic baseline:           15/15
comet                             15/15 verdict and primary-reading alignment
silicon-maid-7b                   15/15 verdict and primary-reading alignment
identity guard enforced:          true (both models)

Live LLM all-real batch:          28/28 PASS on comet_12b_v.7-i1 and silicon-maid-7b-imatrix
```

14 real-case rounds were validated, covering: relationship, gift-credit, late reply / old vector, false repair, work / body margin, self-model identity, household invisible labor, trigger vs cause guard, underdetermined A, moralizing fantasy guard, emotional trigger overweight, health recovery margin, and work scope creep.

---

## Authoritative Artifacts

```text
Patch/latent_cause_reconstruction_operator_guide_ru.md
Patch/latent_cause_reconstruction_real_case_template_ru.md
Patch/latent_cause_reconstruction_worked_examples_ru.md
Patch/latent_cause_reconstruction_prompt_contract_ru.md
Patch/latent_cause_reconstruction_live_answer_quality_gate_ru.md
Patch/latent_cause_reconstruction_real_case_rounds_index.md
Patch/latent_cause_reconstruction_live_llm_all_real_batch_report.md
```

---

## Compression

```text
A-Reconstruction is the inverse-causal half of the routing chain.

Visible rupture B is given.
Latent cause A is reconstructed and ranked.
Repair C is computed from A + B, not from B alone.
The minimum stable state is the one in which A can no longer reproduce B.

Trigger is not cause.
Symptom-only closure is not repair.
```
