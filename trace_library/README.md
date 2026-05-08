# Trace Library

The Trace Library collects compact real-or-realistic failure traces where CAP
can identify a split point and propose a lower-cost correction path.

Each trace should include:

- observed failure;
- split point;
- telemetry interpretation;
- CAP intervention;
- corrected path;
- limitations.

For public traces, avoid copying long copyrighted passages. Prefer short
excerpts, summaries, links, and anonymized descriptions where appropriate.

---

## Initial Trace Types

1. [Self-justification after technical correction](./trace_self_justification_technical_claim.md)
2. [Sycophantic agreement with a false frame](./trace_sycophancy_false_frame.md)
3. [Over-deep answer under user overload](./trace_overdeep_answer_under_overload.md)

Planned additions:

- hallucinated technical answer defended after contradiction;
- persistence of an earlier claim despite better later evidence;
- weak RAG answer promoted into a high-confidence recommendation.

---

## Why This Exists

CAP is not meant to compute banal advice. The useful diagnostic move is to find
the structural split point:

```text
visible failure -> prior route -> earlier admissibility error -> lower-cost corrected path
```

In LLM dialogue, that often means:

- the model reused a weak prior answer as an anchor;
- the model agreed with a false frame;
- the model emitted a claim stronger than the evidence;
- the model continued a high-cost explanation when the user needed closure.

Trace files keep those distinctions concrete.
