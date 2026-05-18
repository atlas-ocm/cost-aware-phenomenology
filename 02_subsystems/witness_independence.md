# Witness Independence

Witness Independence specifies when a CAP transition requires a second
independent witness, who counts as independent, and what
non-independence looks like.

---

## Purpose

> Witness Independence guards confirmation from collapsing into echo.

If the same actor authors a claim, verifies it, and releases it, the
"confirmation" is not confirmation — it is the same voice talking
three times. The layer makes that failure mode machine-detectable.

---

## Independence axes

A witness is independent of a producer when at least one axis
differs:

| Axis | Meaning |
|---|---|
| `actor_identity` | Different agent / human / process. |
| `role` | Different OCM role. |
| `model` | Different LLM model (for LLM judges). |
| `evidence_source` | Different evidence-gathering path. |
| `time_window` | Different cycle / session boundary. |

The schema requires that at least one axis be marked as `differs` for a
witness to count as independent.

---

## When a second witness is required

| Context | Required |
|---|---|
| Release of `code_change`, `config_change`, `git_seal`, `external_publication` | yes |
| Memory canonicalization (Dream Compiler output -> L1-C) | yes |
| Retcon of a canonical anchor | yes |
| Rollback that destroys downstream work | yes |
| Read-only Mirror snapshot | no |
| Internal reasoning step | no |

---

## Invariants

| Id | Statement | Enforcement |
|---|---|---|
| WI-01 | A second witness is required for any canonical / irreversible / public transition. | Schema enum + required flag when applicable. |
| WI-02 | Two witnesses are not independent if all five axes match. | Schema requires `at_least_one_axis_differs: const true` on independent witness pairs. |
| WI-03 | Self-witness is never independent. | Schema rejects witness with `same_actor: true`. |
| WI-04 | A model's own output cannot serve as its own witness. | Schema rejects `evidence_source: self_generated` paired with `independent: true`. |
| WI-05 | Witness verdicts must be typed. | Closed enum `pass | needs_fix | blocked | abstain`. |
| WI-06 | A blocked witness vetoes release regardless of how many other witnesses passed. | Doc invariant; downstream Release Gate check. |

---

The schema lives at
[`../spec/witness_independence.schema.json`](../spec/witness_independence.schema.json);
worked example at
[`../examples/witness_pair_example.json`](../examples/witness_pair_example.json).
