# COM Grammar

COM (Chain Operator Module) is the typed grammar that translates ordinary life narrative into a technical log of routes, statuses, and operators. It is the parsing layer of CAP — the layer that converts "I'm stuck and I don't know what to do" into a structured COM-Log block with explicit operator recommendations.

This document is a working overview. The full specification (1068 lines, including v1.0 base, v1.1 addendum with Looking-Glass Mode, Telemetry Gate, Risk Throttling, and the philosophical foundations) lives in `Patch/com_grammar_spec_v1.md`.

---

## Purpose

COM is a grammar of events, nodes, and operators. Its purpose:

- **Objectify drama into structure** — replace narrative intensity with state syntax
- **See open and leaking nodes** — surface what is unfinished, what is bleeding, what is unaddressed
- **Recommend operators, not advice** — produce structured recommendations with risk weights, not suggestions
- **Produce a `[COM-Log]` block** — the canonical output format

COM does not interpret emotions. It maps events to node states and operator sequences. The output is always a technical log, not a therapeutic response.

---

## Core Form

```text
[Domain] -> [Node] -> [Status] -> [Operator (RiskWeight)] -> [TargetStatus]
```

Extended form:

```text
[Domain] -> [Subdomain] -> [Node] -> [CurrentState] -> [Leak/Risk]
        -> [RecommendedOperator (RiskWeight)] -> [TargetStatus]
```

Every situation is a set of such chains. Some chains are complete (operator applied, target status reached). Some are broken (operator missing, state stalled). COM identifies which chains are broken and what operator is needed.

---

## The 13 Operators

English names with original Russian terms in parentheses for searchability:

| Operator | Description | Typical Risk Range |
|---|---|---|
| **Fixation** (Фиксация) | Lock the current state. Stop the leak. Stabilize the node before any forward movement. | 10–25% |
| **Inversion** (Инверсия) | Reverse the direction of the current route. What was pursued becomes what is avoided. | 60–90% |
| **Break** (Разрыв) | Terminate a connection, contract, expectation, or route. Hard stop, not pause. | 50–80% |
| **Hold / Pause** (Пауза / Hold) | Suspend action on the node without terminating it. Preserves optionality. | 10–20% |
| **Pump / Reinforcement** (Усиление / Pump) | Increase resource input to the node. Accelerate movement toward target status. | 40–70% |
| **Transfer** (Перенос) | Move the node to a different domain, subdomain, or context. | 35–60% |
| **Closure** (Закрытие) | Formally close the node with documentation. Orderly completion. | 30–50% |
| **Boundary** (Граница) | Draw an explicit perimeter around the node. Define inside / outside. | 25–45% |
| **Cleanup** (Очистка) | Remove accumulated noise, legacy state, residual data from the node. | 20–35% |
| **Reframe** (Переименование) | Change the node's label without changing its content. | 15–30% |
| **Compression** (Компрессия) | Consolidate multiple related nodes into a single node. | 20–35% |
| **Separation** (Разводка) | Split one node into multiple routes. | 25–40% |
| **Return** (Возврат) | Return the node to a prior state. Undo a recent operator that produced worse outcomes. | 30–55% |

Risk ranges are calibration defaults. Specific operators in specific contexts can carry higher or lower weights.

For the full operator alphabet in machine-readable form, see [`../spec/operator_alphabet.json`](../spec/operator_alphabet.json).

---

## The 12 Domains

| # | Domain (English) | Domain (Russian) | Subdomain Examples |
|---|---|---|---|
| 1 | Finance | Финансы | Income, Debt, Investment, Reserve, Expenses |
| 2 | Work / Career | Работа / Карьера | Employment, Freelance, Projects, Identity |
| 3 | Business | Бизнес | Client relations, Product, Operations, Partnerships |
| 4 | Relationships | Отношения | Romantic, Family, Friendship, Acquaintance |
| 5 | Health | Здоровье | Physical, Mental, Energy, Medical |
| 6 | Housing | Жильё | Primary, Secondary, Rental, Relocation |
| 7 | Education | Образование | Formal, Self-education, Skill development |
| 8 | Legal | Правовое поле | Contracts, Disputes, Registration, Compliance |
| 9 | Reputation | Репутация | Professional, Social, Digital |
| 10 | Time | Время | Schedule, Deadlines, Allocation |
| 11 | Identity | Идентичность | Self-model, Values, Role, Transitions |
| 12 | Environment | Среда | Social, Physical, Information |

Every node in CAP must be assigned to a domain. A node without a domain is not a CAP node — it is an unprocessed narrative fragment.

---

## The 16 Statuses

| Status | Description |
|---|---|
| **Open** | Node identified, no operator applied yet |
| **Active** | Operator applied, process running |
| **Leaking** | Node losing resources without producing target output |
| **Frozen** | Node stalled — no movement in either direction |
| **Looping** | Node repeating the same cycle without progressing |
| **Escalating** | Node moving toward higher intensity without resolution |
| **Split** | Node has divided into two or more sub-routes requiring separate operators |
| **Misclassified** | Node was assigned to wrong domain or given wrong state |
| **Overloaded** | Node receiving more input than it can process |
| **Bound** | Node cannot move due to external constraint |
| **Pending** | Node waiting for external signal or condition |
| **Closed** | Node formally closed; route segment complete |
| **Resolved** | Node reached target status; issue addressed |
| **Fixed** | Node state corrected after Misclassified diagnosis |
| **Dropped** | Node deliberately removed from active tracking |
| **Reopened** | Previously Closed/Resolved node reactivated due to new signal |

