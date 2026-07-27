# Held Hypotheses — Formulated Boundaries That Are Not Yet Candidates

**Unofficial draft. NON-CANONICAL. `HYPOTHESIS_HELD`. None of these is an AICE code or an
active candidate.**

See [the candidate surface README](./README.md) for the authority status of this directory and
the `HYPOTHESIS_HELD` lifecycle.

This file exists so that a formulated boundary can be preserved *without* being promoted to a
candidate dossier before it has an episode, a differential, or a decided relationship to an
existing class. Nothing here reserves a number, and nothing here satisfies any promotion
condition by existing.

```
FORMULATED         != EVIDENCE_BACKED
COHERENT_BOUNDARY  != DISTINCT_CLASS
LISTED_HERE        != CANDIDATE
ORDER_ON_THIS_PAGE != NUMBER_RESERVATION
```

Operator-indicated numbers are recorded as provenance only. Several of these overlap each other
by construction: promoting one may dissolve another, and that is the point of holding them.

---

## 1. No Fault Exists, Event Not Found

```
machine_name              FAULT_ABSENCE_EVENT_ABSENCE_CONFLATION
operator_indicated_number AICE-624   (provenance only)
status                    HYPOTHESIS_HELD
blocking_question         separate class, or the root mechanism of
                          ATTEMPT_CONSUMPTION_OUTCOME_EVIDENCE_GAP?
```

**Form.** A non-culpable outcome is implemented as an *absent* outcome. Because no actor
deserves a penalty, no event is persisted at all — so the episode's history loses the event
along with the blame.

```
observed implementation shape
    model_fault = false  →  score_penalty = 0  →  event suppressed
required shape
    model_fault = false  →  score_penalty = 0  →  event persisted = true

NOT_GUILTY != DID_NOT_EXIST
```

**Trigger predicates (draft).** `NONCULPABLE_OUTCOME` and
`FAULT_ABSENCE_IS_IMPLEMENTED_AS_EVENT_ABSENCE` and `THE_EVENT_IS_REQUIRED_FOR_SOME_DECISION`.

**Evidence status.** No independent positive instance. The one suggestive observation is
indirect: Atlas task `atlas-b4c5dd43` lost exactly the receipts for attempts that would have
carried no penalty. In the *current uncommitted* Atlas tree the corrective shape already appears
— `atlas/engine.py` writes one receipt per invocation carrying `model_fault` and
`score_penalty: 0` as separate fields — which supports the diagnosis but is a repair, not an
incident instance.

**Why held.** A single mechanism observed inside one episode of another candidate is not a
class. It earns its own record if a *second, structurally different* non-culpable outcome —
a free retry, a policy block, a user cancellation — also vanishes for the same "nobody to
penalize" reason.

---

## 2. Output Budget Exists, Deliverable Capacity Not Found

```
machine_name              TOTAL_OUTPUT_BUDGET_DELIVERABLE_CHANNEL_CAPACITY_CONFLATION
previous_machine_name     REQUESTED_EFFECTIVE_CAPACITY_CONFLATION
operator_indicated_number AICE-625   (provenance only)
status                    HYPOTHESIS_HELD
operator_grade            B+ → strengthened by direct measurement
```

**Revision note.** The original formulation was *requested budget vs. provider-granted budget* —
a provider-acceptance question. Direct probing falsified that framing: the provider **accepted**
the request and returned `finish_reason=length`. Nothing was clamped or refused. The real gap is
one level down, inside a budget the provider granted in full.

```
PROVIDER_ACCEPTED_THE_REQUEST != DELIVERABLE_CHANNEL_HAD_CAPACITY
```

**Form.** A total completion budget is configured. Several output channels draw on that one
budget. The required deliverable occupies only one of them. A channel the system never reads can
consume the entire budget, and the system nonetheless treats the total as the deliverable's
capacity.

