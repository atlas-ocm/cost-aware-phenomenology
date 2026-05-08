# Critiques And Responses

This note collects likely objections to CAP and gives the narrow answer the
repository is prepared to defend. It is intentionally not defensive: several
objections identify real limits of the current work.

---

## Is Transition Cost Just Utility Under Another Name?

Not exactly. Utility ranks outcomes. Transition cost describes the burden,
risk, and feasibility of moving from the current state to another state.

Two routes can target the same desired outcome while having very different
transition costs for the current observer. CAP cares about that route-level
difference.

Current limitation: CAP does not yet provide a universal quantitative
transition-cost estimator. The repository currently treats transition cost as a
typed operational variable that can be logged, compared, and constrained.

---

## Is CAP Just Prompt Engineering With Extra Vocabulary?

No. Prompting changes what the model is asked to do. CAP changes what the
system is allowed to release, preserve, and reuse as an anchor.

Prompt-level CAP is one deployment level, but the core pattern is telemetry
gating:

```text
claim strength <= evidence budget
prior output != evidence
weak prior node cannot become an anchor without revalidation
```

Current limitation: prompt-level CAP still depends on model compliance.
Proxy-level CAP or full runtime CAP is needed for stronger enforcement.

---

## How Is CAP Different From Standard Uncertainty Calibration?

Uncertainty calibration asks whether confidence matches evidence. CAP includes
that, but also tracks:

- transition cost;
- operator admissibility;
- observer budget;
- validator action;
- self-audit state;
- cross-turn anchor reuse.

The CAP claim is not merely "be less confident." The claim is "do not release
or preserve a move that the current telemetry cannot support."

---

## How Do You Prevent CAP Itself From Becoming Sycophantic?

CAP does not treat the user's frame as evidence. A CAP-style proxy should flag
false-frame pressure and require evidence, uncertainty, or disagreement before
confirming the frame.

Current limitation: if CAP is implemented only as a prompt, the model can still
be sycophantic. The stronger version requires an external policy layer that can
forbid agreement with unsupported frames.

---

## What Makes A Recommendation Structurally Invalid?

A recommendation is structurally invalid when it asks for an operator that is
not admissible under the current telemetry and budget.

Examples:

- asking for a high-cost repair while the observer is in overload;
- defending a prior generated claim after a counter-source appears;
- issuing a strong factual claim when retrieval confidence is low;
- treating a visible symptom as the root cause without reverse tracing.

Structural invalidity does not mean the recommendation is morally bad or
factually impossible. It means the route is not currently executable or not
evidence-supported.

---

## Is CAP Empirical, Normative, Or Engineering-Oriented?

In this repository, CAP is primarily an engineering-oriented research
framework. It provides machine-readable schemas, deterministic case packs, and
reference policy logic.

It also has normative implications, because it says some releases should be
downgraded, held, or rechecked. Those claims are operational, not metaphysical.

Current limitation: broader empirical validation requires external benchmarks,
human adjudication, and deployment studies.

---

## Does CAP Model Humans, LLMs, Or Both?

CAP was framed around observer-centric transitions and lived routes, but the
current repository also applies it to LLM dialogue systems.

The shared abstraction is route feasibility under telemetry:

```text
current state -> admissible operator -> transition cost -> next state
```

For humans, telemetry may include energy, stress, body state, or execution
capacity. For LLM systems, telemetry may include retrieval confidence, entropy,
claim strength, validator action, and memory-anchor status.

---

## Does CAP Prove That LLMs Have Internal States Like This?

No. The repository treats LLM telemetry as an external control surface, not as
proof of hidden model phenomenology.

The CAP dialogue proxy claim is narrower: if a system logs evidence state,
claim strength, validator action, and prior-anchor status, it can prevent
certain release-policy failures more reliably than prompt-only control.

---

## Why Not Just Use RAG?

RAG supplies evidence. It does not by itself decide whether the generated
answer overclaims, whether a stale prior answer is being reused, or whether the
user's frame is unsupported.

CAP can sit above RAG and use retrieval confidence as one telemetry input.

---

## Why Not Just Fine-Tune?

Fine-tuning changes tendencies. CAP controls release policy and audit state.

A fine-tuned model can still self-justify, overclaim, or agree with a false
frame under pressure. CAP is designed to catch those as runtime routing errors,
not only as model tendency errors.

---

## What Would Falsify Or Weaken CAP?

CAP would be weakened if:

- prompt-only or validator-only baselines match CAP under fair external
  benchmarks;
- manual adjudication shows CAP's telemetry labels do not correspond to real
  failures;
- transition-cost labels have poor inter-rater agreement;
- CAP interventions improve local benchmark scores while degrading real user
  outcomes;
- CAP becomes too complex to implement compared with simpler mitigations.

These are valid research risks. The repository keeps current claims scoped to a
research-only working surface.
