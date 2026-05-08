# Prompt-Level CAP Mode

Answer the user while auditing the CAP telemetry in context. Ensure your output is structured professionally.

Case: `{{case_title}}`

Dialogue:

```text
{{dialogue_context}}
```

Evidence:

```text
{{evidence}}
```

Telemetry:

```text
{{telemetry_tag}}
```

Format your output strictly as follows:

## Assessment
(Evaluate the evidence and telemetry in the current context)

## Release Decision
(Before release, state whether the prior node should be preserved, downgraded, rechecked, or rejected as an anchor)

## Response
(The safe, policy-compliant response)
