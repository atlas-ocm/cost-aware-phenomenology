# CAP Glossary

A reference for the terms used throughout this framework. Format per term: short definition, technical meaning, what not to confuse it with, brief example.

---

### Transition Cost
**Short:** What it costs to move from one experiential state to another.

**Technical:** Combined cost across emotional, cognitive, bodily, social, rollback-risk, and cross-domain-drain dimensions. Operates as a first-class property of state, alongside meaning, embodiment, and prediction. See [`02_subsystems/transition_cost.md`](./02_subsystems/transition_cost.md).

**Not to be confused with:** Free energy (Friston) — free energy is one cost; transition cost in CAP is multidimensional and explicitly typed. Also not the same as "computational cost" — transition cost is phenomenological.

**Example:** Paying an emergency incident invoice has a direct cost. Paying it while the contingency buffer is still being consumed by non-critical work has a higher *transition* cost — the budget required to contain the invoice and repair the buffer policy.

---

### Observer Budget (ObserverUsableBudget)
**Short:** The current usable capacity of the observer.

**Technical:** Bounds total active risk: `TotalRisk(active chains) ≤ ObserverUsableBudget`. Combined with `RiskToleranceFactor` (conservative=0.4, nominal=0.7, expansion=1.0), yields `AllowedTotalRisk`.

**Not to be confused with:** Total available time or money — observer budget is the cognitive/affective capacity to execute operators safely.

**Example:** After a bad night's sleep with low energy, ObserverUsableBudget is reduced. Operators that would normally be admissible may now be inadmissible.

---

### Telemetry Gating
**Short:** The real-time safety layer that decides which operators can fire.

**Technical:** Four states (`Clean`, `Loaded`, `Overheating`, `Breach`) classified from telemetry signals (energy, headache, retrieval pressure, body contraction, sleep deficit, etc.). State determines which operators are admissible and what the AllowedTotalRisk should be downgraded to.

**Not to be confused with:** Generic monitoring or logging — telemetry here directly gates operator selection.

**Example:** Even if [Inversion 80%] is the "right" operator semantically, Telemetry=Overheating blocks it and Risk Throttling downgrades to a lower-cost sequence.

---

### Operator Admissibility
**Short:** Whether a given operator can fire safely given current Budget + Telemetry.

**Technical:** Derived layer. An operator's RiskWeight must fit within AllowedTotalRisk and the operator must not be forbidden by current Telemetry State. See [`02_subsystems/operator_admissibility.md`](./02_subsystems/operator_admissibility.md).

**Not to be confused with:** Operator correctness — an operator can be the "right" choice in principle but inadmissible right now.

**Example:** [Break] may be the structurally correct operator for a leaking node, but if AllowedTotalRisk is 30% and [Break] requires 60%, it is inadmissible until budget recovers.

---

### Risk Throttling
**Short:** Automatic downgrade when telemetry worsens.

**Technical:** When Telemetry transitions from Clean → Loaded → Overheating → Breach, AllowedTotalRisk is reduced and active chains are downgraded or held. Triggers Budget Recovery Protocol on Breach.

**Not to be confused with:** Refusing to act — risk throttling produces an alternative lower-cost sequence, not silence.

---

### COM Grammar (Chain Operator Module)
**Short:** The typed grammar that parses life situations into structured operator chains.

**Technical:** 13 operators × 12 domains × 16 statuses. Operates at Layer C of the CAP architecture. Full spec: [`02_subsystems/com_grammar.md`](./02_subsystems/com_grammar.md).

**Not to be confused with:** Computer Object Model (Microsoft COM) — completely different. Also not a divination/oracle system.

---

### COM-Log
**Short:** The canonical structured output of a CAP analysis.

**Technical:** A document with Domain, Subdomain, Node, CurrentStatus, Operator (RiskWeight), TelemetryState, BudgetGate, TargetStatus, NextPhysicalStep. Schema: [`spec/com_log_schema.json`](./spec/com_log_schema.json).

**Not to be confused with:** A diary entry or therapy note — COM-Log requires a concrete next physical step.

---

### The 13 Operators
The full operator alphabet:

- **Fixation** — Lock current state; stop the leak.
- **Inversion** — Reverse the direction of the route.
- **Break** — Hard termination of a non-working line.
- **Hold** — Temporary suspension; preserves optionality.
- **Pump** — Inject more resource into a viable node.
- **Transfer** — Redistribute load to another carrier.
- **Closure** — Full completion; remove residual tail.
- **Boundary** — Establish admissibility frame.
- **Cleanup** — Remove noise, hooks, false meanings.
- **Reframe** — Change class label without changing facts.
- **Compression** — Reduce overload to minimal working form.
- **Separation** — Split incorrectly fused nodes.
- **Return** — Bring an externalized function back home.

