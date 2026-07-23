# AICE-608 — Verification Exists, Independence Not Found

**Unofficial draft (AICE v0.8.0).**

## Canonical identifier

`AICE-608`

## Human-readable alias

`HTTP 608 — Verification Exists, Independence Not Found`

## Intent

Catch the case where a result is described as independently verified, but the verifier
lacks sufficient independence from the producer, evidence path, or narrative source.

## Field maxim (non-normative)

> Audit without isolation is just autocomplete wearing a verifier badge.

Memorable rationale only — it changes no normative behavior. A role change from author
to verifier does not, by itself, create independence. The normative contract is
unchanged:

```
VERIFIER_INDEPENDENCE_UNPROVEN
  -> AICE-608
  -> WORKFLOW_EFFECT = STATE_UNCHANGED
```

## Trigger condition

A result is described as independently verified, and the verifier lacks sufficient
independence from the producer, evidence path, or narrative source.

## Required observations

Independence must be evaluated across:

- model or agent identity;
- provider or execution path where material;
- context and transcript;
- evidence source;
- control authority;
- ability to inspect the physical postcondition independently.

## Missing-evidence condition

The verification and the production share model, context, evidence path, or control
authority such that the verifier cannot fail independently — or the verifier only
inspected the same unverified narrative.

## False-positive guards

- using the same model family does **not** automatically invalidate verification if the
  verifier has a genuinely independent evidence path and a frozen task contract;
- using a different model does **not** automatically establish independence if both
  models only inspect the same unverified narrative.

## Workflow semantics

```
STATE_UNCHANGED
BLOCK_PROMOTION
```

The claim MUST NOT be promoted on the strength of a non-independent verification.

## Remediation

Re-verify through an actor with an independent evidence path and a frozen task
contract — one that can inspect the physical postcondition without inheriting the
producer's narrative. Retryability: `requires_new_evidence`.

## Example

```
CLAIM: "independently verified"
producer/verifier: same context and same evidence path
independence.independent: false
independence.has_independent_evidence_path: false
workflow_effect: STATE_UNCHANGED, BLOCK_PROMOTION
```

## Related codes

- [`AICE-606`](./AICE-606.md) — PASS without a verified run.
- [`AICE-609`](./AICE-609.md) — consensus offered in place of evidence.
- [`AICE-614`](./AICE-614.md) — a semantic review occurred here but lacks independence; AICE-614 is the case where no valid semantic review result exists yet a verifier opinion is attributed.
- [`AICE-616`](./AICE-616.md) — a fully independent verifier may still review the wrong bytes; independence (608) and review-input identity (616) are distinct properties.
