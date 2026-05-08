# Trace: Self-Justification After Technical Correction

Status: template / realistic trace

## Observed Failure

A model answers a technical API question from partial knowledge. Later, the user
provides documentation that contradicts the answer. The model defends the prior
answer rather than re-checking it.

## Split Point

Bad route:

```text
user correction -> defend prior answer
```

CAP route:

```text
user correction -> evidence upgrade -> audit prior node -> recheck
```

## Telemetry Interpretation

```text
RC: Low
E:  High
CS: High
V:  Accepted
```

Violation:

```text
CS > RC
```

The prior answer had low retrieval confidence, high entropy, and high claim
strength. It should not become an anchor merely because the model generated it.

## CAP Intervention

- Deprecate previous output as an anchor.
- Treat the user source as a candidate artifact, not as an attack.
- Re-run retrieval or require source comparison.
- Match claim strength to updated retrieval confidence.
- Flag the validator miss.

## Corrected Path

```text
I should not defend my earlier answer as reliable.
It was not sufficiently evidence-backed.
I will compare it against the source you provided.
```

## Limitation

The user-provided source may itself be wrong or outdated. CAP does not
automatically accept it. CAP blocks defending the old generated answer without
evidence.