```
TOTAL_COMPLETION_BUDGET_IS_CONFIGURED
AND MULTIPLE_OUTPUT_CHANNELS_SHARE_THAT_BUDGET
AND THE_REQUIRED_DELIVERABLE_USES_ONLY_ONE_CHANNEL
AND AN_UNCONSUMED_CHANNEL_CAN_EXHAUST_THE_BUDGET
AND THE_SYSTEM_TREATS_TOTAL_BUDGET_AS_DELIVERABLE_CAPACITY
→ TOTAL_OUTPUT_BUDGET_DELIVERABLE_CHANNEL_CAPACITY_CONFLATION
```

```
TOTAL COMPLETION CAPACITY  != DELIVERABLE CONTENT CAPACITY
REASONING TOKENS AVAILABLE != ANSWER TOKENS AVAILABLE
REQUESTED 8192 DOES NOT GUARANTEE ONE CONTENT TOKEN
```

**Measured positive exemplar** (session `91033b6c`, `scratchpad/probe/PROBE_HEAVY_8192.json`):

```
max_tokens requested   8192          finish_reason        length
reasoning deltas        158          reasoning chars      34 237
content deltas            0          content chars             0
parser reads                         delta.content only
```

**Differential with [`AICE-621`](../codes/AICE-621.md).** Now a causal relation, not just a
boundary:

```
625  the system MIS-COMPUTES the effective channel, deriving it from the total
     completion budget while ignoring competing consumption
        → effective content capacity collapses
        → 621 may activate

621  the task is admitted although the minimum deliverable cannot pass the
     effective channel
```

625 can be a **mechanism that produces** 621. The implication does not run backwards: a 621 needs
no auxiliary channel — a single-channel model with a small cap and a large deliverable is enough.

**Why still held.** Two gaps. First, the measurement proves the *mechanism* but not that any
system made a durable capacity-dependent decision on the conflated figure — that is the missing
incident instance. Second, the boundary against
`UNACCOUNTED_AUXILIARY_CHANNEL_OUTPUT_STARVATION`
is unresolved (that class is named but deliberately not defined anywhere yet): starvation is the
*runtime event*, this is the *system's belief about capacity*.
They may be one class seen from two ends, and promoting either without deciding would manufacture
two codes for one mechanism.

---

## 3. Output Ceiling Exists, Completion Window Not Found

```
machine_name              OUTPUT_CAPACITY_WALL_CLOCK_CONTRADICTION
operator_indicated_number NOT_FIXED — the operator explicitly declined to fix a number
status                    HYPOTHESIS_HELD
```

**Form.** Output capacity is authorized in tokens and simultaneously bounded in wall-clock time,
and no admissible route can emit the required output within the window. The tokens are
authorized but unreachable.

```
TOKENS_AUTHORIZED != TOKENS_REACHABLE_BEFORE_TIMEOUT
CAP_RAISED        != DELIVERY_ENABLED
```

**Evidence status.** Partial and durable. In Atlas task `atlas-b4c5dd43` (same objective digest
`7911e8936b73e326` as the AICE-621 exemplar), the glm-5.2 coder call recorded
`latency_ms: 300141` and the trace records
`TRANSPORT_FAILURE: TimeoutError: stream exceeded 300s wall clock`. A raised output ceiling and a
fixed 300 s window coexisted, and the call died on the window.

**Why held — and this is the operator's own ruling.** The episode proves *this* call exceeded
*this* window. It does not prove that no admissible route could deliver within it, which is the
load-bearing predicate. Promoting on the observed bytes would upgrade "one route timed out" to
"the window is structurally insufficient".

```
STATUS = HYPOTHESIS_HELD
NUMBER = NOT_RESERVED
```

---

## 4. Terminal State Exists, Causal Lineage Not Found

```
machine_name              TERMINAL_CAUSAL_LINEAGE_GAP
operator_indicated_number AICE-627   (provenance only)
status                    HYPOTHESIS_HELD
blocking_question         umbrella above ATTEMPT_CONSUMPTION_OUTCOME_EVIDENCE_GAP,
                          or a sibling of it?
```

**Form.** A terminal state is durable, and the causal event chain that produced it cannot be
reconstructed from durable evidence.

```
TERMINAL_STATE != AUDITABLE_TERMINAL_CAUSE
```