### Leak Levels

When a node is in Leaking state, assign a leak level:

| Level | Description |
|---|---|
| **L1 — Slow** | Detectable but not immediately threatening; can be scheduled |
| **L2 — Moderate** | Affecting route progress; requires operator within current cycle |
| **L3 — Fast** | Destabilizing adjacent nodes; immediate operator needed |
| **L4 — Critical** | Threatening route integrity; Fixation required before anything else |

---

## COM-Log v1.1 Format

The full COM-Log block (v1.1):

```text
[COM-Log v1.1]
Domain: [domain name]
Subdomain: [subdomain name, if applicable]
Node: [node label]
CurrentState: [state from the 16 statuses]
LeakLevel: [L1/L2/L3/L4, if Leaking]
Outcome: [observable result already produced by current state]
ReverseTrace: [backward causal chain from current state to SplitPoint]
LikelySplitPoint: [earliest point a different operator would have diverged the route]
RecommendedOperator: [operator from the 13]
RiskWeight: [XX%]
AllowedTotalRisk: [sum vs. ObserverUsableBudget]
TelemetryState: [Clean / Loaded / Overheating / Breach]
BudgetGate: [PASS / HOLD — reason if HOLD]
TargetStatus: [target state]
RepairVector: [sequence of operators required to reach target]
Guard: [conditions under which RepairVector holds]
Notes: [qualifications, missing info, grammar extension candidates]
```

The machine-readable schema for this format is in [`../spec/com_log_schema.json`](../spec/com_log_schema.json).

---

## Parsing Example

**Input narrative**:

> Client called again about the old project, asks for free edits. I spent half an hour explaining why it's impossible, ended up with a headache, but the issue is still hanging.

**COM-Log v1.1 output (compressed)**:

```text
--- Node 1 ---
Domain: Business
Subdomain: Client relations
Node: Free-edits boundary with this client
CurrentState: Looping (3rd iteration of the same conversation)
LeakLevel: L3 (somatic load — headache; time burn ~30 min/cycle)
ReverseTrace: ← Looping ← prior conversations ← initial undocumented
              "I'll help out" stance ← project closure without
              explicit post-delivery scope
LikelySplitPoint: Initial closure without written post-delivery scope.
                  Without a written boundary, every callback was a
                  legitimate request the agent had to talk down.
RecommendedOperator: Boundary (35%)
TelemetryState: Loaded (3 cycles confirmed; somatic markers present)
BudgetGate: PASS (Boundary fits Loaded ceiling at 60%)
TargetStatus: Closed (with documented post-delivery policy)
RepairVector:
  1. Boundary: send written policy ("post-delivery edits = paid scope")
  2. Pause on this node until next contact attempt
  3. Closure on next callback (cite policy)
Guard: Agent is not in financial state requiring this client's future work
```

A complete walk-through of this example is in [`../examples/worked_case_client_free_edits.md`](../examples/worked_case_client_free_edits.md).

---

## Reverse-First Parsing

In COM v1.1, parsing is **reverse-first**:

1. Read the input narrative
2. Identify nodes
3. Assign current states
4. **Before selecting any operator: run ReverseTrace on all Leaking or Looping nodes**
5. Identify LikelySplitPoint for each traced node
6. Then select operators, informed by causal history
7. Assign RiskWeights
8. Check TelemetryState
9. Calculate TotalRisk vs. ObserverUsableBudget
10. Apply BudgetGate (PASS or HOLD)
11. Produce RepairVector with Guard conditions

Skipping step 4 (ReverseTrace) and going directly to operator selection is a v1.0-mode parse. It is not incorrect, but it misses the causal structure that v1.1 requires for Leaking and Persistent Fault nodes.

---

## Persistent Fault Candidate

A node that cycles through the sequence **Active → Leaking → Active → Leaking** two or more times without reaching Resolved or Closed is flagged as a **Persistent Fault Candidate**.

PFC status triggers:

1. Mandatory ReverseTrace to identify the originating SplitPoint
2. Upgrade of leak level by one tier
3. Risk weight increase by 15 percentage points
4. Operator selection review — the current operator is likely wrong

A PFC cannot be closed without completing ReverseTrace and DamageAttribution.

---

## Quality Criteria for COM Analysis

A COM analysis is high quality if and only if it:

1. **Reduces drama**: technical language replaces narrative language
2. **Increases clarity**: situation more precisely described after parsing than before
3. **Shows leak**: if there is a leak (L1–L4), it is identified and quantified by node
4. **Identifies missing operator**: if no operator is currently applied to a critical node, this is flagged explicitly
5. **Specifies next physical step**: at least one physically executable action the agent can take in the next 24 hours

An output that meets all five is a complete COM analysis. Fewer than three is incomplete and should be extended before delivery.

---

## Compression

```text
COM translates history -> route log.
It converts narrative -> nodes.
It converts feelings -> state signals.
It converts "I don't know what to do" -> operator recommendations
                                          with target statuses.
```

For validation status see [`../03_validation/com_grammar.md`](../03_validation/com_grammar.md).