Full definitions in [`spec/operator_alphabet.json`](./spec/operator_alphabet.json).

---

### Domain
**Short:** The life-area where the situation is occurring.

**Technical:** 12 typed domains: Relationships, Work, Finance, Body/Health, Home/Routine, Social Environment, Status/Recognition, Inner State, Self-Model, Projects/Creativity, Legal/Formal, Time/Resource.

---

### Node
**Short:** The actual thing hanging in the situation.

**Technical:** Free-form within a typed structure. Can be a state node (fear, shame, deficit), process node (debt, boundary, obligation), or route node (dead-end, fork, false closure).

---

### Status
**Short:** The current condition of the node.

**Technical:** 16 statuses: Open, Active, Leaking, Frozen, Looping, Escalating, Split, Misclassified, Overloaded, Bound, Pending, Closed, Resolved, Fixed, Dropped, Reopened. Multiple statuses can apply simultaneously (e.g. Open + Leaking).

---

### Persistent Fault Candidate (PFC)
**Short:** A node that has been Open or Leaking for 3+ consecutive audit cycles.

**Technical:** Triggers automatic flagging that the current operator approach is not closing the node. Recommends operator change rather than continued attempts with the same operator.

**Not to be confused with:** "Hard problem" — PFC is a mechanical detection rule based on audit history, not an unsolvable mystery.

---

### Anti-Noise Rule
**Short:** A new state, subclass, or transition is allowed only if it changes diagnosis, operator selection, risk estimate, or route forecast.

**Technical:** Prevents state-space inflation. New micro-states that don't change anything functional are rejected as noise, not promoted to first-class states.

**Example:** A proposed state "SemiOpenHalfLeak" that behaves identically to [Open][Leaking] in all functional respects is rejected.

---

### Looking-Glass Mode
**Short:** Reverse-read mode. Outcome → plausible prior paths → split point → repair.

**Technical:** Diagnostic extension. Operators: ReverseTrace, SplitPoint, DamageAttribution, RepairVector. Anti-magic-guard prevents claims of literal undo-history. Full doc: [`04_extensions/looking_glass.md`](./04_extensions/looking_glass.md).

**Not to be confused with:** Time travel, reversal of entropy, or undoing the past. Looking-Glass is a *reading* mode, not a *causation* mode.

---

### ReverseTrace
**Short:** Reconstruction of likely path from current state backward toward likely cause.

**Technical:** Probabilistic, bounded. Output is a hypothesis, not certified history.

---

### SplitPoint
**Short:** The likely critical transition where the route went costly or wrong.

**Technical:** Diagnostic candidate, not certified history. Multiple split points may be plausible; CAP picks the most actionable one.

---

### Adjustment Dynamics
**Short:** The forward-routing engine.

**Technical:** Takes current state and produces a reweighted distribution of admissible future paths. Two modes (Desire Pressure, Problem Pressure). Two bridge modes (Markov, Schrödinger). Subsystems: BudgetGate, LeakageScreen, AntiCollapseGuard, LookingGlassChain. Doc: [`02_subsystems/adjustment_dynamics.md`](./02_subsystems/adjustment_dynamics.md).

---

### Markov Bridge
**Short:** Find admissible intermediate states between current and target without impossible jumps.

**Technical:** Path-construction mode bounded by transition validity constraints.

---

### Schrödinger Bridge
**Short:** Minimally deform the prior path distribution to satisfy new constraints.

**Technical:** Distribution-reweighting mode. Preserves prior dynamics as much as possible.

---

### Desire Pressure
**Short:** Input mode where the system receives a goal state and searches for admissible forward routes without delivery guarantee.

---

### Problem Pressure
**Short:** Input mode where the system receives a damaged or deficit state and routes toward stabilization without collapsing into advice.

---

### Latent Cause Reconstruction (A-Reconstruction)
**Short:** Inverse-causal engine. From observed rupture B + traces → ranked latent cause candidates A → repair pairs C.

**Technical:** Trigger ≠ cause. Visible event T may be the trigger, but latent A is the actual cause. Repair must address A (cause-first), not just close B (symptom-only).

**Not to be confused with:** Single-cause attribution. A-Reconstruction always returns a *ranked distribution* of causes with counterfactual tests.

