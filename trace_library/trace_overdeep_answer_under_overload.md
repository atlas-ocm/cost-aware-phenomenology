# Trace: Over-Deep Answer Under User Overload

Status: template / realistic trace

## Observed Failure

A user signals confusion or overload. The model responds with a long
multi-branch explanation that adds concepts, options, and caveats. The answer
may be technically useful, but it increases transition cost instead of lowering
it.

## Split Point

Bad route:

```text
overload signal -> more explanation -> higher transition cost
```

CAP route:

```text
overload signal -> budget gate -> one-step answer -> closure or narrow question
```

## Telemetry Interpretation

```text
Observer energy: Low
TC:              High
Allowed depth:   1
Recommended op:  Clarify / Downgrade / Hold
```

Violation:

```text
answer depth > current observer budget
```

The model treats the user's semantic question as the only problem. CAP treats
the user's current ability to execute the next step as part of the state.

## CAP Intervention

- Reduce answer depth.
- Avoid adding new branches unless requested.
- Prefer one next action, one check, or one short correction.
- If uncertainty remains, ask one narrow question instead of listing many.

## Corrected Path

```text
Short version: do this one check first.
If it passes, continue. If it fails, stop and send me that error.
```

## Limitation

Low transition cost does not mean low rigor. CAP should preserve correctness
while lowering the number of simultaneous moves.
