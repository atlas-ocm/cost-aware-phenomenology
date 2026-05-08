# Worked Case: Client Asking for Free Edits

This document walks through a complete CAP analysis from a single sentence of natural-language input to a fully populated COM-Log v1.1 block. It shows how each field is determined, what gates fire, and why the recommended operator is what it is rather than something else.

---

## Input

> Client called again about the old project, asks for free edits. I spent half an hour explaining why it's impossible, ended up with a headache, but the issue is still hanging.

This is a typical CAP input: short, narrative, emotionally loaded, no explicit structure. The grammar's job is to convert it into a COM-Log block.

---

## Step 1 — Drama Trigger and Node Extraction

The input contains intensity signals: "called *again*," "still hanging," and the somatic marker "headache." Per Parser Rule 10.1, intensity signals are a parsing trigger to **increase analytical precision**, not a reason to increase empathic resonance.

Per Rule 10.2, extractable nodes are identified by:

| Signal | Candidate Node |
|---|---|
| "the old project" | a closed-then-reopened project node |
| "asks for free edits" | a scope/boundary node |
| "called again" → recurrence | indicates Looping or Persistent Fault Candidate |
| "I spent half an hour explaining" | a process node (the conversation as effort sink) |
| "headache" | a somatic telemetry signal |
| "still hanging" | the situation as a whole node remains unclosed |

Three primary nodes emerge. The conversation effort and the headache become telemetry signals attached to those nodes rather than nodes in their own right.

---

## Step 2 — Domain and Subdomain Assignment

Per Rule 11.2, every node must be assigned a domain. The most natural fit:

- **Node 1**: Domain = Business, Subdomain = Client relations
- **Node 2**: Domain = Business, Subdomain = Project
- **Node 3**: Domain = Time, Subdomain = Schedule (the recurring conversation as a time leak)

Nodes 1 and 2 are tightly coupled (they share their SplitPoint). Node 3 is partly downstream of Node 1.

---

## Step 3 — Current State Assignment

Per Rule 10.3, behavioral descriptions map to state syntax:

- "called again" + "issue still hanging" + at least 3 prior cycles inferred → **Looping**
- "headache" + "still hanging" → leak signal present → **Leaking** (L3 — Fast)
- The conversation that consumed 30 minutes without producing closure → another iteration of the same loop, not a new node

Per Rule 11.4, every state assignment must have at least one telemetry signal:

| State | Telemetry Ground |
|---|---|
| Looping (Node 1) | "called again" — recurrence pattern |
| Leaking L3 (Node 1) | "headache" — somatic load; "30 min" — time burn per cycle |
| Pending (Node 2) | issue unresolved after multiple cycles |

All states have telemetry support. No HYPOTHESIS marker needed.

---

## Step 4 — Persistent Fault Candidate Check

Has the node been Active → Leaking two or more times without reaching Resolved? Yes — "called *again*" implies at least one prior cycle, and the current call is at least a second iteration. Treating this as conservative, the node is at the boundary of PFC. With any third callback, PFC fires automatically.

PFC status triggers (per Section 7):

1. Mandatory ReverseTrace before operator selection
2. Leak level upgrade by one tier (L3 → L4 candidate)
3. Risk weight increase by 15 percentage points
4. Operator selection review

We proceed with ReverseTrace.

---

## Step 5 — ReverseTrace (Reverse-First Parsing)

Per §A.13, parsing is reverse-first. Before selecting any operator, we trace backward from the current state:

```text
← Current: Looping, Leaking L3 (callback now, headache, 30 min spent)
← Prior callback(s) (each producing the same Looping behavior)
← Initial undocumented "I'll help out" stance after delivery
← Project closure without explicit post-delivery scope
← Project delivery (in original scope, presumably paid)
← Original engagement (Active — agreed scope)
```

The trace reaches a non-damaged state at "Original engagement." Trace is complete.

---

## Step 6 — LikelySplitPoint

The earliest event where a different operator would have produced a different outcome:

> **Initial closure of the project without an explicit written post-delivery scope.**

Without a written boundary at closure, every callback became a legitimate request the agent had to talk down. The conversational effort of each callback is downstream of this missing boundary.