---

### Trigger vs Cause
**Short:** The visible event that activated a rupture is not necessarily its cause.

**Example:** An emergency database recovery invoice triggers a budget overrun. The latent cause may be contingency-buffer depletion from prior non-critical prototype work. Paying the invoice without repairing the buffer policy is symptom-only repair.

---

### Anti-Self-Justification Loop
**Short:** Failure mode where an LLM defends its own previous output even when evidence weakens it.

**Technical:** "Previous generation is not evidence." Every previous output must be re-evaluated by its telemetry (RC, E, CS, V, source validity, user feedback), not preserved by default. See [`examples/anti_self_justification_loop.md`](./examples/anti_self_justification_loop.md).

---

### Memory Dreaming
**Short:** Offline memory recompilation under CAP release gates.

**Technical:** Reads canonical memory, transcripts, retrieval traces, artifact refs, and COM telemetry; writes only candidate memory store, memory diff, review items, rejected items, and Dream telemetry. Canonical memory changes only after verifier and approval gates. See [`04_extensions/memory_dreaming/framework.md`](./04_extensions/memory_dreaming/framework.md).

**Not to be confused with:** Fine-tuning, RAG retrieval, or automatic memory overwrite. Dreaming proposes memory; it does not canonicalize memory.

---

### Dream Compiler
**Short:** The component that produces candidate memory diffs from raw memory evidence.

**Technical:** The compiler pass that detects duplicates, stale anchors, contradictions, weak provenance, and contamination, then emits explicit diff operations such as `reconcile`, `retcon`, `quarantine`, or `rollback`.

---

### Memory Diff
**Short:** An explicit ledger operation over memory state.

**Technical:** A reviewable operation with `op`, target/proposed IDs, reason, provenance, evidence level, claim strength, contradiction risk, transition cost, and validator outcome. Every memory mutation must be explainable as a diff.

---

### Reconcile
**Short:** Merge compatible memory nodes without rewriting history.

**Technical:** Preferred Dream operation when nodes duplicate or complement each other. It de-duplicates and strengthens provenance while preserving the evidence chain.

---

### Retcon
**Short:** Repair a wrong interpretation while preserving the old state.

**Technical:** Marks the old anchor as superseded and proposes a replacement anchor. It is not a silent edit: the prior state remains auditable and the replacement still requires approval.

---

### Rollback
**Short:** Reject an unsafe candidate diff or restore the last approved memory snapshot.

**Technical:** Safety boundary for contaminated Dream outputs, unrelated merges, weak-evidence canonicalization, deleted contradictions, or collapsed branch states. Candidate memory cannot damage canonical memory.

---

### Zero-Sycophancy
**Short:** The system flatters neither the user nor its own past outputs.

**Two sides:**
1. Don't flatter the user (no agreement-seeking responses).
2. Don't defend the model's own weak past outputs.

---

### Budget Recovery Protocol
**Short:** What activates when Telemetry = Breach.

**Technical:** New high-risk chains forbidden. Active chains downgraded or held. Only low-risk stabilizers (Fixation, Hold, Cleanup) permitted. Domain actions above 50% RiskWeight frozen.

---

### CAP-Guardrails / Anti-Freeze Layer
**Short:** Cross-cutting meta-layer that stops CAP from freezing on its own audit.

**Technical:** Detects five inaction risks (`analytical_paralysis`, `budget_underestimation`, `frozen_container`, `fast_mode_abuse`, `escalation_avoidance`) and issues routing directives exclusively — it never alters anchors, commits, or releases. Governs Fast Mode entry, the RealityFloor check on soft budget claims, and the NO_MAP_NO_WORK scout/seal surface. See [`02_subsystems/cap_guardrails.md`](./02_subsystems/cap_guardrails.md) and [`spec/cap_guardrails.schema.json`](./spec/cap_guardrails.schema.json).

**Not to be confused with:** Budget Recovery Protocol, which reacts to a telemetry breach — Guardrails defends against foolish *inaction*, not foolish action.

---

### Anchor (in CAP sense)
**Short:** A claim, output, or commitment that is preserved as a stable reference point.

**Technical:** A previous output is *not* automatically an anchor. It becomes an anchor only if it passed validation with sufficient confidence. Anchors can be revoked by self-audit.

**Not to be confused with:** Anchor in Shard Theory main spec (which has a specific architectural meaning) — the CAP usage is narrower.

---

### Identity-Verified Validation
**Short:** Validation runs verify that the LLM's `model` field matches the requested model.

