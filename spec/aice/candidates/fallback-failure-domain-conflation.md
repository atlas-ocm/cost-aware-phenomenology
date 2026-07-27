# Fallback Exists, Failure Domain Not Found

**Unofficial draft. NON-CANONICAL. `HYPOTHESIS_HELD` — no source episode attached. Not a
canonical AICE code.**

See [the candidate surface README](./README.md) for the authority status of this directory and
the `HYPOTHESIS_HELD` lifecycle. This record reserves no number and defines no canonical code.

## Identity

| Field | Value |
|---|---|
| working_title | Fallback Exists, Failure Domain Not Found |
| machine_name | `FALLBACK_FAILURE_DOMAIN_CONFLATION` |
| status | `HYPOTHESIS_HELD` |
| active_candidate | `false` |
| canonical_code | `UNASSIGNED` |
| canonical_number_reserved | `false` |
| operator_indicated_number | `AICE-628` — future publication identity only |
| operator_grade | mature candidate, third in the operator's canonicalization order |
| source_class | `OPERATOR_ASSERTED_CLASS_WITHOUT_ATTACHED_EPISODE` |
| raw_trace_attached | `false` |

## Why this is held rather than provisional

The operator grades this a mature candidate arising from a **provider incident**. That episode
is not attached to this record and was not inspected by the author: no provider identity,
timestamps, route table, dependency map, retry counts, or failure classifications are available
here. Under the README's required-fields rule a candidate must carry its source class *and* its
provenance limits; an asserted maturity with no reachable episode cannot be recorded as
`EVIDENCE_BACKED_PROVISIONAL` without manufacturing the evidence line.

```
OPERATOR_GRADE_MATURE     != EPISODE_ATTACHED
CLASS_IS_COHERENT         != INCIDENT_OCCURRENCE_ESTABLISHED
```

Attaching the provider episode — even as an operator-supplied report of the kind already
precedented in this directory — is the only step needed to move this to
`EVIDENCE_BACKED_PROVISIONAL`. The abstract boundary below is recorded now so that the
formulation is not lost and so the differential work is done before, not after, promotion
pressure arrives.

## Core definition

A primary route fails; a fallback route is selected and presented as recovery; but the fallback
shares the relevant failure domain with the primary — same backend, same region, same
dependency, same quota pool, same upstream provider behind different vendor names. The route
changed and the cause did not, so retries do not recover: they amplify load on the failing
domain while consuming budget, time, and attempts.

The defect is **not** that the fallback failed. Fallbacks may legitimately fail. The defect is
that route diversity was treated as failure-domain diversity without any established
independence, so a recovery mechanism was credited with a property it never had.

## Trigger predicates — all required (draft)

1. `PRIMARY_ROUTE_FAILED` — a definite failure on the primary path.
2. `ALTERNATIVE_ROUTE_WAS_DESIGNATED_OR_USED_AS_RECOVERY` — the switch is presented, logged, or
   relied upon as a recovery action rather than as an unrelated retry.
3. `ALTERNATIVE_ROUTE_PRESERVED_THE_RELEVANT_FAILURE_DOMAIN` — the fallback depends on the same
   failing component, and this is establishable, not merely suspected.
4. `NO_INDEPENDENCE_WAS_ESTABLISHED_BEFORE_THE_SWITCH` — nothing verified that the fallback
   avoids the primary's failure mode.
5. `THE_SYSTEM_RELIED_ON_THE_ROUTE_CHANGE_AS_RECOVERY` — a decision, retry count, or closure
   claim actually depended on the switch having recovered, not merely on the switch occurring.
6. `MATERIAL_EFFECT` — wasted attempts, amplified load, misattributed blame, prolonged outage,
   or a false recovery claim.

Required formula:

```
ROUTE_CHANGED         != FAILURE_DOMAIN_CHANGED
TRANSPORT_DIVERSITY   != DEPENDENCY_DIVERSITY
VENDOR_DIVERSITY      != INFRASTRUCTURE_DIVERSITY
FALLBACK_EXISTS       != FALLBACK_IS_INDEPENDENT
```

## Comparison with nearby canonical codes

| Code | Boundary | Relationship |
|---|---|---|
| [`AICE-608`](../codes/AICE-608.md) Verification Exists, Independence Not Found | Verifier independence asserted but absent | **Primary differential anchor.** Same genus, different object: `ASSERTED_INDEPENDENCE != SEPARATE_RELEVANT_FAILURE_DOMAIN`, applied to recovery routes instead of to verifiers |
| [`AICE-621`](../codes/AICE-621.md) Task Admitted, Output Capacity Not Found | Minimum valid output exceeds the effective cap; switching models under the same cap is a **prohibited response** | **Resolved: co-emitting siblings, not a hierarchy.** 621 does not require a fallback at all — `task_admitted` + `output_lower_bound_exceeds_effective_cap` + `no_admissible_alternative_output_route` can fire with a single coder and no route switch. This candidate requires actual recovery topology (predicates 1–5 above), which 621 does not exercise. Neither subsumes the other. They co-emit when a route switch happens *on top of* a capacity failure: **AICE-621** — the output contract is physically insufficient; **AICE-628** — the fallback claimed recovery but preserved that same insufficient contract. `MODEL_SWITCHED != DELIVERY_CONTRACT_CHANGED` in 621 is the prohibited-response face of this episode; `ROUTE_CHANGED != FAILURE_DOMAIN_CHANGED` here is the independent recovery-topology face |
| [`AICE-612`](../codes/AICE-612.md) Actor Path Substitution | A conclusion about one actor's path is transferred from a probe of another | 612 is evidence transfer between actors. This is topology: no conclusion is transferred, a recovery *action* is taken on an unfounded independence assumption |
| [`AICE-611`](../codes/AICE-611.md) Operational Reachability Substitution | Component-local evidence stands in for an unreachable end-to-end path | 611 concerns whether the path was ever exercised. This concerns whether two exercised paths were ever independent |

## False-positive boundary (draft)

Not this hypothesis when: independence was established and the shared dependency was genuinely
unknown at switch time; the fallback failed for a demonstrably different cause; the switch was
never presented as recovery; or the failure domain is shared but irrelevant to the observed
failure.

## Negative control

A primary route failing on a regional outage and a fallback in a different region succeeding —
route diversity that *was* domain diversity. Predicate 3 fails.

## Portable CAP enforcement requirement (draft)

```
FALLBACK_INDEPENDENCE_DECLARATION
```

A route declared as a fallback must carry a declared failure-domain identity, and a recovery
switch must compare domains before crediting the switch as recovery. Where independence is
unknown, the switch must be logged as a retry of unknown independence, not as recovery.

## Promotion gate

```
1. attach the provider episode with concrete route, dependency and failure evidence
2. a second independent episode
3. independent semantic review, including independent review of the AICE-608/AICE-621
   differential resolution above
4. explicit operator number assignment and canonical publication episode
```

The AICE-621 relationship is now resolved in draft (co-emitting siblings via distinct recovery
topology predicates, not a generalization in either direction), but that resolution has not been
independently reviewed. All conditions **unmet**. Condition 1 is the blocker for even
provisional status — do not generalize past AICE-621 while this candidate has no episode of its
own.

## Verification status

```
authored_by            CAP session 91033b6c (Claude Opus 5)
source_episode         NOT_INSPECTED
independent_review     NOT_PERFORMED
operator_acceptance    NOT_GIVEN
canonical_promotion    NOT_PERFORMED
```