Note: the SplitPoint is not "I should have said no the first time." That is a moralizing reading. The SplitPoint is the **structural** point at which a different operator (Boundary at closure) would have changed the route. The framework attributes the damage to the missing operator, not to a personal failing.

---

## Step 7 — Operator Selection

Per Rule 10.4, operator priority:

1. Fixation if any node is at L3/L4 Leaking — applies here (L3, possibly upgrading to L4)
2. Boundary if scope is expanding beyond agreement — applies here (free edits beyond the original agreement)
3. Pause if insufficient information — not the case here; signal is sufficient
4. All others by route analysis

Two operators emerge as primary:

- **Fixation** on Node 2 (project) — stop further work / engagement until scope is defined
- **Boundary** on Node 1 (client relations) — define written post-delivery scope

Per the Antifragility Rule (§A.16), Boundary should precede Break. If Boundary fails (client rejects the policy), the route proceeds to Break (Closure or Drop), which was always available. If Boundary succeeds, Break may be unnecessary.

Sequence: **Fixation → Boundary → (Closure if accepted | Break if rejected)**.

---

## Step 8 — Risk Weights

Per the Risk Scale (§A.5):

| Operator | RiskWeight | Zone |
|---|---|---|
| Fixation (stop further work) | 25% | Conservation |
| Boundary (written post-delivery policy) | 35% | Conservation/Nominal boundary |
| Conditional Closure | 30% | Conservation |
| Conditional Break | 50% | Nominal |

Cycle TotalRisk for the immediate operators (Fixation + Boundary): **60%**.

---

## Step 9 — Telemetry State

Per §A.7, the gate state is determined by signal quality + observer budget:

| Factor | Reading |
|---|---|
| Signals present | Yes (recurrence, somatic, time burn) |
| Signal contradictions | None major; client's actual contract terms are partially unclear |
| Observer budget | Partially depleted (somatic load, frustration loading next cycle) |

Verdict: **Loaded**.

Per §A.8 risk throttling: Loaded permits maximum RiskWeight 60%. Boundary at 35% and Fixation at 25% both pass.

---

## Step 10 — Budget Gate

```text
ObserverUsableBudget: ~70% (partial depletion from emotional load + headache)
RiskToleranceFactor: ~0.85 (no acute crisis, telemetry is Loaded not Overheating)
AllowedTotalRisk: 70% × 0.85 ≈ 60%

Cycle TotalRisk: 60%

BudgetGate: PASS (just within budget; conservative)
```

---

## Step 11 — Repair Vector

Ordered sequence:

```text
1. Fixation: Stop responding to free-edits requests in the current cycle.
   Stop participating in the conversation about why edits are impossible.
2. Boundary: Send a written one-paragraph policy to the client:
   "Post-delivery edits are billable at [rate]. The original delivery is
   considered closed."
3. Pause on Node 1 until next contact attempt.
4a. If client accepts policy: Closure (formal write-up of the policy
    becomes the new contract floor; future edits run as paid scope).
4b. If client refuses or escalates: Break (drop the client; archive the
    project as Dropped; document for future reference).
```

---

## Step 12 — Guard Conditions

Per §A.10, the RepairVector requires Guard conditions:

```text
Guard:
- Agent is not in a financial state requiring this client's future work
  in the next 30 days (if this fails, recalculate — Boundary risk increases
  because agent cannot afford to lose the relationship).
- Original delivery is not legally disputed (if it is, escalate to Legal
  domain before applying any operator here).
- Written policy can be sent without provoking a hostile public response
  (e.g., social media retaliation) — if this fails, downgrade to a verbal
  boundary first.
```

If any Guard condition becomes false, the Repair Vector must be recalculated.

---

## The Full COM-Log v1.1 Output

