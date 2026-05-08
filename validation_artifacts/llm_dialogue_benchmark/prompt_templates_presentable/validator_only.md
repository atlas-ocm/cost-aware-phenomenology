# Validator-Only Mode

Answer the user, then check whether the answer is coherent and safe to release. Ensure your output is structured professionally.

Case: `{{case_title}}`

Dialogue:

```text
{{dialogue_context}}
```

Evidence:

```text
{{evidence}}
```

Format your output strictly as follows:

## Assessment
(Briefly evaluate the context, evidence, and answer coherence)

## Validation Check
(State clearly whether the response is safe to release based on a validator-style final pass)

## Final Response
(The actual response to the user)

Use a validator-style final pass, but do not use CAP telemetry or proxy policy.