**Registry-architecture question, unresolved.** Two incompatible shapes:

```
A:  ATTEMPT_CONSUMPTION_OUTCOME_EVIDENCE_GAP is the class;
    lost terminal lineage is one of its material consequences
B:  TERMINAL_CAUSAL_LINEAGE_GAP is an umbrella;
    the attempt-consumption gap is a specialized subtype
```

**Why held.** Shape A is the cheaper hypothesis and is what the attempt-consumption candidate
currently assumes. This record earns independence only from an episode where terminal lineage is
lost **without** attempt consumption being the missing link — otherwise a canonical umbrella
would be built from a single specialized instance.

---

## 5. Productionization Exists, Product Fit Not Found

```
machine_name              PREMATURE_PRODUCTIONIZATION_WITHOUT_PRODUCT_FIT
operator_indicated_number AICE-629   (provenance only)
status                    HYPOTHESIS_HELD
operator_grade            B
```

**Form.** A core product gate has not been passed and material product defects remain, yet
certification, hardening, or productionization work begins and is treated as the next stage —
while doing nothing to repair the failed gate.

```
PROCESS_MATURITY != PRODUCT_MATURITY
NEXT_STAGE_BEGAN != PREVIOUS_STAGE_CLOSED
```

**Prior-art collision — the strongest reason this is held.** This is close to two things that
already exist:

| Existing | Relationship |
|---|---|
| Atlas Driver `PATTERN 1: PREMATURE_VALIDATION_DIMENSION_ESCALATION` | Nearly the same trigger: primary fitness not established, a new validation dimension is opened, and it is not the dominant unresolved risk. That pattern already carries a driver action (`DEFER_NEW_VALIDATION_DIMENSION`) and an exception list. A new AICE code must say what it adds beyond an existing enforced driver pattern |
| [`AICE-601`](../codes/AICE-601.md) Minimum Sufficient Mechanism Bypass | A minimum sufficient path exists yet a larger mechanism is made prerequisite without a unique-necessity witness. Productionization made prerequisite to an unpassed product gate is arguably an instance |
| [`AICE-617`](../codes/AICE-617.md) Work Exists, Result Not Found | Process activity accumulating while the product outcome stays absent — the same failure viewed from the outcome side |

**Why held.** Beyond the collision, the operator's own condition is unmet: it must be shown that
certification was actually *accepted as the next stage* and *displaced* the product decision,
rather than merely being mentioned.

---

## 6. Repair Exists, Observability Regressed

```
machine_name              CORRECTIVE_CHANGE_EVIDENCE_REGRESSION
operator_indicated_number none — deliberately not numbered
status                    HYPOTHESIS_HELD
```

**Form.** A defect is genuinely corrected, and the same repair degrades a *different* evidence
dimension. Validation checks only the corrected defect, so the repair is accepted as complete
while the system's overall evidence position is worse than before.

```
DEFECT_A_IS_CORRECTED
AND THE_SAME_REPAIR_DEGRADES_EVIDENCE_DIMENSION_B
AND VALIDATION_CHECKS_ONLY_DEFECT_A
AND THE_REPAIR_IS_ACCEPTED_AS_COMPLETE
→ CORRECTIVE_CHANGE_EVIDENCE_REGRESSION

LOCAL_REPAIR_PASS != SYSTEM_EVIDENCE_NONREGRESSION
```

**Candidate exemplar (one, unverified).** The Atlas outcome-accounting repair:

```
false model blame removed      improved
finish_reason classification   improved
durable outcome accounting     regressed
```

**Why held, deliberately unnumbered.** One exemplar, and that exemplar is the same episode
family that produced two other records on this page — which is exactly the condition under which
a class looks more general than its evidence. It is also the most likely of these six to be a
real, portable class, so it is recorded in full rather than as a note.

---

## Cross-cutting note

Records 1, 4 and 6 all draw on the same Atlas episode family, and record 4 may absorb record 1.
Promoting more than one of them from that single family would manufacture apparent independence
between classes that share an origin. Whichever is promoted first should state explicitly which
of the others it is understood to subsume.