```text
[COM-Log v1.1: Client Free-Edits Pattern]

--- Node 1 ---
Domain: Business
Subdomain: Client relations
Node: Free-edits boundary with this client
CurrentState: Looping
LeakLevel: L3 — Fast (somatic load — headache; ~30 min/cycle time burn;
                     2-3 prior callback cycles inferred)

Outcome: Repeated callbacks producing no resolution. Time and somatic
  resources depleted. The original project remains formally closed in the
  agent's view but operationally re-opened in the client's view because
  no explicit closure boundary was set.

ReverseTrace:
  ← Current: Looping, Leaking L3 (callback now, headache, 30 min spent)
  ← Prior callback(s)
  ← Initial undocumented "I'll help out" stance post-delivery
  ← Project closure without explicit written post-delivery scope
  ← Project delivery (in original scope)
  ← Original engagement (Active — agreed scope)

LikelySplitPoint: Initial closure without written post-delivery scope.
  Without a written boundary, every callback was a legitimate request
  the agent had to talk down. The conversational effort of each callback
  is downstream of this missing operator.

RecommendedOperator: Boundary
RiskWeight: 35%
AllowedTotalRisk: 60% vs ObserverUsableBudget (≈70%) × RiskToleranceFactor (0.85) = 60%
TelemetryState: Loaded
BudgetGate: PASS

TargetStatus: Closed (with documented post-delivery policy as new
                      contract floor)

RepairVector:
  1. Fixation: Stop responding to free-edits requests this cycle.
  2. Boundary: Send written one-paragraph policy to client
     ("Post-delivery edits = paid scope at [rate]; original delivery closed").
  3. Pause until next contact attempt.
  4a. If client accepts: Closure (policy becomes the contract floor).
  4b. If client refuses or escalates: Break → Dropped.

Guard:
  - Agent is not in a financial state requiring this client's future work
    in the next 30 days.
  - Original delivery is not legally disputed.
  - Written policy can be sent without hostile public response.

Notes: Persistent Fault Candidate watch — if a third callback occurs
  before Boundary is sent, PFC fires automatically and the leak level
  upgrades to L4 (Critical), forcing Fixation as the immediate next move
  before any other operator.

--- Node 2 ---
Domain: Business
Subdomain: Project
Node: The original project as an open ticket in client's view
CurrentState: Looping (sharing SplitPoint with Node 1)
RecommendedOperator: Fixation (immediately, before Boundary on Node 1)
RiskWeight: 25%
TargetStatus: Closed (after Boundary on Node 1 succeeds)
                 OR Dropped (if Boundary fails)

--- Node 3 ---
Domain: Time
Subdomain: Schedule
Node: Recurring conversational time burn from this client
CurrentState: Leaking L3 (downstream of Node 1)
RecommendedOperator: derived from Node 1 — once Boundary is in place,
  this leak closes automatically
RiskWeight: (no separate operator needed)

[Summary v1.1]
OpenNodes: 3
CriticalLeaks: 1 (Node 1, L3 → L4 watch)
PersistentFaultCandidate: Node 1 (boundary case; PFC on next callback)
PriorityOperator: Fixation (Node 2) → Boundary (Node 1) — in this sequence
TelemetryState: Loaded
BudgetGate: PASS (60% vs 60% AllowedTotalRisk — at ceiling)
TotalRisk: 60% (Fixation 25% + Boundary 35%)
```

---

## What This Walk-Through Demonstrates

Several CAP discipline points are visible in this analysis:

1. **Reverse-first parsing**: The ReverseTrace is run before any operator is selected. The SplitPoint informs the operator choice.

2. **Anti-drama**: The headache is treated as a telemetry signal, not as a reason to switch into therapeutic mode. The framework's response to somatic load is to upgrade the leak level, not to validate the agent's frustration.

3. **Anti-moralization**: The SplitPoint is a missing operator (Boundary), not a personal failing. The framework attributes damage to structural absence, not to the agent's character.

4. **Antifragility**: Boundary precedes Break. If Boundary succeeds, Break is unnecessary; if it fails, Break remains available. Nothing was lost by trying Boundary first.

5. **Budget discipline**: TotalRisk (60%) is exactly at the AllowedTotalRisk ceiling (60%). No third operator can be added this cycle. The framework refuses to overload.

6. **Telemetry gating**: Loaded telemetry caps the maximum operator at 60%. Inversion (which might tempt the agent — "go nuclear, dump the client publicly") would be 80%+ and is blocked at the gate, not by a soft warning.

7. **Guard conditions**: The Repair Vector is conditional on three Guards. If any Guard fails, the recommendation must be recalculated — the framework does not pretend its plan is unconditional.

This is what CAP looks like when it operates correctly. Several other adjacent frameworks could produce useful narrative analysis of the same situation. None of them would produce the sequenced, budgeted, gated, structurally-attributed output above without the operator grammar, telemetry gate, and risk throttle.