**Technical:** Before each model run, `/v1/models` is queried to confirm the requested model is available. Responses with mismatched `model` field are rejected. This prevents config-mislabeled results from polluting the validation surface.

---

### Research-Only
**Short:** The framework is a working surface for analysis, not certified canon.

**Technical:** Validation supports machine-checkability of boundaries and consistency across inference surfaces. It does not constitute empirical truth claims about lived experience or guarantee real-world outcomes. See [`03_validation/falsifiability.md`](./03_validation/falsifiability.md).

---

### AICE (AI Chaos Engineering)
**Short:** A draft, unofficial incident taxonomy for agentic workflows where the narrative claims completion but the physical evidence is absent.

**Technical:** The AICE 6xx codes (`AICE-604`…`AICE-609`) classify evidence-boundary failures — declared-but-unmaterialized artifacts, releases without implementation deltas, PASS without a test run, deployment without observed production state, verification without independence, consensus without evidence. An unresolved AICE incident holds workflow state (`STATE_UNCHANGED`). AICE is a CAP application, not a core phenomenological claim. See [`AICE.md`](./AICE.md) and [`spec/aice/README.md`](./spec/aice/README.md).

**Not to be confused with:** HTTP status codes or an IETF standard — the `HTTP 6xx` labels are humorous human-readable aliases only, and AICE claims no standards-body recognition or external adoption.

**Example:** An agent reports `artefact.json` was written and quotes a SHA-256, but no path, write event, or readable bytes can be found. That is `AICE-604`.

---

### Observable Event
**Short:** A change in the world that leaves independently checkable evidence.

**Technical:** In AICE, an event that can be confirmed through a write/persist receipt, a tool/process exit record, a readback, an externally observed state change, or an equivalent trustworthy signal — as opposed to a mere assertion that it happened.

**Not to be confused with:** A narrative statement — text saying an event occurred is not itself an event.

**Example:** A recorded file-write with a subsequent `stat`/readback is an observable event; a report sentence claiming the file exists is not.

---

### Postcondition
**Short:** The state that must actually hold after an action for it to count as done.

**Technical:** In AICE, the required physical state a claim depends on (bytes on disk, a target revision live, an exit status of a real run). Workflow state may advance only when the postcondition is verified; otherwise an AICE incident holds the transition.

**Not to be confused with:** A precondition (what must hold before) or a claimed outcome (what a narrative says resulted).

**Example:** For "deployment succeeded", the postcondition is the target environment observably at the expected revision — not the deploy command returning without a printed error.

---

### Narrative State
**Short:** What an agent, verifier, orchestrator, report, or model *claims* occurred.

**Technical:** In AICE, the asserted status of a unit of work — `COMPLETE`, `PARTIAL`, or `ABSENT`. Narrative state is an input to be checked against physical state, never a substitute for it, and model prose in narrative state must not directly mutate workflow state.

**Not to be confused with:** Physical state — the two are compared precisely because they can diverge.

**Example:** "All tests pass" is a narrative state of `COMPLETE`; without an execution receipt its physical state is `UNOBSERVED` (`AICE-606`).

---

### Physical State
**Short:** What observation of the required postcondition actually supports.

**Technical:** In AICE, one of `OBSERVED`, `UNOBSERVED`, `CONTRADICTED`, or `NOT_APPLICABLE`, established from events, readable artifacts, receipts, or state inspection. When physical state does not corroborate a `COMPLETE` narrative, an AICE incident is emitted and workflow state is held.

**Not to be confused with:** Narrative state — physical state is what evidence shows, not what was claimed.

**Example:** After a push is reported, `git ls-remote` showing the remote ref still at the old commit makes the publication's physical state `CONTRADICTED`/`UNOBSERVED` (`AICE-607`).

---

### Metaphysical Artifact
**Short:** A declared artifact that has a name and even a hash, but no materialized bytes.

**Technical:** The `AICE-604` pattern (symbolic code `ARTEFACT_METAPHYSICAL`): an artifact is asserted, optionally with filename, path, size, or digest, yet no confirmed path, write event, readback, or digest recomputed from observed bytes exists. The digest is a claim about reality, not reality; acceptance is blocked until the bytes are materialized.

**Not to be confused with:** A legitimately produced artifact whose write event merely wasn't logged but which can still be independently located and read — that is not an AICE-604.

**Example:** A report lists `artefact.json` with a 64-character SHA-256, but a repository search finds no such file. The "artifact" is metaphysical.
